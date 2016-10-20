+++
type = "post"
title = "Motor Internals: How I Asynchronized a Synchronous Library"
date = "2012-07-09T22:07:45"
description = "How and why I wrote Motor, my asynchronous driver for MongoDB and Tornado."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-collection.png"
draft = false
disqus_identifier = "4ffb8e715393742d5b000000"
disqus_url = "https://emptysqua.re/blog/4ffb8e715393742d5b000000/"
+++

<p>I'm going to explain why and how I wrote <a href="/motor/">Motor</a>, my asynchronous driver for MongoDB and Tornado. I hope I can justify my ways to you.</p>
<h1 id="the-problem">The Problem</h1>
<p>Here's how you query one document from MongoDB with <a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a>, 10gen's official driver:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> Connection()
document <span style="color: #666666">=</span> connection<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find_one()
<span style="color: #008000; font-weight: bold">print</span> document
</pre></div>


<p>As you can see, the official driver is blocking: you call <code>find_one</code> and your code waits for the result.</p>
<p>Deep in the bowels of PyMongo, the driver sends your query over a socket and waits for the database's response:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Connection</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">send_and_receive</span>(<span style="color: #008000">self</span>, message, socket):
        socket<span style="color: #666666">.</span>sendall(message)
        header <span style="color: #666666">=</span> socket<span style="color: #666666">.</span>recv(<span style="color: #666666">16</span>) <span style="color: #408080; font-style: italic"># Get 16-byte header</span>
        length <span style="color: #666666">=</span> struct<span style="color: #666666">.</span>unpack(<span style="color: #BA2121">&quot;&lt;i&quot;</span>, header[:<span style="color: #666666">4</span>])[<span style="color: #666666">0</span>]
        body <span style="color: #666666">=</span> socket<span style="color: #666666">.</span>recv(length)
        <span style="color: #008000; font-weight: bold">return</span> header <span style="color: #666666">+</span> body
</pre></div>


<p>That's three blocking operations on the socket in a row. All of PyMongo relies on the assumption that it can use sockets synchronously. How the hell can I make it non-blocking so you can use it with Tornado? Specifically, how can I implement this API?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">opened</span>(connection, error):
    connection<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find_one(callback<span style="color: #666666">=</span>found)

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">found</span>(document, error):
    <span style="color: #008000; font-weight: bold">print</span> document

MotorConnection()<span style="color: #666666">.</span>open(callback<span style="color: #666666">=</span>opened)
</pre></div>


<h1 id="asyncmongos-solution">AsyncMongo's Solution</h1>
<p>bit.ly's non-blocking driver, <a href="https://github.com/bitly/asyncmongo">AsyncMongo</a>, took the straightforward approach. It copied and pasted PyMongo as it stood two years ago, and turned it inside-out to use callbacks. PyMongo's <code>send_and_receive</code> became this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Connection</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">send_and_receive</span>(<span style="color: #008000">self</span>, message, callback):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>callback <span style="color: #666666">=</span> callback

        <span style="color: #408080; font-style: italic"># self.stream is a Tornado IOStream</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>stream<span style="color: #666666">.</span>write(message)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>stream<span style="color: #666666">.</span>read_bytes(<span style="color: #666666">16</span>,
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>parse_header)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">parse_header</span>(<span style="color: #008000">self</span>, data):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>header <span style="color: #666666">=</span> data
        length <span style="color: #666666">=</span> struct<span style="color: #666666">.</span>unpack(<span style="color: #BA2121">&quot;&lt;i&quot;</span>, data[:<span style="color: #666666">4</span>])[<span style="color: #666666">0</span>]
        <span style="color: #008000">self</span><span style="color: #666666">.</span>stream<span style="color: #666666">.</span>read_bytes(length,
            callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>parse_response)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">parse_response</span>(<span style="color: #008000">self</span>, data):
        response <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>header <span style="color: #666666">+</span> data
        <span style="color: #008000">self</span><span style="color: #666666">.</span>callback(response)
</pre></div>


<p>(Note that IOStream buffers the output in <code>write</code>, so only the <code>read_bytes</code> calls take callbacks.)</p>
<p>This is a solution to the problem of making PyMongo async, but now there's a new problem: how do we maintain code like this? PyMongo is extended and improved every month by 10gen's programmers (like me!). An effort comparable to that devoted to maintaining PyMongo would be required to keep AsyncMongo up to date, because every PyMongo change must be manually ported over. Who has that kind of time?</p>
<h1 id="motors-solution">Motor's Solution</h1>
<p>Since I joined 10gen in November last year, I'd been thinking there must be a better way. I wanted to somehow reuse all of PyMongo's existing code&mdash;its years of improvements and bugfixes and battle-testing&mdash;but make it non-blocking so Tornado programmers could use it. I thought that if Python had something like Scheme's <a href="http://en.wikipedia.org/wiki/Call-with-current-continuation">call-with-current-continuation</a>, I could pause PyMongo's execution whenever it would block waiting for a socket, and resume when the socket was ready. From that thought, it surely took me longer, dear reader, than it would have taken you to deduce the solution, but during a particularly distracted meditation session it somehow dawned on me: <a href="http://pypi.python.org/pypi/greenlet">greenlets</a>. I'd use a Gevent-like technique to wrap PyMongo and asynchronize it, while presenting a classic Tornado callback API to you.</p>
<p>Asynchronizing PyMongo takes two steps. First, I wrap each PyMongo method and run it on a greenlet, like this:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-collection.png" alt="MotorCollection" title="motor-collection.png" border="0"   /></p>
<p>So when you call <code>collection.find_one(callback=found)</code>, Motor (1) grabs the callback argument and (2) starts a greenlet that (3) runs PyMongo's original <code>find_one</code>. That <code>find_one</code> sends a message to the server and calls <code>recv</code> on a socket to get the response.</p>
<p>The second step is to pause the greenlet whenever it would block. I wrote a <code>MotorSocket</code> class which seems to PyMongo like a regular socket, but in fact it wraps a Tornado IOStream:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-socket.png" alt="MotorSocket" title="motor-socket.png" border="0"   /></p>
<p><code>MotorSocket.recv</code> (4) starts reading the requested number of bytes and (5) pauses the caller's greenlet. At this point, (6) the original call to <code>find_one</code> returns. Because Motor's API is callback-based, its <code>find_one</code> returns <code>None</code>. The actual MongoDB document will be passed into the callback asynchronously.</p>
<p>Eventually, IOStream's <code>read_bytes</code> call completes and executes the callback, which (7) resumes the paused greenlet. That greenlet then completes PyMongo's processing, parsing the server's response and so on, until PyMongo's original <code>find_one</code> returns. Motor gets a result or an exception from PyMongo's <code>find_one</code> and (8) schedules your callback on the IOLoop.</p>
<p>(The real code is a little more complicated, <a href="https://github.com/mongodb/motor/blob/0.5/motor/frameworks/tornado.py#L288">gory details here</a>.)</p>
<p>If you're a visual learner, here's the same sequence of events diagrammed:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-internals.png" alt="Motor Internals" title="motor-internals.png" border="0"   /></p>
<p>Sorry, it's the best diagram I can think of.</p>
<h1 id="why">Why?</h1>
<p>PyMongo is three and a half years old. The core module is 3000 source lines of code. There are hundreds improvements and bugfixes, and 7000 lines of unittests. Anyone who tries to make a non-blocking version of it has a lot of work cut out, and will inevitably fall behind development of the official PyMongo. With Motor's technique, I can wrap and reuse PyMongo whole, and when we fix a bug or add a feature to PyMongo, Motor will come along for the ride, for free.</p>
