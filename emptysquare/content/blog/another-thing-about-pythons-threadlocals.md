+++
type = "post"
title = "Another Thing About Python's Threadlocals"
date = "2013-04-25T22:24:16"
description = "Another concurrency bug in old Python threadlocals. In Python 2.6, no one can hear you scream."
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "dammit@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="dammit.jpg" alt="Dammit" title="dammit.jpg" border="0"   /></p>
<p>As the maintainer of the connection pool for PyMongo, the official MongoDB driver for Python, I've gotten far more intimate knowledge of Python threads than I'd ever wanted.</p>
<p>One of the challenges I face is: if the connection pool assigns a socket to a thread and the thread dies, how do we reclaim the socket for the general pool? I thought I nailed it last year, using a weakref callback to a threadlocal, but there's a bug in that method. <a href="https://twitter.com/papercrane">Justin Patrin</a> of Idle Games discovered it while testing a PyMongo contribution he's making. I'm going to describe the bug, its impact, the cause, and the fix. I'll conclude by kvetching about supporting archaic versions of Python.</p>
<h1 id="the-bug">The Bug</h1>
<p>Here's some code to start 1000 threads and register to be notified when they're kaput. At the end I assert no thread has died unmourned:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">threading</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">weakref</span>

nthreads <span style="color: #666666">=</span> <span style="color: #666666">1000</span>
ncallbacks <span style="color: #666666">=</span> <span style="color: #666666">0</span>
ncallbacks_lock <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Lock()
local <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>local()
refs <span style="color: #666666">=</span> <span style="color: #008000">set</span>()

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Vigil</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">pass</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">run</span>():
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">on_thread_died</span>(ref):
        <span style="color: #008000; font-weight: bold">global</span> ncallbacks
        ncallbacks_lock<span style="color: #666666">.</span>acquire()
        ncallbacks <span style="color: #666666">+=</span> <span style="color: #666666">1</span>
        ncallbacks_lock<span style="color: #666666">.</span>release()

    vigil <span style="color: #666666">=</span> Vigil()
    local<span style="color: #666666">.</span>vigil <span style="color: #666666">=</span> vigil
    refs<span style="color: #666666">.</span>add(weakref<span style="color: #666666">.</span>ref(vigil, on_thread_died))

threads <span style="color: #666666">=</span> [threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>run)
           <span style="color: #008000; font-weight: bold">for</span> _ <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(nthreads)]
