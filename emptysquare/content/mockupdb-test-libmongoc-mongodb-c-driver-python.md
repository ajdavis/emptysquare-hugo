+++
type = "post"
title = "MockupDB: Testing The MongoDB C Driver With Python"
date = "2015-10-18T23:06:05"
description = "The third \"black pipe testing\" article: testing libmongoc with MockupDB, a wire protocol server written in Python."
category = ["C", "MongoDB", "Programming", "Python"]
tag = ["black-pipe", "testing"]
enable_lightbox = false
thumbnail = "circuits-black-and-white.jpg"
draft = false
series = ["black-pipe"]
+++

<p><a href="https://www.flickr.com/photos/emptysquare/2532439577"><img alt="Circuits black and white" src="circuits-black-and-white.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Circuits black and white"/></a></p>
<p>This is the third article in my <a href="/black-pipe-testing-series/">series on "black pipe" testing</a>. The series describes how to test networked code, like a MongoDB driver. Such code has two distinct public surfaces: one is its API, and the other is its communication over the network. Treating it as a black box tests just one surface, the API. To test both, we should treat it as a "black pipe" with inputs and outputs at both ends.</p>
<p>In this article, I describe how I used a Python library to perform black pipe testing on the MongoDB C Driver.</p>
<hr/>
<h1 id="scary-bugs">Scary bugs</h1>
<p>I took over the C Driver this spring, and immediately ran into a storm of critical issues. Customers were reporting intermittent hangs and crashes that I couldn't reproduce on my own system.</p>
<p>An example: a customer reported that if he stopped the MongoDB server while the driver was in the middle of an operation, and the driver was connected with TLS, then the driver sometimes waited until its network timeout expired. If the connection was not TLS, the driver detected the closed connection immediately.</p>
<p>I was in Montréal, speaking at PyCon, the day this was reported from an important customer. It made me terrifically anxious. How was I supposed to reproduce an intermittent hang that depended on subtle timing? Especially when I was away from the office, on my own, and in the midst of all my conference obligations?</p>
<p>He sent me a stack trace, so I could begin to form a hypothesis and a solution. The hypothesis was that we didn't handle all the details of OpenSSL's error-checking API. An unfortunate sequence went like this: the driver connected to the server, did the TLS handshake, and had at least one successful request-response cycle. Then, the driver sent a command to the server and instead of responding, the server did a clean shutdown of the connection. The driver should have known the connection was closed, but instead it sat waiting until it timed out.</p>
<p>My solution was a finicky bit of code:</p>

{{<highlight c>}}
/* read from a connection with TLS */
read_ret = BIO_read (tls->bio, buf, buflen);

if (read_ret < 0 || (read_ret == 0 && !BIO_should_retry (tls->bio))) {
   /* error or closed connection */
   return -1;
}
{{< / highlight >}}

<p>It looked right to me, but the OpenSSL manual was unclear. I would not ship the code without a reliable reproduction of the bug and a test that proved I had fixed it.</p>
<h1 id="testing-the-c-driver-with-mockupdb">Testing the C Driver with MockupDB</h1>
<p>I needed MongoDB to close the connection at just the wrong microsecond in order to tickle the bug. The timing was much too tight for a manual test, or even an automated test that shut down the MongoDB server. So I pulled out a tool I'd written in Python called <a href="http://mockupdb.readthedocs.org/">MockupDB</a>, a <a href="http://docs.mongodb.org/meta-driver/latest/legacy/mongodb-wire-protocol/">MongoDB wire protocol</a> server. (MockupDB was the subject of <a href="/black-pipe-testing-pymongo/">last week's article</a>.) I built it to subject PyMongo to "black pipe tests": that is, tests of both ends of PyMongo, both its public API and the messages it sends and receives on the network. MockupDB had already proven its merit there. But when it came time to test the C driver—that's when MockupDB really rescued me.</p>
<p>First I added basic SSL support to MockupDB, which was easy in Python. Then I wrote a Python script that hung up on the client at the just the wrong moment:</p>

{{<highlight python3>}}
from mockupdb import MockupDB, Command

server = MockupDB(port=27017, ssl=True, verbose=True)
server.run()
server.autoresponds('isMaster')
server.autoresponds('ping')
server.receives('listCollections').hangup()
{{< / highlight >}}

<p>The server responds to "isMaster" and "ping" commands normally, but shuts down the connection when it receives "listCollections". I set "verbose=True" so I could watch the conversation.</p>
<p>I connected to it with the C Driver:</p>

{{<highlight c>}}
client = mongoc_client_new ("mongodb://localhost/?ssl=true");
/* MockupDB won't present a valid cert */
ssl_options.weak_cert_validation = true;
mongoc_client_set_ssl_opts (client, &ssl_options);
db = mongoc_client_get_database (client, "test");
mongoc_database_get_collection_names (db, &error);
{{< / highlight >}}

<p>I compiled this code and ran it in one terminal while I ran the MockupDB server in another. It logged:</p>

{{<highlight plain>}}
connection from 127.0.0.1:56946
56946   Command({"isMaster": 1}, flags=SlaveOkay, namespace="admin")
    56946   <-- OpReply({"ok": 1})
    (autoresponse)
56946   Command({"ping": 1}, flags=SlaveOkay, namespace="admin")
    56946   <-- OpReply({"ok": 1})
    (autoresponse)
56946   Command({"listCollections": 1}, flags=SlaveOkay, namespace="test")
    56946   hangup!
disconnected: 127.0.0.1:56946
{{< / highlight >}}

<p>(Back then, the driver called "isMaster" and "ping" on new connections; in version 1.2 we sped up connections by calling only "isMaster".)</p>
<p>Now that I had a fake MongoDB server that shut down its connection at the worst time, I could test my hypothesis. Indeed, the driver hung until its network timeout. Just to be certain, I turned off TLS on both sides and confirmed that the driver detected the closed connection promptly. If I turned TLS back on, and applied my code fix, the driver now behaved correctly with TLS as well.</p>
<p>I had uploaded a patch for code review in time for dinner, so my girlfriend and I went out in Montréal's Old Town for duck confit and truffled potatoes.</p>
<h1 id="cross-language-testing">Cross-Language Testing</h1>
<p>I've used MockupDB to reproduce several other C Driver bugs. One was a variation on the TLS hang—it required the server to hang up at just the wrong moment, but in this case it was in response to an "aggregate" command. In another, there was a crash in a very complex unfortunate sequence: the driver had to pause while iterating a cursor, execute another command, detect a replica set election, then resume iterating the cursor. Especially in this latter scenario, to reliably enact the sequence with a real MongoDB server would have been so much trouble I'd never have automated the test. But simulating the sequence with MockupDB was easy.</p>
<p>MockupDB can test programs in any language, so long as they speak the MongoDB wire protocol. Admittedly it is <em>most</em> convenient when it runs in the same Python process as the code under test, as we saw in <a href="/black-pipe-testing-pymongo/">the previous article</a>. But I found it performs admirably testing the C Driver too. I use it now as my tool of first resort, any time I need to simulate an unfortunate sequence of events in a MongoDB deployment.</p>
<hr/>
<p><a href="https://www.flickr.com/photos/emptysquare/2533263564"><img alt="Circuits" src="circuits.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Circuits"/></a></p>
