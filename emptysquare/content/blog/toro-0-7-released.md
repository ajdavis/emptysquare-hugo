+++
type = "post"
title = "Toro 0.7 Released"
date = "2014-10-29T10:09:55"
description = "A major bug fixed in Toro, my package of semaphores, locks, and queues for Tornado coroutines."
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "toro@240.png"
draft = false
legacyid = "5450f3bb5393740960d41350"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toro.png" alt="Toro" title="toro.png" border="0"   /></p>
<p>I've just released version 0.7 of Toro. Toro provides semaphores, locks, events, conditions, and queues for Tornado coroutines. It enables advanced coordination among coroutines, similar to what you do in a multithreaded application. Get the latest version with "pip install --upgrade toro". Toro's <a href="https://toro.readthedocs.org/">documentation, with plenty of examples, is on ReadTheDocs</a>.</p>
<p>There is one bugfix in this release. <a href="https://toro.readthedocs.org/en/stable/classes.html#toro.Semaphore.wait">Semaphore.wait()</a> is supposed to wait until the semaphore can be acquired again:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">coro</span>():
    sem <span style="color: #666666">=</span> toro<span style="color: #666666">.</span>Semaphore(<span style="color: #666666">1</span>)
    <span style="color: #008000; font-weight: bold">assert</span> <span style="color: #AA22FF; font-weight: bold">not</span> sem<span style="color: #666666">.</span>locked()

    <span style="color: #408080; font-style: italic"># A semaphore with initial value of 1 can be acquired once,</span>
    <span style="color: #408080; font-style: italic"># then it&#39;s locked.</span>
    sem<span style="color: #666666">.</span>acquire()
    <span style="color: #008000; font-weight: bold">assert</span> sem<span style="color: #666666">.</span>locked()

    <span style="color: #408080; font-style: italic"># Wait for another coroutine to release the semaphore.</span>
    <span style="color: #008000; font-weight: bold">yield</span> sem<span style="color: #666666">.</span>wait()
</pre></div>


<p>... however, there was a bug and the semaphore didn't mark itself "locked" when it was acquired, so "wait" always returned immediately. I'm grateful to <a href="https://github.com/DanielBlack">"abing"</a> on GitHub for noticing the bug and contributing a fix.</p>
    