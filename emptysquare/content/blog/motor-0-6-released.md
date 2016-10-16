+++
type = "post"
title = "Announcing Motor 0.6"
date = "2016-03-06T16:41:34"
description = "A bugfix release, and an entertaining problem from a change in asyncio coroutines."
categories = ["Programming", "Mongo", "Python", "Motor"]
tags = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor logo by Musho Rodney Alan Greenblat" title="motor-musho.png" border="0" /></p>
<p>Motor is the asynchronous Python driver for MongoDB. It is compatible with Tornado and asyncio.</p>
<p>This is just a patch release with <a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%200.6%20AND%20project%20%3D%20MOTOR">six bugfixes</a>, but some fixes required tiny API changes that
might affect you, so I'm bumping the version from 0.5 to 0.6, instead of to 0.5.1. Read below for the changes&mdash;if you make it to the bottom you'll learn about an abstruse asyncio optimization in Python 3.5.1!</p>
<h1 id="motor_asyncio-and-motor_tornado-submodules"><code>motor_asyncio</code> and <code>motor_tornado</code> submodules</h1>
<p>These modules have been moved from:</p>
<ul>
<li><code>motor_asyncio.py</code></li>
<li><code>motor_tornado.py</code></li>
</ul>
<p>To:</p>
<ul>
<li><code>motor_asyncio/__init__.py</code></li>
<li><code>motor_tornado/__init__.py</code></li>
</ul>
<p>Motor had to make this change in order to omit the <code>motor_asyncio</code> submodule
entirely and avoid a spurious <code>SyntaxError</code> being printed when installing in
Python 2. The change should be invisible to application code. Thanks to Jordi Soucheiron for the report.</p>
<h1 id="database-and-collection-names-with-leading-underscores">Database and collection names with leading underscores</h1>
<p>A database or collection whose name starts with an underscore can no longer be
accessed as a property:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Now raises AttributeError.</span>
db <span style="color: #666666">=</span> MotorClient()<span style="color: #666666">.</span>_mydatabase
collection <span style="color: #666666">=</span> db<span style="color: #666666">.</span>_mycollection
subcollection <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>_subcollection
</pre></div>


<p>Such databases and collections can still be accessed dict-style:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Continues to work the same as previous Motor versions.</span>
db <span style="color: #666666">=</span> MotorClient()[<span style="color: #BA2121">&#39;_mydatabase&#39;</span>]
collection <span style="color: #666666">=</span> db[<span style="color: #BA2121">&#39;_mycollection&#39;</span>]
</pre></div>


<p>To ensure a "sub-collection" with a name that includes an underscore is
accessible, Motor collections now allow dict-style access, the same as Motor
clients and databases always have:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># New in Motor 0.6</span>
subcollection <span style="color: #666666">=</span> collection[<span style="color: #BA2121">&#39;_subcollection&#39;</span>]    
</pre></div>


<p>These changes solve problems with iPython code completion and the Python 3
<code>ABC</code> abstract base class. Thanks to <a href="https://github.com/TechBK">TechBK</a> and Andrew Svetlov for reporting and diagnosing the bug.</p>
<h1 id="change-to-asyncio-coroutines">Change to asyncio coroutines</h1>
<p>There is also a pure bugfix with no API consequences, but it's interesting enough that I wrote it up.</p>
<p>Motor's internals mostly use callbacks and greenlets. Just one rarely-used function, <a href="http://motor.readthedocs.org/en/stable/api/gridfs.html#motor.motor_tornado.MotorGridOut.stream_to_handler"><code>stream_to_handler</code></a>, is a generator-based coroutine. This coroutine needs a framework-agnostic way to resolve a Future into a value:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_framework<span style="color: #666666">.</span>yieldable(some_future)
</pre></div>


<p>Motor's utility <code>yieldable()</code> abstracts differences between Tornado and asyncio, so the coroutine works with either framework. If the framework is asyncio, then <code>yieldable</code> does some footwork to avoid the need for <code>yield from</code> in Motor:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">yieldable</span>(future):
    <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">next</span>(<span style="color: #008000">iter</span>(future))
</pre></div>


<p>So <code>yieldable</code> gets the Future started, then just returns it to be yielded up the coroutine chain. When the coroutine is resumed with a call to <code>coro.send(value)</code>, that becomes the value of the yield expression.</p>
<p>This wouldn't work if Motor's coroutine called another coroutine with multiple yields. But in Motor's narrow use case, I overcome the need for <code>yield from</code> with asyncio, so I can write code that works equally well with Tornado.</p>
<p>Recently, Yury Selivanov <a href="https://github.com/python/asyncio/pull/289">optimized how asyncio coroutines resolve Futures to values</a>. When an asyncio coroutine pauses:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield from</span> some_future
</pre></div>


<p>... it stops within <code>Future.__iter__</code> at the <code>yield</code> statement:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Future</span>:
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__iter__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>done():
            <span style="color: #408080; font-style: italic"># Tell Task to wait for completion.</span>
            <span style="color: #008000; font-weight: bold">yield</span> <span style="color: #008000">self</span>
        <span style="color: #408080; font-style: italic"># Resume coroutine with the result.</span>
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>result()
</pre></div>


<p>The Task class later resumes the coroutine with a value like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Task</span>:
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">step</span>(<span style="color: #008000">self</span>, value):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>coro<span style="color: #666666">.</span>send(value)
</pre></div>


<p>Yury noticed that, when the coroutine resumes, the actual result comes directly from the Future, when it returns <code>self.result()</code>. That means it doesn't matter what value Task passes with <code>send(value)</code>!  Not only does the value not matter, but CPython chooses a faster code path when it executes <code>send(None)</code> instead. So he updated asyncio to do that, and the optimization was released with Python 3.4.4 and 3.5.1.</p>
<p>Everybody was happy but me. I retested Motor this weekend and found that Yury's change broke my <code>yieldable</code> trick. Now <code>stream_to_handler</code>, and any other Motor function I write from now on that resolves a Future to a value, must resolve it in two steps:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">while</span> written <span style="color: #666666">&lt;</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>length:
    f <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_framework<span style="color: #666666">.</span>yieldable(<span style="color: #008000">self</span><span style="color: #666666">.</span>read(<span style="color: #008000">self</span><span style="color: #666666">.</span>chunk_size))
    <span style="color: #008000; font-weight: bold">yield</span> f
    chunk <span style="color: #666666">=</span> f<span style="color: #666666">.</span>result()
</pre></div>


<p>This is a minor bug since Motor's sole coroutine, <code>stream_to_handler</code>, isn't really useful with asyncio until I finish <a href="https://jira.mongodb.org/browse/MOTOR-92">some larger feature work</a>. But the diagnosis was a scenic trip.</p>
    