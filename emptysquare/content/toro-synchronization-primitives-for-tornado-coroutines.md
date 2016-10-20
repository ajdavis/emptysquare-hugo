+++
type = "post"
title = "Toro: synchronization primitives for Tornado coroutines"
date = "2012-11-18T15:17:49"
description = "I took a break from Motor to make a new package \"Toro\": queues, semaphores, locks, and so on for Tornado coroutines. (The name \"Toro\" is from \"Tornado\" and \"Coro\".) Why would you need something like this, especially since Tornado apps are [ ... ]"
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "toro.png"
draft = false
disqus_identifier = "50a9422b5393741e2d1b4d16"
disqus_url = "https://emptysqua.re/blog/50a9422b5393741e2d1b4d16/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p>I took a break from <a href="/motor/">Motor</a> to make a new package "Toro": queues, semaphores, locks, and so on for Tornado coroutines. (The name "Toro" is from "Tornado" and "Coro".)</p>
<p>Why would you need something like this, especially since Tornado apps are usually single-threaded? Well, with Tornado's <a href="http://www.tornadoweb.org/en/latest/gen.html">gen</a> module you can turn Python generators into full-featured coroutines, but coordination among these coroutines is difficult. If one coroutine wants exclusive access to a resource, how can it notify other coroutines to proceed once it's finished? How do you allow N coroutines, but no more than N, access a resource at once? How do you start a set of coroutines and end your program when the last completes?</p>
<p>Each of these problems can be solved individually, but Toro's classes generalize the solutions. Toro provides to Tornado coroutines a set of locking primitives and queues analogous to those that Gevent provides to Greenlets, or that the standard library provides to threads.</p>
<p>Here's a producer-consumer example with a <code>toro.Queue</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> ioloop, gen
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">toro</span>

q <span style="color: #666666">=</span> toro<span style="color: #666666">.</span>JoinableQueue(maxsize<span style="color: #666666">=3</span>)

<span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">consumer</span>():
    <span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
        item <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(q<span style="color: #666666">.</span>get)
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Doing work on&#39;</span>, item
        <span style="color: #008000; font-weight: bold">finally</span>:
            q<span style="color: #666666">.</span>task_done()

<span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">producer</span>():
    <span style="color: #008000; font-weight: bold">for</span> item <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10</span>):
        <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(q<span style="color: #666666">.</span>put, item)

<span style="color: #008000; font-weight: bold">if</span> __name__ <span style="color: #666666">==</span> <span style="color: #BA2121">&#39;__main__&#39;</span>:
    producer()
    consumer()
    loop <span style="color: #666666">=</span> ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()
    q<span style="color: #666666">.</span>join(callback<span style="color: #666666">=</span>loop<span style="color: #666666">.</span>stop) <span style="color: #408080; font-style: italic"># block until all tasks are done</span>
    loop<span style="color: #666666">.</span>start()
</pre></div>


<p>More <a href="http://toro.readthedocs.org/en/latest/examples/index.html">examples are in the docs</a>: graceful shutdown using Toro's <code>Lock</code>, a caching proxy server with <code>Event</code>, and a web spider with <code>Queue</code>. Further reading:</p>
<p><a href="http://toro.readthedocs.org/">Toro on Read the Docs</a></p>
<p><a href="https://github.com/ajdavis/toro">Toro on Github</a></p>
<p><a href="http://pypi.python.org/pypi/toro/">Toro on PyPI</a></p>
<p><em>Toro logo by <a href="http://whimsyload.com/">Musho Rodney Alan Greenblat</a></em></p>
