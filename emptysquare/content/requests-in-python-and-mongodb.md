+++
type = "post"
title = "Requests in Python and MongoDB"
date = "2012-04-26T15:36:12"
description = "PyMongo 2.2's connection pooling."
category = ["Mongo", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "pymongo-2-1.png"
draft = false
disqus_identifier = "472 http://emptysquare.net/blog/?p=472"
disqus_url = "https://emptysqua.re/blog/472 http://emptysquare.net/blog/?p=472/"
+++

<p>If you use <a href="https://github.com/mongodb/mongo-python-driver">PyMongo</a>,
10gen's official MongoDB driver for Python, I want to ensure you
understand how it manages sockets and threads, and I want to brag about
performance improvements in PyMongo 2.2, which we plan to release next
week.</p>
<h1 id="the-problem-threads-and-sockets">The Problem: Threads and Sockets</h1>
<p>Each PyMongo <code>Connection</code> object includes a connection pool (a pool of
sockets) to minimize the cost of reconnecting. If you do two operations
(e.g., two <code>find()</code>s) on a Connection, it creates a socket for the first
<code>find()</code>, then reuses that socket for the second. (Update: <a href="/pymongos-new-default-safe-writes/">Starting
with PyMongo 2.4 you should use <code>MongoClient</code> instead of <code>Connection</code></a>.)</p>
<p>When sockets are returned to the pool, the pool checks if it has more
than <code>max_pool_size</code> spare sockets, and if so, it closes the extra
sockets. By default max_pool_size is 10. (Update: in PyMongo 2.6, <a href="/pymongo-2-6-released/">max_pool_size is now 100</a>,
and its meaning has changed since I wrote this article.)</p>
<p>What if multiple Python threads share a Connection? A possible
implementation would be for each thread to get a random socket from the
pool when needed, and return it when done. But consider the following
code. It updates a count of visitors to a web page, then displays the
number of visitors on that web page <strong>including</strong> this visit:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>Connection()
counts <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>counts
counts<span style="color: #666666">.</span>update(
    {<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()},
    {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}},
    upsert<span style="color: #666666">=</span><span style="color: #008000">True</span>)

