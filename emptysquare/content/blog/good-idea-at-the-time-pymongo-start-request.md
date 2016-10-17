+++
type = "post"
title = "It Seemed Like A Good Idea At The Time: PyMongo's \"start_request\""
date = "2014-11-25T08:22:16"
description = "First in a four-part series about choices we regretted in the design of PyMongo."
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = ["good-idea-at-the-time", "pymongo"]
enable_lightbox = false
thumbnail = "get_last_error@240.png"
draft = false
legacyid = "546dfde45393740969f01c0a"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="road-1.jpg" alt="Road" title="Road" /></p>
<p><em>The road to hell is paved with good intentions.</em></p>
<p>I'll tell you the story of <a href="/blog/good-idea-at-the-time-pymongo/">four regrettable decisions we made when we designed PyMongo</a>, the standard Python driver for MongoDB. Each of these decisions led to years of pain for PyMongo's maintainers, Bernie Hackett and me, and years of confusion for our users. This winter I'm ripping out these regrettable designs in preparation for PyMongo 3.0. As I delete them, I give each a bitter little eulogy.</p>
<p>Today I'll tell the story of the first regrettable decision: "requests".</p>
<div class="toc">
<ul>
<li><a href="#the-beginning">The Beginning</a></li>
<li><a href="#the-invention-of-start_request">The Invention of start_request</a></li>
<li><a href="#the-road-to-hell">The Road to Hell</a><ul>
<li><a href="#the-worst-bug">The worst bug</a></li>
<li><a href="#a-bug-factory">A bug factory</a></li>
<li><a href="#an-attractive-nuisance">An attractive nuisance</a></li>
</ul>
</li>
<li><a href="#redemption">Redemption</a><ul>
<li><a href="#mongoclient">MongoClient</a></li>
<li><a href="#write-commands">Write commands</a></li>
<li><a href="#sharding">Sharding</a></li>
<li><a href="#removing-start_request">Removing start_request</a></li>
</ul>
</li>
<li><a href="#post-mortem">Post-mortem</a></li>
</ul>
</div>
<hr />
<h1 id="the-beginning">The Beginning</h1>
<p>It all began when MongoDB, Inc. was a tiny startup called 10gen. Back in the beginning, Eliot Horowitz and Dwight Merriman were making a hosted application platform, a bit like Google App Engine, but with Javascript as the programming language and a JSON-like database for storage. Customers wouldn't use the database directly. It would be exposed through a clean API.</p>
<p>Under the hood, it had a funny way of reporting errors. First you told the database to modify some data, then you asked it whether the modification had succeeded or not. In the Javascript shell, this looked something like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.collection.insert({_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
<span style="color: #666666">&gt;</span> db.runCommand({getlasterror<span style="color: #666666">:</span> <span style="color: #666666">1</span>})  <span style="color: #408080; font-style: italic">// It worked.</span>
{
    <span style="color: #BA2121">&quot;ok&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
    <span style="color: #BA2121">&quot;err&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">null</span>
}
<span style="color: #666666">&gt;</span> db.collection.insert({_id<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
<span style="color: #666666">&gt;</span> db.runCommand({getlasterror<span style="color: #666666">:</span> <span style="color: #666666">1</span>})
{
    <span style="color: #BA2121">&quot;ok&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span>,
    <span style="color: #BA2121">&quot;err&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;E11000 duplicate key error&quot;</span>
}
</pre></div>


<p>The raw protocol was neatly packaged behind an API that handled error reporting for you. (<a href="http://blog.mongodb.org/post/36666163412/introducing-mongoclient">Eliot describes the history of the protocol in more detail here.</a>)</p>
<p>As 10gen grew, we realized the application platform wasn't going to take off. The real product was the database layer, MongoDB. 10gen decided to toss the application platform and focus on the database. We started writing drivers in several languages, including Python. That was the birth of PyMongo.  Mike Dirolf began writing it in January of 2009.</p>
<p>At the time we thought our database's funky protocol was a feature: if you wanted minimum-latency writes, you could write to the database blind, without stopping to ask about errors. In Python, this looked like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># Obsolete code, don&#39;t use this!</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> Connection
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>c <span style="color: #666666">=</span> Connection()
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection <span style="color: #666666">=</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>Unacknowledged writes didn't care about network latency, so they could saturate the network's throughput:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="no-get_last_error.png" alt="Unacknowledged write" title="Unacknowledged write" /></p>
<p>On the other hand, if you wanted acknowledged writes, you could ask after each operation whether it succeeded:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># Also obsolete code. &quot;safe&quot; means &quot;acknowledged&quot;.</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>}, safe<span style="color: #666666">=</span><span style="color: #008000">True</span>)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>}, safe<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>But you'd pay for the latency:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="get_last_error.png" alt="Get last error" title="Get last error" /></p>
<p>We thought this design was great! You, the user, get to choose whether to await acknowledgment, or "fire and forget." We made our first regrettable decision: we set the default to "fire and forget."</p>
<h1 id="the-invention-of-start_request">The Invention of start_request</h1>
<p>There are a number of problems with the default, unacknowledged setting. The obvious one is, you don't know whether your writes succeeded. But there's a subtler problem, a problem with consistency. After an unacknowledged write, you can't always immediately read what you wrote. Say you had two Python threads executing two functions, doing unacknowledged writes:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">c <span style="color: #666666">=</span> Connection()
collection_one <span style="color: #666666">=</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection_one
collection_two <span style="color: #666666">=</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection_two

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">function_one</span>():
    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">100</span>):
        collection_one<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;fieldname&#39;</span>: i})

    <span style="color: #008000; font-weight: bold">print</span> collection_one<span style="color: #666666">.</span>count()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">function_two</span>():
    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">100</span>):
        collection_two<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;fieldname&#39;</span>: i})

    <span style="color: #008000; font-weight: bold">print</span> collection_two<span style="color: #666666">.</span>count()

threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>function_one)<span style="color: #666666">.</span>start()
threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>function_two)<span style="color: #666666">.</span>start()
</pre></div>


<p>Since there are two threads doing concurrent operations, PyMongo opens two sockets. Sometimes, one thread finishes sending documents on a socket, checks the socket into the connection pool, and checks the <em>other</em> socket out of the pool to execute the "count". If that happens, the server might not finish reading the final inserts from the first socket before it responds to the "count" request on the other socket. Thus the count is less than 100:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="unacknowledged-inserts.png" alt="Unacknowledged inserts" title="Unacknowledged inserts" /></p>
<p>If the driver did acknowledged writes by default, it would await the server's acknowledgment of the inserts before it ran the "count", so there's no consistency problem.</p>
<p>But the default was unacknowledged, so users would get results that surprised them. In January of 2009, PyMongo's original author Mike Dirolf fixed this problem. He wrote a connection pool that simply allocated a socket per thread. As long as a thread always uses the same socket, it doesn't matter if its writes are acknowledged or not: </p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="unacknowledged-inserts-single-socket.png" alt="Unacknowledged inserts single socket" title="Unacknowledged inserts single socket" /></p>
<p>The server doesn't read the "count" request from the socket until it's processed all the inserts, so the count is always correct. (Assuming the inserts succeeded.) Problem solved!</p>
<p>Whenever a new thread started talking to MongoDB, PyMongo opened a new socket for it. When the thread died, its socket was closed. 
Mike's solution was simple and did what users expected. And thus began PyMongo's five-year trudge down the road to hell.</p>
<!---
begin: always socket per thread
mike Wed Feb 11 17:50:27 2009 auto_start_request introduced, default True, start_request and end_request added
mike January 7, 2010 auto_start_request always on
bernie April 12, 2011 at 3:03:57 PM EDT remove auto_start_request
me March 10, 2012 at 9:19:04 PM EST make auto_start_request optional again, introduce reclamation
-->

<hr />
<p>I don't want you to misunderstand me: What Mike did seemed like a good idea at the time. The company had decided that unacknowledged was the default setting for all MongoDB drivers, but Mike still wanted to guarantee read-your-writes consistency if possible. Plus, the Java driver already associated sockets with threads, so Mike wanted the Python driver to act similarly.</p>
<p>I can picture Mike sitting at one of the desks in 10gen's original office. There were only a half-dozen people working for 10gen then, or fewer. This was long before my time. They had a corner of an office shared by Gilt, ShopWiki and Panther Express, in an old gray stone building on 20th Street in Manhattan, next to a library. It would've been very cold that day, maybe snowy. I see Mike sitting next to Eliot, Dwight, and their tiny company. He was banging out a Python driver for MongoDB, making one quick decision after another. Did he know he was setting a course that could not be corrected for five years? Probably not.</p>
<hr />
<p>So Mike had decided that PyMongo would reserve a socket for each thread. But what if a thread talks to MongoDB, and then goes and does something else for a long time? PyMongo reserves a socket for the thread, that no one else can use. So in February, Mike added the "end_request" method to let a thread relinquish its socket. He also added an "auto_start_request" option. It was turned on by default, but you could turn it off if you didn't need it. If you only did acknowledged writes, or if you didn't immediately read your own writes, you could turn off "auto_start_request" and you'd have a more efficient connection pool.</p>
<p>The next year, in January 2010, Mike simplified the pool. In his new code, "auto_start_request" could no longer be turned off. His commit message claimed he made PyMongo "~2x faster for simple benchmarks." He wrote,</p>
<blockquote>
<p>Calling Connection.end_request allows the socket to be returned to the pool, and to be used by other threads instead of creating a new socket. Judicious use of this method is important for applications with many threads or with long running threads that make few calls to PyMongo.</p>
</blockquote>
<p>Bernie Hackett took over PyMongo the year after that, and since "auto_start_request" didn't do anything any more, Bernie removed it entirely in April 2011.</p>
<p>The "judicious use of end_request" tip had been in PyMongo's documentation since the year before, but Bernie suspected that users didn't follow the directions. Just as most people don't recycle their plastic bottles, most developers didn't call "end_request", so good sockets were wasted. Even worse, since threads kept their sockets open and reserved for as long as each thread lived, it was common to see a Python application deployment with thousands and thousands of open connections to MongoDB, even though only a few connections were doing any work.</p>
<p>Therefore, when I came to work for Bernie that November, he directed me to improve PyMongo's connection pool in two ways. First, PyMongo should once again allow you to turn off "auto_start_request". Second, if a thread died without calling "end_request", PyMongo should somehow detect that the thread had died and reclaim its socket for the pool, instead of closing it.</p>
<p>Making "auto_start_request" optional again was easy. If you turned it off, each thread just checked its socket back into the pool whenever it wasn't using it. When the thread next needed a socket, it checked one out, probably a different one. We recommended that PyMongo users do "safe" writes (that is, acknowledged writes), and turn off "auto_start_request". This led to better error reporting and much more efficient connection pooling: sane choices but not, alas, the defaults. We couldn't change the defaults because we had to be backwards-compatible with the regrettable decisions made years earlier.</p>
<p>So restoring "auto_start_request" was a cinch. Detecting that a thread had died, however, was hell.</p>
<h1 id="the-road-to-hell">The Road to Hell</h1>
<p>I wanted to fix PyMongo so it could "reclaim" sockets. If a thread had a socket reserved for it, and it forgot to call "end_request" before it died, PyMongo shouldn't just close the socket. It should check the socket back into the connection pool for some future thread to use. My first solution was to wrap each socket in an object with a <code>__del__</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">SocketInfo</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, pool, sock):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>pool <span style="color: #666666">=</span> pool
        <span style="color: #008000">self</span><span style="color: #666666">.</span>sock <span style="color: #666666">=</span> sock

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__del__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>pool<span style="color: #666666">.</span>return_socket(<span style="color: #008000">self</span><span style="color: #666666">.</span>sock)
</pre></div>


<p>Piece of cake. We released this code in May 2012, and it was much more efficient. Whereas the previous version of PyMongo's pool tended to close and open sockets frequently:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-2-1.png" alt="PyMongo 2.1" title="PyMongo 2.1"/></p>
<p>PyMongo 2.2 reclaimed dead threads' sockets for new threads that wanted them:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-2-2-auto-start-request.png" alt="PyMongo 2.2" title="PyMongo 2.2"/></p>
<p>I was proud of my achievement. Then all hell broke loose.</p>
<h2 id="the-worst-bug">The worst bug</h2>
<p>Right after we released my "socket reclamation" code in PyMongo, a user reported that in Python 2.6 and mod_wsgi 2.8, and with "auto_start_request" turned on (the default), his application leaked a connection once every two requests! Once he'd leaked a few thousand connections he ran out of file descriptors and crashed. It took me 18 days of desperate debugging, with <a href="https://twitter.com/lazlofruvous">Dan Crosta</a> by my side, before I got to the bottom of it. It turns out there are roughly three bugs in Python's threadlocal implementation, which were all fixed when Antoine Pitrou rewrote threadlocals for Python 2.7.1. <a href="http://bugs.python.org/issue1868">One of them was reported</a> and the other two never were.</p>
<p>The unreported bug I'd found was in the C function in the Python interpreter that manages threadlocals. By accessing a threadlocal from a <code>__del__</code> method, I'd caused the function to be called recursively, which it wasn't designed for. This caused a refleak every <em>second</em> time it happened, leaving open sockets that could never be garbage-collected.</p>
<p>This bug in an obsolete version of Python was, in turn, interacting with an obsolete version of mod_wsgi, which cleared each Python thread's state after each HTTP request. So anyone on Python 2.7 or mod_wsgi 3.x, or both, wouldn't hit the bug. But ancient versions of Python and mod_wsgi are widely used.</p>
<p>I <a href="https://jira.mongodb.org/browse/PYTHON-353?focusedCommentId=124033&amp;page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-124033">wrote up my diagnosis of the bug</a>, reimplemented my socket reclamation code to avoid the recursive call, and released the fix. <a href="/blog/pythons-thread-locals-are-weird/">I wrote a frustrated article about how weird Python's threadlocals are</a>, and early the next year <a href="/blog/knowing-when-a-python-thread-has-died/">I wrote a description of my workaround</a>.</p>
<p>To this day, the bug is my worst. It's among the worst for impact, certainly it was the hardest to diagnose, and it remains the most complicated to explain.</p>
<p>That last point&mdash;the bug is hard to explain&mdash;has real costs. It makes it very hard for anyone but me to maintain PyMongo's connection pool. Anyone else who touches it risks recreating the bug. Of course, we test for the bug after every commit: we loadtest PyMongo with Apache and mod_wsgi in our Jenkins server to guard against a regression of this bug. But no outside contributor is likely to go to such effort, nor to understand why it is necessary.</p>
<h2 id="a-bug-factory">A bug factory</h2>
<p>A full year later, in April 2013, I discovered <a href="https://jira.mongodb.org/browse/PYTHON-509">another connection leak</a>. Unlike the 2012 bug, this leak was rare and hard to reproduce. I don't think anyone was hurt by it. I was a much better diagnostician by now, and I knew the relevant part of CPython all too well. It took me less than a day to determine that in Python 2.6, <a href="/blog/another-thing-about-pythons-threadlocals/"><em>assigning</em> to a threadlocal is not thread safe</a>. I added a lock around the assignment and released yet another bugfix for "start_request" in PyMongo.</p>
<p>For my whole career at MongoDB, I've regularly found and fixed bugs in "start_request". In 2012 I found that if one thread calls "start_request", <a href="https://jira.mongodb.org/browse/PYTHON-428">other threads can sometimes think, wrongly, that they're in a request, too</a>. And when a replica set primary steps down, <a href="https://jira.mongodb.org/browse/PYTHON-345">threads in requests all threw an exception before reconnecting</a>.</p>
<p>In 2013 a contributor Justin Patrin tried to add a feature to our connection pool, but what should have been a straightforward patch got fouled by the barbed wire in "start_request". In his code, if a thread in a request <a href="https://jira.mongodb.org/browse/PYTHON-537">got a network error it leaked a semaphore</a>. And just last month I had to fix a <a href="/blog/a-normal-accident-in-python-and-mod-wsgi/">little bug in the connection pool</a> related to "start_request" and mod_wsgi.</p>
<h2 id="an-attractive-nuisance">An attractive nuisance</h2>
<p>There's another thing about "start_request" that's almost as bad as its complexity: its name. It's an attractive nuisance. It sounds like, "I have to call this before I start a request to MongoDB." I frequently see developers who are new to PyMongo write code like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Don&#39;t do this.</span>
c<span style="color: #666666">.</span>start_request()
doc <span style="color: #666666">=</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find_one()
c<span style="color: #666666">.</span>end_request()
</pre></div>


<p>This is completely pointless, a waste of the programmer's effort and the machine's. But the name is so vague, and the explanation is so complex, you'd be forgiven for thinking this is how you're supposed to use PyMongo.</p>
<p>Now, I ask you, which decision was the most regrettable? Was socket reclamation a bad feature&mdash;should we have let PyMongo continue closing threads' sockets when threads died, instead of building a Rube Goldberg device to check those sockets back into the pool? Or maybe a worse idea came years before, when Mike turned on "auto_start_request" by default&mdash;maybe everything would have been okay if he'd required users to call "start_request" explicitly, instead. Maybe he shouldn't have implemented "start_request" at all. Most likely, the root cause was the decision we made before Mike even started writing PyMongo: the decision to make unacknowledged writes the default.</p>
<h1 id="redemption">Redemption</h1>
<h2 id="mongoclient">MongoClient</h2>
<p>Late in 2012, while I was in the midst of all these "start_request" bugs, Eliot had an idea that turned us around, and showed us the way back from hell. He figured out a way redeem our original sin, the sin of making unacknowledged writes the default. See, we had long recommended that users override PyMongo's defaults, like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Obsolete.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> c <span style="color: #666666">=</span> Connection(safe<span style="color: #666666">=</span><span style="color: #008000">True</span>, auto_start_request<span style="color: #666666">=</span><span style="color: #008000">False</span>)
</pre></div>


<p>...but we couldn't make this the new default because it would break backwards compatibility. Eliot decided that all the drivers should introduce a new class with the proper defaults. Scott Hernandez came up with a good name for the class, one that no driver used yet: "MongoClient".</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Modern code.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> c <span style="color: #666666">=</span> MongoClient()
</pre></div>


<p>While we were at it, we deprecated the old "safe / unsafe" terms and <a href="/blog/pymongos-new-default-safe-writes/">introduced a new terminology, "write concern"</a>. Users could opt into the new class, but we wouldn't break any existing code. Orpheus took the first step of his walk home from Hades.</p>
<h2 id="write-commands">Write commands</h2>
<p>In MongoDB 2.6, released this spring, we began to undo an even older decision: the old protocol that sends a modification to MongoDB, then calls "getLastError" to find out if it succeeded. The new protocol, <a href="http://docs.mongodb.org/manual/reference/command/nav-crud/">write commands</a>, always awaits a response from the server. Furthermore, it lets us batch hundreds of modifications in a single command, and get a batch of responses back. The change was transparent to users, but we transcended the tradeoff of our original protocol. You no longer have to decide if you want low-latency unacknowledged writes, or acknowledged writes and pay for the latency. Now you can batch up your operations, do acknowledged writes, and get the best of both worlds.</p>
<!-- Another benefit of the new write commands is scalability in a sharded cluster. With the old protocol, you had to call getLastError on the *same* connection you used for the last write operation. That means every client thread had its own connection to mongos, and mongos made a distinct connection to each shard for each client thread.

<img style="display:block; margin-left:auto; margin-right:auto;" src="old-sharding.png" alt="Old sharding" title="Old sharding" />

You can see that the number of mongos's outbound connections becomes a bottleneck when you have hundreds of client connections and dozens of shards. You can scale out the number of mongoses to account for this, but it would be better if mongos could multiplex client connections among shard connections:

<img style="display:block; margin-left:auto; margin-right:auto;" src="new-sharding.png" alt="New sharding" title="New sharding" />

MongoDB 2.6's new write commands allow us to do this: mongos need no longer call getLastError on each shard, since write commands don't require a separate getLastError. Therefore it can put a shard connection back in the general connection pool as soon as a particular operation is complete; mongos doesn't need to reserve the connection for the client in case it calls "getLastError". Therefore mongos only needs as many connections to the shards as there are concurrent operations in flight, which is far fewer than one connection per client. -->

<h2 id="sharding">Sharding</h2>
<p>The final nail was a change in MongoDB's sharding. It used to be that, as long as a thread used the same connection to mongos for secondary reads, mongos would keep using the same secondary on each shard's replica set. This was meant to prevent "time travel": if one secondary in a shard is lagging and another is not, we didn't want your client thread to read once from the caught-up secondary, and then once from the laggy secondary, getting an <em>earlier</em> view of your data.</p>
<p>But this design made mongos's connection pooling much less efficient. And we couldn't guarantee perfect monotonicity when you read from a secondary anyway. In MongoDB 2.6 we changed this behavior so that mongos balances each client connection's reads among all the secondaries. Thus, the last good reason for a client thread to always use the same connection is obsolete. It's time for "start_request" to go.</p>
<h2 id="removing-start_request">Removing start_request</h2>
<p>This morning I removed "start_request" from PyMongo's code, on the branch that will become PyMongo 3.0. The change deletes about 300 lines. The hairiest, riskiest Python I've ever written is gone. The connection pool code looks sane again. Once again, a contributor could send patches for it without opening a can of worms. Coders who start out with PyMongo won't be lured by the attractive nuisance of "start_request". And my time won't be taken up by occasional, urgent bugs in the PyMongo connection pool. Destroying my own work has never before been so satisfying, so liberating.</p>
<h1 id="post-mortem">Post-mortem</h1>
<p>The onramps of the road to hell are not well-marked. How can we recognize them next time?</p>
<p>One principle is: Don't try to give users what they can't have. You can't combine read-your-writes consistency with unacknowledged writes. Our efforts to give you both things at once were heroic, but foolish. We thought we were being generous to you by maintaining very complex code, but as <a href="https://www.python.org/dev/peps/pep-0020/">the Zen of Python</a> says,</p>
<blockquote>
<p>Simple is better than complex.<br/>
If the implementation is hard to explain, it's a bad idea.</p>
</blockquote>
<p>It's fun to write complex, hard-to-explain code. It's certainly more fun to write gnarly code now, than to think hard about the future, and wait until you've thought of a simple design that will stand the test of time. But in the case of "start_request", a better design was out there.</p>
<p>Here again, the Zen of Python is instructive. It advises us to wait until we have a pretty good answer, before we start coding:</p>
<blockquote>
<p>Now is better than never.<br/>
Although never is often better than <em>right</em> now.</p>
</blockquote>
<p>But even though we made a regrettable decision, we eventually righted ourselves. The new protocol&mdash;write commands&mdash;gives us high throughput <em>and</em> acknowledged writes, without breaking backwards compatibility. And now that we have the new protocol we can remove "start_request" in PyMongo 3.0. The walk home from hell is over.</p>
<hr />
<p><em>The next installment in "It Seemed Like A Good Idea At The Time" is <a href="/blog/it-seemed-like-a-good-idea-at-the-time-pymongo-use-greenlets/">PyMongo's "use_greenlets"</a>.</em></p>
    