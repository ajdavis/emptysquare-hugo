+++
type = "post"
title = "Response to \"Asynchronous Python and Databases\""
date = "2015-04-01T08:52:40"
description = "Some thoughts on Mike Bayer's excellent article about asyncio, database drivers, and performance."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "tulips@240.png"
draft = false
legacyid = "550e28c55393741c65d16a26"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tulips.png" alt="Tulips" title="Tulips" /></p>
<p>In his excellent article a few weeks ago, <a href="http://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/">"Asynchronous Python and Databases"</a>, SQLAlchemy's author Mike Bayer writes:</p>
<blockquote>
<p>Asynchronous programming is just one potential approach to have on the shelf, and is by no means the one we should be using all the time or even most of the time, unless we are writing HTTP or chat servers or other applications that specifically need to concurrently maintain large numbers of arbitrarily slow or idle TCP connections (where by "arbitrarily" we mean, we don't care if individual connections are slow, fast, or idle, throughput can be maintained regardless).</p>
</blockquote>
<p>This is nicely put. If you are serving very slow or sleepy connections, which must be held open indefinitely awaiting events, async usually scales better than starting a thread per socket. In contrast, if your server application's typical workload is quick requests and responses, async may <em>not</em> be right for it. On the third hand, if it listens on the public Internet a <a href="http://en.wikipedia.org/wiki/Slowloris_%28software%29">slow loris attack</a> will force it to handle the kind of workload that async is best at, anyway. So you at least need a non-blocking frontend like Nginx to handle slow requests from such an attacker.</p>
<p>And async isn't just for servers. Clients that open a very large number of connections, and await events indefinitely, will scale up better if they are async. This is less commonly required on the client side. But for hugely I/O-bound programs like web crawlers you may start to see an advantage with async.</p>
<p>The general principle is: if you do not control both sides of the socket, one side may be arbitrarily slow. Perhaps maliciously slow. Your side had better be able to handle slow connections efficiently.</p>
<p>But what about your application's connection to your database? Here, you control both sides, and you are responsible for ensuring all database requests are quick. As Mike's tests showed, your application may not spend much time at all waiting for database responses. He tested with Postgres, but a well-configured MongoDB instance is similarly responsive. With a low-latency database your program's raw speed, not its scalability, is your priority. In this case async is not the right answer, at least not in Python: a small thread pool serving low-latency connections is typically faster than an async framework.</p>
<p>I agree with Mike's article, based on my own tests and my discussions with Tornado's author Ben Darnell. As I <a href="/blog/pycon-2014-video-what-is-async/">said at PyCon last year</a>, async minimizes resources per idle connection, while you are waiting for some event to occur in the indefinite future. Its big win is not that it is faster. In many cases it is not.</p>
<p>The strategy Mike seems to advocate is to separate the async API for a database driver from an async <em>implementation</em> for it. In asyncio, for example, it is important that you can read from a database with code like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@asyncio</span><span style="color: #666666">.</span>coroutine
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">my_query_method</span>():
    <span style="color: #408080; font-style: italic"># &quot;yield from&quot; unblocks the event loop while</span>
    <span style="color: #408080; font-style: italic"># waiting for the database.</span>
    result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield from</span> my_db<span style="color: #666666">.</span>query(<span style="color: #BA2121">&quot;query&quot;</span>)
</pre></div>


<p>But it is <em>not</em> necessary to reimplement the driver itself using non-blocking sockets and asyncio's event loop. If <code>db.query</code> defers your operation to a thread pool, and injects the result into the event loop on the main thread when it is ready, it might be faster and scales perfectly well for the small number of database connections you need.</p>
<p>So what about <a href="http://motor.readthedocs.org/">Motor</a>, my asynchronous driver for MongoDB and Tornado? With some effort, I wrote Motor to provide an async API to MongoDB for <a href="http://www.tornadoweb.org/">Tornado</a> applications, and to use non-blocking connections to MongoDB with Tornado's event loop. (Motor uses <a href="http://greenlet.readthedocs.org/">greenlets</a> internally to ease the latter task, but greenlets are beside the point for this discussion.) If Mike Bayer's article is right, and I believe it is, was Motor a waste?</p>
<p>With Motor, I achieved two goals. One was necessary, but I am reconsidering the other. The necessary goal was to provide an async API for Tornado applications that want to use MongoDB; Motor succeeds at this. But I wonder if Motor would not have marginally better throughput if it used a thread pool and blocking sockets, instead of Tornado's event loop, to talk to MongoDB. If I began again, particularly now that the <a href="http://pythonhosted.org/futures/">concurrent.futures</a> threadpool is more mainstream, I might use threads instead. It may be possible to gain ten or twenty percent on some benchmarks, and streamline future development too. Later this year I hope to make the time to experiment with the performance and maintainability of that approach for some future version of Motor.</p>
