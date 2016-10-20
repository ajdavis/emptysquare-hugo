+++
type = "post"
title = "Knowing When A Python Thread Has Died"
date = "2013-01-26T17:17:32"
description = "Sometimes thread.join() isn't enough."
category = ["Programming", "Python"]
tag = ["threading"]
enable_lightbox = false
thumbnail = "Andrea_Previtali-portrait-of-a-man.jpg"
draft = false
disqus_identifier = "51043af95393747dd209a86b"
disqus_url = "https://emptysqua.re/blog/51043af95393747dd209a86b/"
+++

<p><a href="http://commons.wikimedia.org/wiki/File:Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG"><img style="display:block; margin-left:auto; margin-right:auto;" src="Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG" alt="Young Woman Contemplating a Skull by Alessandro Casolani Statens Museum for Kunst DSC08131" title="Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG" border="0"   />
</a></p>
<p>A few months ago I had to solve a problem in PyMongo that is harder than it seems: how do you register for notifications when the current thread has died?</p>
<p>The circumstances are these: when you call <a href="http://api.mongodb.org/python/2.8/examples/requests.html"><code>start_request</code></a> in PyMongo, it gets a socket from its pool and assigns the socket to the current thread. We need some way to know when the current thread dies so we can reclaim the socket and return it to the socket pool for future use, rather than wastefully allowing it to be closed.</p>
<p>PyMongo can assume nothing about what kind of thread this is: It could've been started from the <code>threading</code> module, or the more primitive <code>thread</code> module, or it could've been started outside Python entirely, in C, as when PyMongo is running under mod_wsgi.</p>
<p>Here's what I came up with:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">threading</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">weakref</span>

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">ThreadWatcher</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Vigil</span>(<span style="color: #008000">object</span>):
        <span style="color: #008000; font-weight: bold">pass</span>

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>_refs <span style="color: #666666">=</span> {}
        <span style="color: #008000">self</span><span style="color: #666666">.</span>_local <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>local()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">_on_death</span>(<span style="color: #008000">self</span>, vigil_id, callback, ref):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>_refs<span style="color: #666666">.</span>pop(vigil_id)
        callback()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">watch</span>(<span style="color: #008000">self</span>, callback):
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>is_watching():
<span style="background-color: #ffffcc">            <span style="color: #008000">self</span><span style="color: #666666">.</span>_local<span style="color: #666666">.</span>vigil <span style="color: #666666">=</span> v <span style="color: #666666">=</span> ThreadWatcher<span style="color: #666666">.</span>Vigil()
</span><span style="background-color: #ffffcc">            on_death <span style="color: #666666">=</span> partial(
</span><span style="background-color: #ffffcc">                <span style="color: #008000">self</span><span style="color: #666666">.</span>_on_death, <span style="color: #008000">id</span>(v), callback)
</span><span style="background-color: #ffffcc">
</span><span style="background-color: #ffffcc">            ref <span style="color: #666666">=</span> weakref<span style="color: #666666">.</span>ref(v, on_death)
</span><span style="background-color: #ffffcc">            <span style="color: #008000">self</span><span style="color: #666666">.</span>_refs[<span style="color: #008000">id</span>(v)] <span style="color: #666666">=</span> ref
</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">is_watching</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121">&quot;Is the current thread being watched?&quot;</span>
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">hasattr</span>(<span style="color: #008000">self</span><span style="color: #666666">.</span>_local, <span style="color: #BA2121">&#39;vigil&#39;</span>)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">unwatch</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">try</span>:
            v <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_local<span style="color: #666666">.</span>vigil
            <span style="color: #008000; font-weight: bold">del</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_local<span style="color: #666666">.</span>vigil
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_refs<span style="color: #666666">.</span>pop(<span style="color: #008000">id</span>(v))
        <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">AttributeError</span>:
            <span style="color: #008000; font-weight: bold">pass</span>
</pre></div>


