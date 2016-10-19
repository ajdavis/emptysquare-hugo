+++
type = "post"
title = "Night Of The Living Thread"
date = "2013-10-16T10:06:09"
description = "A fun series about a race condition I fixed in Python's threading implementation."
category = ["Programming", "Python"]
tag = ["threading"]
enable_lightbox = false
thumbnail = "bloodthirsty-lust@240.jpg"
draft = false
disqus_identifier = "525d892b539374035f7ebf09"
disqus_url = "https://emptysqua.re/blog/525d892b539374035f7ebf09/"
+++

<p>What should this Python code print?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread()
t<span style="color: #666666">.</span>start()
<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork() <span style="color: #666666">==</span> <span style="color: #666666">0</span>:
    <span style="color: #408080; font-style: italic"># We&#39;re in the child process.</span>
    <span style="color: #008000; font-weight: bold">print</span> t<span style="color: #666666">.</span>isAlive()
</pre></div>


<p>In Unix, only the thread that calls <code>fork()</code> is copied to the child process; all other threads are dead. So <code>t.isAlive()</code> in the child process should always return False. But <em>sometimes</em>, it returns True! It's the....</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="night-of-the-living-thread.jpg" alt="Night of the Living Thread" title="Night of the Living Thread" /></p>
<p>How did I discover this horrifying zombie thread? A project I work on, PyMongo, uses a background thread to monitor the state of the database server. If a user initializes PyMongo and then forks, the monitor is absent in the child. PyMongo should notice that the monitor thread's <code>isAlive</code> is False, and raise an error:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Starts monitor:</span>
client <span style="color: #666666">=</span> pymongo<span style="color: #666666">.</span>MongoReplicaSetClient()
os<span style="color: #666666">.</span>fork()

<span style="color: #408080; font-style: italic"># Should raise error, &quot;monitor is dead&quot;:</span>
client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find_one()
</pre></div>


<p>But intermittently, the monitor is still alive after the fork! It keeps coming back in a bloodthirsty lust for HUMAN FLESH!</p>
<p>I put on my Sixties scientist outfit (lab coat, thick-framed glasses) and sought the cause of this unnatural reanimation. To begin with, what does <code>Thread.isAlive()</code> do?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Thread</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">isAlive</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>__started<span style="color: #666666">.</span>is_set() <span style="color: #AA22FF; font-weight: bold">and</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>__stopped
</pre></div>


<p>After a fork, <code>__stopped</code> should be True on all threads but one. Whose job is it to set <code>__stopped</code> on all the threads that <em>didn't</em> call <code>fork()</code>? In <code>threading.py</code> I discovered the <code>_after_fork()</code> function, which I've simplified here:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Globals.</span>
_active <span style="color: #666666">=</span> {}
_limbo <span style="color: #666666">=</span> {}

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_after_fork</span>():
    <span style="color: #408080; font-style: italic"># This function is called by PyEval_ReInitThreads</span>
    <span style="color: #408080; font-style: italic"># which is called from PyOS_AfterFork.  Here we</span>
    <span style="color: #408080; font-style: italic"># clean up threading module state that should not</span>
    <span style="color: #408080; font-style: italic"># exist after a fork.</span>

    <span style="color: #408080; font-style: italic"># fork() only copied current thread; clear others.</span>
    new_active <span style="color: #666666">=</span> {}
    current <span style="color: #666666">=</span> current_thread()
    <span style="color: #008000; font-weight: bold">for</span> thread <span style="color: #AA22FF; font-weight: bold">in</span> _active<span style="color: #666666">.</span>itervalues():
        <span style="color: #008000; font-weight: bold">if</span> thread <span style="color: #AA22FF; font-weight: bold">is</span> current:
            <span style="color: #408080; font-style: italic"># There is only one active thread.</span>
            ident <span style="color: #666666">=</span> _get_ident()
            new_active[ident] <span style="color: #666666">=</span> thread
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #408080; font-style: italic"># All the others are already stopped.</span>
<span style="background-color: #ffffcc">            thread<span style="color: #666666">.</span>_Thread__stop()
</span>
    _limbo<span style="color: #666666">.</span>clear()
    _active<span style="color: #666666">.</span>clear()
    _active<span style="color: #666666">.</span>update(new_active)
    <span style="color: #008000; font-weight: bold">assert</span> <span style="color: #008000">len</span>(_active) <span style="color: #666666">==</span> <span style="color: #666666">1</span>
</pre></div>


<p>This function iterates all the Thread objects in a global dict called <code>_active</code>; each is removed and marked as "stopped", except for the current thread. How could this go wrong?</p>
<p><img style="display:block; margin-left:auto; margin-right:auto; border:1px solid black" src="night_of_the_living_dead_3.jpg" alt="Night of the living dead" title="Night of the living dead" /></p>
<p>Well, consider how a thread starts:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Thread</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">start</span>(<span style="color: #008000">self</span>):
        _limbo[<span style="color: #008000">self</span>] <span style="color: #666666">=</span> <span style="color: #008000">self</span>
        _start_new_thread(<span style="color: #008000">self</span><span style="color: #666666">.</span>__bootstrap)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__bootstrap</span>(<span style="color: #008000">self</span>):