n <span style="color: #666666">=</span> counts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()})[<span style="color: #BA2121">&#39;n&#39;</span>]

<span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;You are visitor number </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> n
</pre></div>


<p>Since PyMongo defaults to <strong>unsafe</strong> writes&mdash;that is, it does not ask the
server to acknowledge its inserts and updates&mdash;it will send the <code>update</code>
message to the server and then instantly send the <code>find_one</code>, then await
the result. (Update: if you use <code>MongoClient</code>, <a href="/pymongos-new-default-safe-writes/">safe writes are the default</a>.) If PyMongo gave out sockets to threads at random, then the
following sequence <strong>could</strong> occur:</p>
<ol>
<li>This thread gets a socket, which I'll call socket 1, from the pool.</li>
<li>The thread sends the update message to MongoDB on socket 1. The
    thread does not ask for nor await a response.</li>
<li>The thread returns socket 1 to the pool.</li>
<li>The thread asks for a socket again, and gets a different one: socket
    2.</li>
<li>The thread sends the find_one message to MongoDB on socket 2.</li>
<li>MongoDB happens to read from socket 2 first, and executes the
    find_one.</li>
<li>Finally, MongoDB reads the update message from socket 1 and executes
    it.</li>
</ol>
<p>In this case, the count displayed to the visitor wouldn't include this
visit.</p>
<p>I know what you're thinking: just do the find_one first, add one to it,
and display it to the user. <strong>Then</strong> send the update to MongoDB to
increment the counter. Or use
<a href="http://www.mongodb.org/display/DOCS/findAndModify+Command">findAndModify</a>
to update the counter and get its new value in one round trip. Those are
great solutions, but then I would have no excuse to explain requests to
you.</p>
<p>Maybe you're thinking of a different fix: use <code>update(safe=True)</code>. That
would work, as well, with the added advantage that you'd know if the
update failed, for example because MongoDB's disk is full, or you
violated a unique index. But a safe update comes with a latency cost:
you must send the update, <strong>wait for the acknowledgement</strong>, then send
the find_one and wait for the response. In a tight loop the extra
latency is significant.</p>
<h1 id="the-fix-one-socket-per-thread">The Fix: One Socket Per Thread</h1>
<p>PyMongo solves this problem by automatically assigning a socket to each
thread, when the thread first requests one. (Update: since <code>MongoClient</code> defaults to
using safe writes, <a href="/pymongos-new-default-safe-writes/#auto_start_request">it no longer assigns a socket to each thread</a>. Instead all sockets are kept in a connection pool.)
The socket is stored in a
thread-local variable within the connection pool. Since MongoDB
processes messages on any single socket in order, using a single socket
per thread guarantees that in our example code, update is processed
<strong>before</strong> find_one, so find_one's result includes the current visit.</p>
<h1 id="more-awesome-connection-pooling">More Awesome Connection Pooling</h1>
<p>While PyMongo's socket-per-thread behavior nicely resolves the
inconsistency problem, there are some nasty performance costs that are
fixed in the forthcoming PyMongo 2.2. (I did most of this work, at the
direction of PyMongo's maintainer Bernie Hackett and with
co-brainstorming by my colleague Dan Crosta.)</p>
<h2 id="connection-churn">Connection Churn</h2>
<p>PyMongo 2.1 stores each thread's socket in a thread-local variable.
Alas, when the thread dies, its thread locals are garbage-collected and
the socket is closed. This means that if you regularly create and
destroy threads that access MongoDB, then you are regularly creating and
destroying connections rather than reusing them.</p>
<p>You could call <code>Connection.end_request()</code> before the thread dies.
end_request() returns the socket to the pool so it can be used by a
future thread when it first needs a socket. But, just as most people
don't recycle their plastic bottles, most developers don't use
end_request(), so good sockets are wasted.</p>
<p>In PyMongo 2.2, I wrote a "socket reclamation" feature that notices when
a thread has died without calling end_request, and reclaims its socket
for the pool. Under the hood, I wrap each socket in a <code>SocketInfo</code>
object, whose <code>__del__</code> method returns the socket to the pool. For your
application, this means that once you've created as many sockets as you
need, those sockets can be reused as threads are created and destroyed
over the lifetime of the application, saving you the latency cost of
creating a new connection for each thread.</p>
<h2 id="total-number-of-connections">Total Number of Connections</h2>
<p>Consider a web crawler that launches hundreds of threads. Each thread
downloads pages from the Internet, analyzes them, and stores the results
of that analysis in MongoDB. Only a couple threads access MongoDB at
once, since they spend most of their time downloading pages, but PyMongo
2.1 must use a separate socket for each. In a big deployment, this could
result in thousands of connections and a lot of overhead for the MongoDB
server.</p>
<p>In PyMongo 2.2 we've added an <code>auto_start_request</code> option to the
Connection constructor. It defaults to True, in which case PyMongo 2.2's
Connection acts the same as 2.1's, except it reclaims sockets from dead
threads. If you set auto_start_request to False, however, threads can
freely and safely share sockets. The Connection will only create as many
sockets as are actually used <strong>simultaneously</strong>. In our web crawler
example, if you have a hundred threads but only a few of them are
simultaneously accessing MongoDB, then only a few sockets are ever
created.</p>
<h3 id="start95request-and-end95request">start_request and end_request</h3>
<p>If you create a Connection with auto_start_request=False you might
still want to do <strong>some</strong> series of operations on a single socket for
read-your-own-writes consistency. For that case I've provided an API
that can be used three ways, in ascending order of convenience.</p>
<p>You can call start/end_request on the Connection object directly:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>Connection(auto_start_request<span style="color: #666666">=</span><span style="color: #008000">False</span>)
counts <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>counts
<span style="background-color: #ffffcc">connection<span style="color: #666666">.</span>start_request()
</span><span style="color: #008000; font-weight: bold">try</span>:
    counts<span style="color: #666666">.</span>update(
        {<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()},
        {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}},
        upsert<span style="color: #666666">=</span><span style="color: #008000">True</span>)

    n <span style="color: #666666">=</span> counts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()})[<span style="color: #BA2121">&#39;n&#39;</span>]
<span style="color: #008000; font-weight: bold">finally</span>:
<span style="background-color: #ffffcc">    connection<span style="color: #666666">.</span>end_request()
</span></pre></div>


<h3 id="the-request-object">The Request object</h3>
<p>start_request() returns a <code>Request</code> object, so why not use it?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>Connection(auto_start_request<span style="color: #666666">=</span><span style="color: #008000">False</span>)
counts <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>counts
<span style="background-color: #ffffcc">request <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>start_request()
</span><span style="color: #008000; font-weight: bold">try</span>:
    counts<span style="color: #666666">.</span>update(
        {<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()},
        {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}},
        upsert<span style="color: #666666">=</span><span style="color: #008000">True</span>)

    n <span style="color: #666666">=</span> counts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()})[<span style="color: #BA2121">&#39;n&#39;</span>]
<span style="color: #008000; font-weight: bold">finally</span>:
<span style="background-color: #ffffcc">    request<span style="color: #666666">.</span>end()
</span></pre></div>


<h3 id="using-the-request-object-as-a-context-manager">Using the Request object as a context manager</h3>
<p>Request objects can be used as <a href="http://docs.python.org/reference/datamodel.html#context-managers">context
managers</a>
in Python 2.5 and later, so the previous example can be terser:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>Connection(auto_start_request<span style="color: #666666">=</span><span style="color: #008000">False</span>)
counts <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>counts
<span style="background-color: #ffffcc"><span style="color: #008000; font-weight: bold">with</span> connection<span style="color: #666666">.</span>start_request() <span style="color: #008000; font-weight: bold">as</span> request:
</span>    counts<span style="color: #666666">.</span>update(
        {<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()},
        {<span style="color: #BA2121">&#39;$inc&#39;</span>: {<span style="color: #BA2121">&#39;n&#39;</span>: <span style="color: #666666">1</span>}},
        upsert<span style="color: #666666">=</span><span style="color: #008000">True</span>)

    n <span style="color: #666666">=</span> counts<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: this_page_url()})[<span style="color: #BA2121">&#39;n&#39;</span>]
</pre></div>


<h1 id="proof">Proof</h1>
<p>I wrote a <a href="https://gist.github.com/2212215">very messy test script</a> to
verify the effect of my changes on the number of open sockets, and the
total number of sockets created.</p>
<p>The script queries Mongo for 60 seconds. It starts a thread each second
for 40 seconds, each thread lasting for 20 seconds and doing 10 queries
per second. So there's a 20-second rampup until there are 20 threads,
then 20 seconds of steady-state with 20 concurrent threads (one dying
and one created per second), then a 20 second cooldown until the last
thread completes. My script then parses the MongoDB log to see when
sockets were opened and closed.</p>
<p>I tested the script with the current PyMongo 2.1, and also with PyMongo
2.2 with auto_start_request=True and with auto_start_request=False.</p>
<p>PyMongo 2.1 has one socket per thread throughout the test. Each new
thread starts a new socket because old threads' sockets are lost. It
opens 41 total sockets (one for each worker thread plus one for the
main) and tops out at 21 concurrent sockets, because there are 21
concurrent threads (counting the main thread):</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-2-1.png" title="Pymongo 2.1" /></p>
<p>PyMongo 2.2 with auto_start_request=True acts rather differently (and
much better). It ramps up to 21 sockets and keeps them open throughout
the test, reusing them for new threads when old threads die:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-2-2-auto-start-request.png" title="Pymongo 2.2, auto\_start\_request=True" /></p>
<p>And finally, with auto_start_request=False, PyMongo 2.2 only needs as many
sockets as there are threads <strong>concurrently</strong> waiting for responses from
MongoDB. In my test, this tops out at 7 sockets, which stay open until
the whole pool is deleted, because max_pool_size is 10:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-2-2-no-auto-start-request.png" title="Pymongo 2.2, auto\_start\_request=False" /></p>
<h1 id="conclusion">Conclusion</h1>
<p>Applications that create and destroy a lot of threads without calling
end_request() should run significantly faster with PyMongo 2.2 because
threads' sockets are automatically reused after the threads die.</p>
<p>Although we had to default the new auto_start_request option to True
for backwards compatibility, virtually all applications should set it to
False. Heavily multithreaded apps will need far fewer sockets this way,
meaning they'll spend less time establishing connections to MongoDB, and
put less load on the server.</p>