<p>The key lines are highlighted, in <code>watch()</code>. First, I make a <a href="http://docs.python.org/2/library/weakref.html#weakref.ref">weakref</a> to a thread local. Weakrefs are permitted on subclasses of <code>object</code> but not <code>object</code> itself, so I use an inner class called Vigil. I initialize the weakref with a callback, which will be executed when the vigil is deleted.</p>
<p>The callback only fires if the weakref outlives the vigil, so I keep the weakref alive by storing it as a value in the <code>_refs</code> dict. The key into <code>_refs</code> can't be the vigil itself, since then the vigil would have a strong reference and wouldn't be deleted when the thread dies. I use <code>id(key)</code> instead.</p>
<p>Let's step through this. When a thread calls <code>watch()</code>, the only strong reference to the vigil is a thread-local. When a thread dies its locals are cleaned up, the vigil is dereferenced, and <code>_on_death</code> runs. <code>_on_death</code> cleans up <code>_refs</code> and then voil&agrave;, it runs the original callback.</p>
<p>When exactly is the vigil deleted? This is a subtle point, as the sages among you know. First, PyPy uses occasional <a href="http://doc.pypy.org/en/latest/gc_info.html">mark and sweep garbage collection</a> instead of reference-counting, so the vigil isn't deleted until some time after the thread dies. In unittests, I force the issue with <code>gc.collect()</code>.</p>
<p>Second, there's a <a href="http://bugs.python.org/issue1868">bug in CPython 2.6</a> and earlier, fixed by Antoine Pitrou in CPython 2.7.1, where thread locals aren't cleaned up until the thread dies <em>and</em> some other thread accesses the local. I <a href="/pythons-thread-locals-are-weird/">wrote about this in detail</a> last year when I was struggling with it. <code>gc.collect()</code> won't help in this case.</p>
<p>Thirdly, when is the local cleaned up in Python 2.7.1 and later? It happens as soon as the interpreter deletes the underlying <code>PyThreadState</code>, but that can actually come <em>after</em> <code>Thread.join()</code> returns&mdash;<code>join()</code> is simply waiting for a <a href="http://docs.python.org/2/library/threading.html#condition-objects">Condition</a> to be set at the end of the thread's run, which comes before the locals are cleared. So in Python 2.7.1 we need to sleep a few milliseconds after joining the thread to be certain it's truly gone.</p>
<p>Thus a reliable test for my ThreadWatcher class might look like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">TestWatch</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_watch</span>(<span style="color: #008000">self</span>):
        watcher <span style="color: #666666">=</span> ThreadWatcher()
        callback_ran <span style="color: #666666">=</span> [<span style="color: #008000">False</span>]

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>():
            callback_ran[<span style="color: #666666">0</span>] <span style="color: #666666">=</span> <span style="color: #008000">True</span>

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">target</span>():
            watcher<span style="color: #666666">.</span>watch(callback)

        t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>target)
        t<span style="color: #666666">.</span>start()
        t<span style="color: #666666">.</span>join()

        <span style="color: #408080; font-style: italic"># Trigger collection in Py 2.6</span>
        <span style="color: #408080; font-style: italic"># See http://bugs.python.org/issue1868</span>
<span style="background-color: #ffffcc">        watcher<span style="color: #666666">.</span>is_watching()
</span><span style="background-color: #ffffcc">        gc<span style="color: #666666">.</span>collect()
</span>
        <span style="color: #408080; font-style: italic"># Cleanup can take a few ms in</span>
        <span style="color: #408080; font-style: italic"># Python &gt;= 2.7</span>
<span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">for</span> _ <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10</span>):
</span><span style="background-color: #ffffcc">            <span style="color: #008000; font-weight: bold">if</span> callback_ran[<span style="color: #666666">0</span>]:
</span><span style="background-color: #ffffcc">                <span style="color: #008000; font-weight: bold">break</span>
</span><span style="background-color: #ffffcc">            <span style="color: #008000; font-weight: bold">else</span>:
</span><span style="background-color: #ffffcc">                time<span style="color: #666666">.</span>sleep(<span style="color: #666666">.1</span>)
</span>

        <span style="color: #008000; font-weight: bold">assert</span> callback_ran[<span style="color: #666666">0</span>]
        <span style="color: #408080; font-style: italic"># id(v) removed from _refs?</span>
        <span style="color: #008000; font-weight: bold">assert</span> <span style="color: #AA22FF; font-weight: bold">not</span> watcher<span style="color: #666666">.</span>_refs
</pre></div>


<p>The <code>is_watching()</code> call accesses the local object from the main thread after the child has died, working around the Python 2.6 bug, and the <code>gc.collect()</code> call makes the test pass in PyPy. The sleep loop gives Python 2.7.1 a chance to finish tearing down the thread state, including locals.</p>
<p>Two final cautions. The first is, you can't predict which thread runs the callback. In Python 2.6 it's whichever thread accesses the local <em>after</em> the child dies. In later versions, with Pitrou's improved thread-local implementation, the callback is run on the dying child thread. In PyPy it's whichever thread is active when the garbage collector decides to run.</p>
<p>The second caution is, there's an unreported memory-leak bug in Python 2.6, which Pitrou fixed in Python 2.7.1 along with the other bug I linked to. If you access a thread-local from <em>within</em> the weakref callback, you're touching the local in an inconsistent state, and the <em>next</em> object stored in the local will never be dereferenced. So don't do that. Here's a demonstration:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">TestRefLeak</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_leak</span>(<span style="color: #008000">self</span>):
        watcher <span style="color: #666666">=</span> ThreadWatcher()
        n_callbacks <span style="color: #666666">=</span> [<span style="color: #666666">0</span>]
        nthreads <span style="color: #666666">=</span> <span style="color: #666666">10</span>

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>():
            <span style="color: #408080; font-style: italic"># BAD, NO!:</span>
            <span style="color: #408080; font-style: italic"># Accessing thread-local in callback</span>