<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>__started<span style="color: #666666">.</span>set()
</span><span style="background-color: #ffffcc">        _active[<span style="color: #008000">self</span><span style="color: #666666">.</span>__ident] <span style="color: #666666">=</span> <span style="color: #008000">self</span>
</span><span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">del</span> _limbo[<span style="color: #008000">self</span>]
</span>        <span style="color: #008000">self</span><span style="color: #666666">.</span>run()
</pre></div>


<p>(Again, I've simplified this.) The Thread object's <code>start</code> method adds the object to the <code>_limbo</code> list, then creates a new OS-level thread. The new thread, before it gets to work, marks itself as "started" and moves itself from <code>_limbo</code> to <code>_active</code>.</p>
<p>Do you see the bug now? Perhaps the thread was <a href="http://en.wikipedia.org/wiki/Night_of_the_living_dead#Plot_summary">reanimated by space rays from Venus</a> and craves the flesh of the living!</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="night_of_the_living_dead_4.jpg" alt="Night of the living dead 4" title="Night of the living dead 4" /></p>
<p>Or perhaps there's a race condition:</p>
<ol>
<li>Main thread calls worker's <code>start()</code>.</li>
<li>Worker calls <code>self.__started.set()</code>, but is interrupted before it adds itself to <code>_active</code>.</li>
<li>Main thread calls <code>fork()</code>.</li>
<li>In child process, main thread calls <code>_after_fork</code>, which doesn't find the worker in <code>_active</code> and doesn't mark it "stopped".</li>
<li><code>isAlive()</code> now returns True because the worker is started and not stopped.</li>
</ol>
<p><br />
Now we know the cause of the grotesque revenant. What's the cure? Headshot?</p>
<p>I <a href="http://bugs.python.org/issue18418">submitted a patch to Python</a> that simply swapped the order of operations: first the thread adds itself to <code>_active</code>, then it marks itself started:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__bootstrap</span>(<span style="color: #008000">self</span>):
<span style="background-color: #ffffcc">    _active[<span style="color: #008000">self</span><span style="color: #666666">.</span>__ident] <span style="color: #666666">=</span> <span style="color: #008000">self</span>
</span><span style="background-color: #ffffcc">    <span style="color: #008000">self</span><span style="color: #666666">.</span>__started<span style="color: #666666">.</span>set()
</span>    <span style="color: #008000">self</span><span style="color: #666666">.</span>run()
</pre></div>


<p>If the thread is interrupted by a fork after adding itself to <code>_active</code>, then <code>_after_fork()</code> finds it there and marks it stopped. The thread ends up stopped but not started, rather than the reverse. In this case <code>isAlive()</code> correctly returns False.</p>
<p>The Python core team looked at my patch, and Charles-Fran&ccedil;ois Natali suggested a cleaner fix. If the zombie thread is not yet in <code>_active</code>, it <em>is</em> in the global <code>_limbo</code> list. So <code>_after_fork</code> should iterate over both <code>_limbo</code> and <code>_active</code>, instead of just <code>_active</code>. Then it will mark the zombie thread as "stopped" along with the other threads.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_enumerate</span>():
    <span style="color: #008000; font-weight: bold">return</span> _active<span style="color: #666666">.</span>values() <span style="color: #666666">+</span> _limbo<span style="color: #666666">.</span>values()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_after_fork</span>():
    new_active <span style="color: #666666">=</span> {}
    current <span style="color: #666666">=</span> current_thread()
<span style="background-color: #ffffcc">    <span style="color: #008000; font-weight: bold">for</span> thread <span style="color: #AA22FF; font-weight: bold">in</span> _enumerate():
</span>        <span style="color: #008000; font-weight: bold">if</span> thread <span style="color: #AA22FF; font-weight: bold">is</span> current:
            <span style="color: #408080; font-style: italic"># There is only one active thread.</span>
            ident <span style="color: #666666">=</span> _get_ident()
            new_active[ident] <span style="color: #666666">=</span> thread
        <span style="color: #008000; font-weight: bold">else</span>:
            <span style="color: #408080; font-style: italic"># All the others are already stopped.</span>
            thread<span style="color: #666666">.</span>_Thread__stop()
</pre></div>


<p>This fix will be included in the next Python 2.7 and 3.3 releases. The zombie threads will stay good and dead...for now!</p>
<p>(Now read the sequels: <a href="/blog/dawn-of-the-thread/">Dawn of the Thread</a>, in which I battle zombie threads in the abandoned tunnels of Python 2.6; and <a href="/blog/day-of-the-thread/">Day of the Thread</a>, a post-apocalyptic thriller in which a lone human survivor tries to get a patch accepted via bugs.python.org.)</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="bloodthirsty-lust.jpg" alt="They keep coming back in a bloodthirsty lust for human flesh!" title="They keep coming back in a bloodthirsty lust for human flesh!" /></p>