<span style="color: #008000; font-weight: bold">for</span> t <span style="color: #AA22FF; font-weight: bold">in</span> threads: t<span style="color: #666666">.</span>start()
<span style="color: #008000; font-weight: bold">for</span> t <span style="color: #AA22FF; font-weight: bold">in</span> threads: t<span style="color: #666666">.</span>join()
<span style="color: #008000">getattr</span>(local, <span style="color: #BA2121">&#39;c&#39;</span>, <span style="color: #008000">None</span>)  <span style="color: #408080; font-style: italic"># Trigger cleanup in &lt;= 2.7.0</span>
<span style="color: #008000; font-weight: bold">assert</span> ncallbacks <span style="color: #666666">==</span> nthreads, \
    <span style="color: #BA2121">&#39;only </span><span style="color: #BB6688; font-weight: bold">%d</span><span style="color: #BA2121"> callbacks run&#39;</span> <span style="color: #666666">%</span> ncallbacks
</pre></div>


<p>This is the method I presented in <a href="/blog/knowing-when-a-python-thread-has-died/">"Knowing When A Python Thread Has Died"</a>. Each thread creates a "vigil" object and sticks it in a threadlocal. Since only the threadlocal refers to the vigil, the vigil should be destroyed when the thread dies. I make a weakref to the vigil and register a <a href="http://docs.python.org/2/library/weakref.html#weakref.ref">weakref callback</a>. If all goes well, the callback is run as the thread dies. A quirk of Python 2.7.0 or lesser is that the callback is run when the <strong>next</strong> thread accesses the threadlocal. This oddity is a consequence of <a href="http://bugs.python.org/issue1868">Python Issue 1868</a>, fixed by Antoine Pitrou in late 2010 and released in Python 2.7.1.</p>
<p>Note also that I synchronize <code>ncallbacks += 1</code> with a mutex, since <code>+=</code> <a href="/blog/python-increment-is-weird/">is not atomic in Python</a>. This innocent-looking mutex harbors a dark intent, as we shall soon discover.</p>
<p>In Python 2.7.1 and newer, the code above works as expected: <code>ncallbacks</code> is equal to 1000 immediately after all the threads are joined. In Python 2.7.0, <code>ncallbacks</code> should be 999 after the threads are joined, and then 1000 after the main thread does the final <code>getattr</code> to trigger cleanup.</p>
<p>The bug is: In Python 2.7.0 and older, <code>ncallbacks</code> is sometimes a few callbacks shy of a thousand. A few threads have been buried in unmarked graves....</p>
<h1 id="its-impact">Its Impact</h1>
<p>I found that an application running Python 2.7.0 or older, if it creates and destroys very large numbers of threads continuously for a long time, and if each thread calls <a href="http://api.mongodb.org/python/2.8/examples/requests.html"><code>end_request</code></a> at least once and <code>start_request</code> more times than <code>end_request</code>, will occasionally leave a socket tied to a dead thread. These sockets will eventually exceed the process's ulimit or MongoDB's.</p>
<p>This application pattern would be as weird and unusual as it sounds, which is why no one's complained of the bug.</p>
<h1 id="the-fix">The Fix</h1>
<p>Once I'd written the test code above, I spent a few hours futzing with it&mdash;Dammit, I thought this worked! I tried various techniques to force Python 2.7.0 to run the callback a thousand times reliably. Late in the day a divine voice intoned, "synchronize assignment to the threadlocal." So I added a lock:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">local_lock = threading.Lock()
# ...
    vigil = Vigil()
    local_lock.acquire()
    local.vigil = vigil
    local_lock.release()
    refs.add(weakref.ref(vigil, on_thread_died))
</pre></div>


<p>It worked! Now I was angrier. How can <em>assigning</em> to a threadlocal not be thread-safe?</p>
<h1 id="the-cause">The Cause</h1>
<p>Let's again consider the example code above. The bytecode for assigning <code>vigil</code> to <code>local.vigil</code> is:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">28 LOAD_FAST        1 (vigil)
31 LOAD_GLOBAL      3 (local)
34 STORE_ATTR       4 (vigil)
</pre></div>


<p><code>STORE_ATTR</code> calls <code>PyObject_SetAttr</code>, which calls <code>local_setattro</code>, defined in Modules/threadmodule.c:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">static <span style="color: #008000">int</span>
local_setattro(localobject <span style="color: #666666">*</span><span style="color: #008000">self</span>, PyObject <span style="color: #666666">*</span>name, PyObject <span style="color: #666666">*</span>v)
{
    PyObject <span style="color: #666666">*</span>ldict;

<span style="background-color: #ffffcc">    ldict <span style="color: #666666">=</span> _ldict(<span style="color: #008000">self</span>);
</span>    <span style="color: #008000; font-weight: bold">if</span> (ldict <span style="color: #666666">==</span> NULL)
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #666666">-1</span>;

    <span style="color: #008000; font-weight: bold">return</span> PyObject_GenericSetAttr((PyObject <span style="color: #666666">*</span>)<span style="color: #008000">self</span>, name, v);
}
</pre></div>


<p>At the highlighted line it calls <code>_ldict</code>. The <code>_ldict</code> function is, as I've known for some time, a pathetic piece of poo in Python 2.7.0 and older. Here's the turd, edited down a bit:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">static PyObject <span style="color: #666666">*</span>
_ldict(localobject <span style="color: #666666">*</span><span style="color: #008000">self</span>)
{
    PyObject <span style="color: #666666">*</span>tdict, <span style="color: #666666">*</span>ldict;

    tdict <span style="color: #666666">=</span> PyThreadState_GetDict();
    ldict <span style="color: #666666">=</span> PyDict_GetItem(tdict, <span style="color: #008000">self</span><span style="color: #666666">-&gt;</span>key);
    <span style="color: #008000; font-weight: bold">if</span> (ldict <span style="color: #666666">==</span> NULL) {
        ldict <span style="color: #666666">=</span> PyDict_New(); <span style="color: #666666">/*</span> we own ldict <span style="color: #666666">*/</span>

        PyDict_SetItem(tdict, <span style="color: #008000">self</span><span style="color: #666666">-&gt;</span>key, ldict);
        Py_DECREF(ldict); <span style="color: #666666">/*</span> now ldict <span style="color: #AA22FF; font-weight: bold">is</span> borrowed <span style="color: #666666">*/</span>
        <span style="color: #008000; font-weight: bold">if</span> (i <span style="color: #666666">&lt;</span> <span style="color: #666666">0</span>)
            <span style="color: #008000; font-weight: bold">return</span> NULL;

<span style="background-color: #ffffcc">        Py_CLEAR(<span style="color: #008000">self</span><span style="color: #666666">-&gt;</span><span style="color: #008000">dict</span>);
</span>        Py_INCREF(ldict);
        <span style="color: #008000">self</span><span style="color: #666666">-&gt;</span><span style="color: #008000">dict</span> <span style="color: #666666">=</span> ldict; <span style="color: #666666">/*</span> still borrowed <span style="color: #666666">*/</span>
    }

    <span style="color: #666666">/*</span> The call to tp_init above may have caused
       another thread to run<span style="color: #666666">.</span>
       Install our ldict again<span style="color: #666666">.</span> <span style="color: #666666">*/</span>
    <span style="color: #008000; font-weight: bold">if</span> (<span style="color: #008000">self</span><span style="color: #666666">-&gt;</span><span style="color: #008000">dict</span> <span style="color: #666666">!=</span> ldict) {
        Py_CLEAR(<span style="color: #008000">self</span><span style="color: #666666">-&gt;</span><span style="color: #008000">dict</span>);
        Py_INCREF(ldict);
        <span style="color: #008000">self</span><span style="color: #666666">-&gt;</span><span style="color: #008000">dict</span> <span style="color: #666666">=</span> ldict;
    }

    <span style="color: #008000; font-weight: bold">return</span> ldict;
}
</pre></div>


<p>We haven't seen any use of the <code>Py_BEGIN_ALLOW_THREADS</code> macro, so one thread's had the GIL the whole time. Locking around the assignment shouldn't have any effect, right?</p>
<p>Well, take a look at the highlighted <code>Py_CLEAR(self-&gt;dict)</code> statement&mdash;there's the perpetrator. That statement gets the <code>ldict</code> of the last thread that accessed this threadlocal, swaps it with NULL and decrefs it. If this is the last reference to <code>ldict</code> (because the last thread has died) then decref'ing destroys it, and the weakref callback to <code>vigil</code> runs. The callback does <code>ncallbacks_lock.acquire</code>, which releases the GIL before trying to get the mutex.</p>
<p>So here's the kind of scenario I prevented by locking around assignment to the threadlocal:</p>
<ol>
<li>Thread A starts, assigns to the threadlocal, dies.</li>
<li>Thread A's <code>ldict</code> is now the threadlocal's <code>self-&gt;dict</code> and has a refcount of 1.</li>
<li>Thread B starts, begins assigning to the threadlocal, enters the <code>_ldict</code> function.</li>
<li><code>_ldict</code> sets <code>self-&gt;dict</code> to NULL and decrefs Thread A's <code>ldict</code>, which runs <code>on_thread_died</code>, which calls <code>ncallbacks_lock.acquire</code> and releases the GIL.</li>
<li>Now Thread C starts, begins assigning to the threadlocal, enters <code>_ldict</code>.</li>
<li>Thread C finds <code>self-&gt;dict</code> is NULL, increfs its own local <code>ldict</code> and assigns it to <code>self-&gt;dict</code>. It exits <code>_ldict</code>.</li>
<li>Thread B resumes at <code>Py_CLEAR(self-&gt;dict)</code>, increfs its own <code>ldict</code> and assigns it to <code>self-&gt;dict</code>.</li>
</ol>
<p>Thread B has now replaced a pointer to Thread C's <code>ldict</code> with a pointer to its own, but it didn't decref Thread C's <code>ldict</code> first. (<code>_ldict</code> wasn't written to survive interruption during <code>Py_CLEAR</code>.) Thread C's <code>ldict</code> will never be destroyed, and a weakref callback to its <code>vigil</code> attribute will never be called.</p>
<p>Locking around assignment to the threadlocal prevents <code>_ldict</code> from running concurrently for any one threadlocal object, and prevents the refleak. In Python 2.7.1 and newer, the whole misguided <code>self-&gt;dict</code> system is removed from threadlocals and the lock's not needed.</p>
<p>This scenario applies to PyMongo's connection pool because the pool <strong>does</strong> need to acquire a lock in its weakref callback. Even if it didn't, there's a possibility of interruption whenever a thread is running Python code.</p>
<h1 id="a-kvetch">A Kvetch<a id="scream"></a></h1>
<p>This testing, the bug it revealed, the investigation, the fix: all this effort was spent to support entirely obsolete versions of Python. The Python core developers stopped maintaining them years ago, but PyMongo supports all Pythons going back to 2.4, mainly because there are "long-term support" Linux distros like Ubuntu and RHEL that once shipped with them. I have very savvy friends writing <strong>new</strong> applications on Python 2.6. Our children will have flying cars before we're done debugging these steam-powered versions of Python.</p>
<p>It's particularly frustrating because there's no point even filing bugs against Pythons before 2.7. "We fixed it," the developers will reply. "Upgrade." In Python 2.6, no one can hear you scream.</p>
    