<span style="background-color: #ffffcc">            watcher<span style="color: #666666">.</span>is_watching()
</span>            n_callbacks[<span style="color: #666666">0</span>] <span style="color: #666666">+=</span> <span style="color: #666666">1</span>

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">target</span>():
            watcher<span style="color: #666666">.</span>watch(callback)

        <span style="color: #008000; font-weight: bold">for</span> _ <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(nthreads):
            t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>target)
            t<span style="color: #666666">.</span>start()
            t<span style="color: #666666">.</span>join()

        watcher<span style="color: #666666">.</span>is_watching()
        gc<span style="color: #666666">.</span>collect()
        <span style="color: #008000; font-weight: bold">for</span> _ <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10</span>):
            <span style="color: #008000; font-weight: bold">if</span> n_callbacks[<span style="color: #666666">0</span>] <span style="color: #666666">==</span> nthreads:
                <span style="color: #008000; font-weight: bold">break</span>
            <span style="color: #008000; font-weight: bold">else</span>:
                time<span style="color: #666666">.</span>sleep(<span style="color: #666666">.1</span>)

<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(nthreads, n_callbacks[<span style="color: #666666">0</span>])
</span></pre></div>


<p>In Python 2.7.1 and later the test passes because all ten threads' locals are cleaned up, and the callback runs ten times. But in Python 2.6 only five locals are deleted.</p>
<p>I discovered this bug when I rewrote the connection pool in PyMongo 2.2 and a user reported that in Python 2.6 and mod_wsgi, every <em>second</em> request leaked one socket! I fixed PyMongo in version 2.2.1 by avoiding accessing thread locals while they're being torn down. (See bug <a href="https://jira.mongodb.org/browse/PYTHON-353">PYTHON-353</a>.)</p>
<p><strong>Update:</strong> I've discovered that in Python 2.7.0 and earlier, you need to lock around the assignment to <code>self._local.vigil</code>, see <a href="/another-thing-about-pythons-threadlocals/">"Another Thing About Threadlocals"</a>.</p>
<p>For further reading:</p>
<ul>
<li><a href="https://gist.github.com/4644641">My whole gist for ThreadWatcher and its tests</a></li>
<li><a href="http://bugs.python.org/issue1868">Pitrou's new thread-local implementation for Python 2.7.1</a></li>
<li><a href="https://github.com/mongodb/mongo-python-driver/blob/master/pymongo/thread_util.py">PyMongo's thread utilities</a></li>
</ul>
<hr />
<p>Post-script: The image up top is a <a href="http://en.wikipedia.org/wiki/Memento_mori">memento mori</a>, a "reminder you will die," by Alessandro Casolani from the 16th Century. The memento mori genre is intended to offset a portrait subject's vanity&mdash;you look good now, but your beauty won't make a difference when you face your final judgment.</p>
<p>This was painted circa 1502 by Andrea Previtali:</p>
<p><a href="http://commons.wikimedia.org/wiki/File:Andrea_Previtali_-_Memento_Mori_%28verso%29_-_WGA18406.jpg"><img style="display:block; margin-left:auto; margin-right:auto;" src="Andrea_Previtali_Memento_Mori_WGA18406.jpg" alt="Andrea Previtali Memento Mori WGA18406" title="Andrea_Previtali_Memento_Mori_WGA18406.jpg" border="0"   /></a></p>
<p>The inscription is "Hic decor hec forma manet, hec lex omnibus unam," which my Latin-nerd friends translate as, "This beauty endures only in this form, this law is the same for everyone." It was painted upside-down on the back of this handsome guy:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Andrea_Previtali-portrait-of-a-man.jpg" alt="Andrea Previtali portrait of a man" title="Andrea_Previtali-portrait-of-a-man.jpg" border="0"   /></p>
<p>The painting was mounted on an axle so the face and the skull could be rapidly alternated and compared. Think about that the next time you start a thread&mdash;it may be running now, but soon enough it will terminate and even its thread-id will be recycled.</p>
