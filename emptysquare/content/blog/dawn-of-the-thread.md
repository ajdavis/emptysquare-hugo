+++
type = "post"
title = "Dawn Of The Thread"
date = "2013-10-25T10:17:05"
description = "How to avoid zombie threads in ancient versions of Python."
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["threading"]
enable_lightbox = false
thumbnail = "dawn-of-the-thread@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="dawn-of-the-thread.jpg" alt="Dawn of the thread" title="Dawn of the thread" /></p>
<p>In my previous post, <a href="/blog/night-of-the-living-thread/">Night of the Living Thread</a>, I described how a dead Python thread may think it's still alive after a fork, and how I fixed this bug in the Python standard library. But what if you need to save your code from the ravenous undead in Python 2.6? The bug will never be fixed in Python 2.6's standard library. You're on your own. In Python 2.6, no one can hear you scream.</p>
<p>Recall from my last post that I can create a zombie thread like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread()
t<span style="color: #666666">.</span>start()
<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork() <span style="color: #666666">==</span> <span style="color: #666666">0</span>:
    <span style="color: #408080; font-style: italic"># We&#39;re in the child process.</span>
    <span style="color: #008000; font-weight: bold">print</span> t<span style="color: #666666">.</span>isAlive()
</pre></div>


<p>isAlive() should always be False, but sometimes it's True. The problem is, I might fork before the thread has added itself to the global <code>_active</code> list, so Python doesn't mark the thread as "stopped" after the fork. To fix this, I need <code>t.start()</code> to wait until the thread is completely initialized, so that I can't fork too soon.</p>
<p>Here's my solution, a SafeThread that will never rise from its grave:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">SafeThread</span>(threading<span style="color: #666666">.</span>Thread):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, <span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs):
        <span style="color: #008000">super</span>(SafeThread, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>__init__(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>really_started <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Event()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">start</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>(SafeThread, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>start()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>really_started<span style="color: #666666">.</span>wait()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">run</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>really_started<span style="color: #666666">.</span>set()
        <span style="color: #008000">super</span>(SafeThread, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>run()
</pre></div>


<p>I create an <a href="http://docs.python.org/2/library/threading.html#event-objects">event</a> in the SafeThread's constructor. Then in SafeThread.start(), I call the standard Thread's start method, but I wait for the event before returning. Finally, I trigger the event in run(), which is executed in the new thread. By the time the standard Thread executes run(), it has added itself to <code>_active</code>: thus, we know it's safe to set the event and unblock the thread that called start(). Even if I fork immediately after that, the Safethread is in <code>_active</code> and can't become zombified.</p>
<p>You can imagine more complex scenarios that will still defeat me. For example, Thread A could start Thread B, and Thread C could fork at the wrong moment and leave Thread B zombified. For absolute safety from zombies, upgrade to Python 2.7.6 or 3.3.3 when they're released with my bugfix. Meanwhile, SafeThread is good enough for the common case where the main thread creates the background thread and then forks.</p>
<p>(Now read the gory finale, <a href="/blog/day-of-the-thread/">Day of the Thread</a>, in which humanity's last hope is to figure out the quirky code review system used by the Python Software Foundation.)</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="dawndead1.jpg" alt="Dawn of the Dead" title="Dawn of the Dead" /></p>
    