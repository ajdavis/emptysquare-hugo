+++
type = "post"
title = "Tornado Locks And Queues (The End Of Toro)"
date = "2015-05-28T11:46:28"
description = "I merged Toro, my library for coordinating asynchronous coroutines, into Tornado 4.2."
categories = ["Programming", "Python"]
tags = ["tornado"]
enable_lightbox = false
thumbnail = "toro.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p>On Tuesday, Ben Darnell released Tornado 4.2, with two new modules: <a href="http://www.tornadoweb.org/en/stable/locks.html">tornado.locks</a> and <a href="http://www.tornadoweb.org/en/stable/queues.html">tornado.queues</a>. These new modules help you coordinate Tornado's asynchronous coroutines with patterns familiar from multi-threaded programming.</p>
<p>I originally developed these features in my <a href="https://toro.readthedocs.org/">Toro</a> package, which I began almost three years ago, and I'm honored that Ben has adopted my code into Tornado's core. It's a bit sad, though, because this is the end of the line for Toro, one of the best ideas of my career. Skip to the bottom for my thoughts on Toro's retirement.</p>
<p>The classes Condition and Queue are representative of Tornado's new features. Here's how one coroutine signals another, using a Condition:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">condition <span style="color: #666666">=</span> locks<span style="color: #666666">.</span>Condition()

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">waiter</span>():
    <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;I&#39;ll wait right here&quot;</span>)
    <span style="color: #008000; font-weight: bold">yield</span> condition<span style="color: #666666">.</span>wait()  <span style="color: #408080; font-style: italic"># Yield a Future.</span>
    <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;I&#39;m done waiting&quot;</span>)

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">notifier</span>():
    <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;About to notify&quot;</span>)
    condition<span style="color: #666666">.</span>notify()
    <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;Done notifying&quot;</span>)

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">runner</span>():
    <span style="color: #408080; font-style: italic"># Yield two Futures; wait for waiter() and notifier() to finish.</span>
    <span style="color: #008000; font-weight: bold">yield</span> [waiter(), notifier()]

io_loop<span style="color: #666666">.</span>run_sync(runner)
</pre></div>


<p>This script prints:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">I&#39;ll wait right here
About to notify
Done notifying
I&#39;m done waiting
</pre></div>


<p>As you can see, the Condition interface is close to the Python standard library's Condition. But instead of coordinating threads, Tornado's Condition coordinates asynchronous coroutines.</p>
<p>Tornado's Queue is similarly analogous to the standard Queue:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">q <span style="color: #666666">=</span> queues<span style="color: #666666">.</span>Queue(maxsize<span style="color: #666666">=2</span>)

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">consumer</span>():
    <span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
        item <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> q<span style="color: #666666">.</span>get()
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;Doing work on </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> item)
            <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>sleep(<span style="color: #666666">0.01</span>)
        <span style="color: #008000; font-weight: bold">finally</span>:
            q<span style="color: #666666">.</span>task_done()

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">producer</span>():
    <span style="color: #008000; font-weight: bold">for</span> item <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">5</span>):
        <span style="color: #008000; font-weight: bold">yield</span> q<span style="color: #666666">.</span>put(item)
        <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;Put </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> item)

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">main</span>():
    consumer()           <span style="color: #408080; font-style: italic"># Start consumer.</span>
    <span style="color: #008000; font-weight: bold">yield</span> producer()     <span style="color: #408080; font-style: italic"># Wait for producer to put all tasks.</span>
    <span style="color: #008000; font-weight: bold">yield</span> q<span style="color: #666666">.</span>join()       <span style="color: #408080; font-style: italic"># Wait for consumer to finish all tasks.</span>
    <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;Done&#39;</span>)

io_loop<span style="color: #666666">.</span>run_sync(main)
</pre></div>


<p>This will print:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Put 0
Put 1
Put 2
Doing work on 0
Doing work on 1
Put 3
Doing work on 2
Put 4
Doing work on 3
Doing work on 4
Done
</pre></div>


<p>Tornado's new locks and queues implement the same familiar patterns we've used for decades to coordinate threads. There's no need to invent these techniques anew for coroutines.</p>
<p>I was inspired to write these classes in 2012, when I was deep in the initial implementation of <a href="https://motor.readthedocs.org/">Motor</a>, my MongoDB driver for Tornado. The time I spent learning about coroutines for Motor's sake provoked me to wonder, how far could I push them? How much of the threading API was applicable to coroutines? The outcome was Toro&mdash;not necessarily evidence of my genius, but a very good idea that led me far. Toro's scope was straightforward, and I had to make very few decisions. The initial implementation took a week or two. I commissioned the cute bull character from <a href="http://whimsyload.com/">Musho Rodney Alan Greenblat</a>. The cuteness of Musho's art matched the simplicity of Toro's purpose.</p>
<p>When I heard about Guido van Rossum's Tulip project at his PyCon talk in 2013, I thought he could use Toro's locks and queues. It would be an excuse for me to work with Guido. I found that Tulip already had locks, implemented by Nikolay Kim if I remember right, but it didn't have queues yet so I jumped in and contributed mine. It was a chance to be code-reviewed by Guido and other Python core developers. In the long run, when Tulip became the <code>asyncio</code> standard library module, <a href="https://docs.python.org/3.4/library/asyncio-queue.html">my queues</a> became my first big contribution to the Python standard library.</p>
<p>Toro has led me to collaborate with Guido van Rossum and Ben Darnell, two of the coders I admire most. And now Toro's life is over. Its code is split up and merged into much larger and better-known projects. The name "Toro" and the character are relics. When I find the time I'll post the deprecation notice and direct people to use the locks and queues in Tornado core. Toro was the most productive idea of my career. Now I'm waiting for the next one.</p>
    