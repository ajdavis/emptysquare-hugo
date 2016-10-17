+++
type = "post"
title = "Toro 0.6 Released"
date = "2014-07-08T22:05:47"
description = "One minor bug fixed in Toro, my package of semaphores, locks, and queues for Tornado coroutines."
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "toro@240.png"
draft = false
legacyid = "53bca2fb5393745d31c3f8b7"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p>I've just released version 0.6 of Toro. Toro provides semaphores, queues, and so on, for advanced control flows with Tornado coroutines. Get it with "pip install --upgrade toro". Toro's <a href="https://toro.readthedocs.org/">documentation, with plenty of examples, is on ReadTheDocs</a>.</p>
<p>There is one bugfix in this release. A floating point <code>maxsize</code> had been treated as infinite. So if you did this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">q <span style="color: #666666">=</span> toro<span style="color: #666666">.</span>Queue(maxsize<span style="color: #666666">=1.3</span>)
</pre></div>


<p>...then the queue would never be full. In the newest version of Toro, a <code>maxsize</code> of 1.3 now acts like a <code>maxsize</code> of 2.</p>
<p>Shouldn't Toro just require that <code>maxsize</code> be an integer? Well, <a href="https://docs.python.org/2/library/queue.html">the Python standard Queue</a> allows a floating-point number. So when Vajrasky Kok noticed that asyncio's Queue treats a floating-point <code>maxsize</code> as infinity, he proposed a fix that handles floats the same as the standard Queue does. (That asyncio bug was my fault, too.)</p>
<p>Once Guido van Rossum accepted that fix, I updated Toro to comply with the other two Queues.</p>
    