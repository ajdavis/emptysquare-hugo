+++
type = "post"
title = "Toro Rewritten for Tornado 3.0"
date = "2013-04-12T16:27:58"
description = ""
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "toro@240.png"
draft = false
legacyid = "51686df353937474b99b1858"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p><a href="/blog/pycon-lightning-talk-about-toro/">Speaking of my package Toro</a>, I've just released version 0.5. Toro provides semaphores, queues, and so on, for advanced control flows with Tornado coroutines. </p>
<p>Version 0.5 is a rewrite, motivated by two recent events. First, the release of Tornado 3.0 has introduced a much more convenient coroutine API, and I wanted Toro to support the modern style. Second, I <a href="http://code.google.com/p/tulip/source/detail?r=f83dba559f89">contributed a version of Toro's queues to Tulip</a>, and the queues changed a bit in the process. As much as possible, I updated Toro to match the API of Tulip's locks and queues, for consistency's sake.</p>
<p>In previous versions, most Toro methods had to be wrapped in <code>gen.Task</code>, which made for weird-looking code. But using Toro is now quite graceful. For example, a producer-consumer pair:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">q <span style="color: #666666">=</span> toro<span style="color: #666666">.</span>Queue()

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">producer</span>():
    <span style="color: #008000; font-weight: bold">for</span> item <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">5</span>):
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Sending&#39;</span>, item
        <span style="color: #008000; font-weight: bold">yield</span> q<span style="color: #666666">.</span>put(item)

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">consumer</span>():
    <span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
        item <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> q<span style="color: #666666">.</span>get()
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;</span><span style="color: #BB6622; font-weight: bold">\t\t</span><span style="color: #BA2121">&#39;</span>, <span style="color: #BA2121">&#39;Got&#39;</span>, item

consumer()
producer()
IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>start()
</pre></div>


<p>Another nice new feature: <code>Semaphore.acquire</code> and <code>Lock.acquire</code> can be used with the <code>with</code> statement:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">lock <span style="color: #666666">=</span> toro<span style="color: #666666">.</span>Lock()

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
   <span style="color: #008000; font-weight: bold">with</span> (<span style="color: #008000; font-weight: bold">yield</span> lock<span style="color: #666666">.</span>acquire()):
       <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;We&#39;re in the lock&quot;</span>

   <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;Out of the lock&quot;</span>
</pre></div>


<p>More <a href="http://toro.readthedocs.org/en/stable">examples are in the docs</a>. Enjoy!</p>
    