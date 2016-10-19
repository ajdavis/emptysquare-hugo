+++
type = "post"
title = "Python's Thread Locals Are Weird"
date = "2012-05-27T16:46:58"
description = ""
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "new-python-thread-local-architecture@240.png"
draft = false
disqus_identifier = "564 http://emptysquare.net/blog/?p=564"
disqus_url = "https://emptysqua.re/blog/564 http://emptysquare.net/blog/?p=564/"
+++

<h1 id="the-weirdness">The Weirdness</h1>
<p>What do you think this script prints?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">thread</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">threading</span><span style="color: #666666">,</span> <span style="color: #0000FF; font-weight: bold">sys</span>

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Weeper</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__del__</span>(<span style="color: #008000">self</span>):
        sys<span style="color: #666666">.</span>stdout<span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;oh cruel world </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> thread<span style="color: #666666">.</span>get_ident())

local <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>local()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">target</span>():
    local<span style="color: #666666">.</span>weeper <span style="color: #666666">=</span> Weeper()

t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>target)
t<span style="color: #666666">.</span>start()
t<span style="color: #666666">.</span>join()
sys<span style="color: #666666">.</span>stdout<span style="color: #666666">.</span>write(<span style="color: #BA2121">&#39;done </span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&#39;</span> <span style="color: #666666">%</span> thread<span style="color: #666666">.</span>get_ident())
<span style="color: #008000">getattr</span>(local, <span style="color: #BA2121">&#39;whatever&#39;</span>, <span style="color: #008000">None</span>)
</pre></div>


<p>If you guessed something like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">oh cruel world 4475731968
done 140735297751392
</pre></div>


<p>...then you'd be right, <em>in Python after 2.7.1</em>. In Python 2.7.0 and
older (including the whole 2.6 series), the order of messages is reversed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">done 140735297751392
oh cruel world 140735297751392
</pre></div>


<p>In New Python, the Weeper is deleted as soon as its thread dies, and
__del__ runs on the dying thread. In Old Python, the Weeper isn't
deleted until the thread is dead <strong>and</strong> a different thread accesses the
local's __dict__. Thus the Weeper is deleted at the line
<code>getattr(local, 'whatever', None)</code>, after the thread dies, and
Weeper.__del__ runs on the main thread.</p>
<p>What if we remove the <code>getattr</code> call? In Old Python, this happens:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">done 140735297751392
Exception AttributeError: &quot;&#39;NoneType&#39; object has no attribute &#39;get_ident&#39;&quot;
    in &lt;bound method Weeper.__del__ of &lt;__main__.Weeper object at 0x104f95590&gt;&gt;
    ignored
</pre></div>


<p>Without <code>getattr</code>, the Weeper isn't deleted until interpreter shutdown.
The shutdown sequence is complex and hard to predict—in this case the
<code>thread</code> module has been set to <code>None</code> before the Weeper is deleted, so
Weeper.__del__ can't do <code>thread.get_ident()</code>.</p>
<h1 id="thread-locals-in-old-python">Thread Locals in Old Python</h1>
<p>To understand why locals act this way in Old Python, let's
look at the implementation in C. The core interpreter's <code>PyThreadState</code>
struct has a <code>dict</code> attribute, and each <code>threading.local</code> object has a
<code>key</code> attribute formatted like
<code>"thread.local.&lt;memory address of self&gt;"</code>. Each local has a <code>__dict__</code>
of attributes per thread, stored in <code>PyThreadState</code>'s <code>dict</code> with the
local's key.</p>
<p>threadmodule.c includes a function <code>_ldict(localobject *self)</code> which
takes a local and finds its <code>__dict__</code> for the current thread.
<code>_ldict()</code> finds and returns the local's <code>__dict__</code> for this thread,
<strong>and</strong> stores it in <code>self-&gt;dict</code>.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="old-python-thread-local-architecture.png" title="Old Python's thread-local architecture" /></p>
<p>This architecture has, in my opinion, a bug. Here's the implementation
of <code>_ldict()</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject <span style="color: #666666">*</span> <span style="color: #0000FF">_ldict</span>(localobject <span style="color: #666666">*</span>self)
{
    PyObject <span style="color: #666666">*</span>tdict <span style="color: #666666">=</span> PyThreadState_GetDict(); <span style="color: #408080; font-style: italic">// get PyThreadState-&gt;dict for this thread</span>
    PyObject <span style="color: #666666">*</span>ldict <span style="color: #666666">=</span> PyDict_GetItem(tdict, self<span style="color: #666666">-&gt;</span>key);
    <span style="color: #008000; font-weight: bold">if</span> (ldict <span style="color: #666666">==</span> <span style="color: #008000">NULL</span>) {
        ldict <span style="color: #666666">=</span> PyDict_New(); <span style="color: #408080; font-style: italic">/* we own ldict */</span>
        PyDict_SetItem(tdict, self<span style="color: #666666">-&gt;</span>key, ldict);
<span style="background-color: #ffffcc">        Py_CLEAR(self<span style="color: #666666">-&gt;</span>dict);
</span>        Py_INCREF(ldict);
        self<span style="color: #666666">-&gt;</span>dict <span style="color: #666666">=</span> ldict; <span style="color: #408080; font-style: italic">/* still borrowed */</span>

<span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">if</span> (Py_TYPE(self)<span style="color: #666666">-&gt;</span>tp_init <span style="color: #666666">!=</span> PyBaseObject_Type.tp_init) {
</span><span style="background-color: #ffffcc">            Py_TYPE(self)<span style="color: #666666">-&gt;</span>tp_init((PyObject<span style="color: #666666">*</span>)self, self<span style="color: #666666">-&gt;</span>args, self<span style="color: #666666">-&gt;</span>kw);
</span>        }
    }

    <span style="color: #408080; font-style: italic">/* The call to tp_init above may have caused another thread to run.</span>
<span style="color: #408080; font-style: italic">       Install our ldict again. */</span>
    <span style="color: #008000; font-weight: bold">if</span> (self<span style="color: #666666">-&gt;</span>dict <span style="color: #666666">!=</span> ldict) {
<span style="background-color: #ffffcc">        Py_CLEAR(self<span style="color: #666666">-&gt;</span>dict);
</span>        Py_INCREF(ldict);
        self<span style="color: #666666">-&gt;</span>dict <span style="color: #666666">=</span> ldict;
    }

    <span style="color: #008000; font-weight: bold">return</span> ldict;
}
</pre></div>


<p>I've edited for brevity. There's a few interesting things here—one is
the check for a custom <code>__init__</code> method. If this object is a subclass
of local which overrides <code>__init__</code>, then <code>__init__</code> is called whenever
a new thread accesses this local's attributes for the first time.</p>
<p>But the main thing I'm showing you is the two calls to
<code>Py_CLEAR(self-&gt;dict)</code>, which decrements <code>self-&gt;dict</code>'s refcount. It's
called when a thread accesses this local's attributes for the first
time, <strong>or</strong> if this thread is accessing the local's attributes after a
different thread has accessed them—that is, if <code>self-&gt;dict != ldict</code>.</p>
<p>So now we clearly understand why a thread's locals aren't deleted
immediately after it dies:</p>
<ol>
<li>The worker thread stores a Weeper in <code>local.weeper</code>. <code>_ldict()</code>
    creates a new <code>__dict__</code> for this thread and stores it as a value in
    <code>PyThreadState-&gt;dict</code>, <strong>and</strong> stores it in <code>local-&gt;dict</code>. So there
    are two references to this thread's <code>__dict__</code>: one from
    <code>PyThreadState</code>, one from local.</li>
<li>The worker thread dies, and the interpreter deletes its
    <code>PyThreadState</code>. Now there's one reference to the dead thread's
    <code>__dict__</code>: <code>local-&gt;dict</code>.</li>
<li>Finally, we do <code>getattr(local, 'whatever', None)</code> from the main
    thread. In <code>_ldict()</code>, <code>self-&gt;dict != ldict</code>, so <code>self-&gt;dict</code> is
    dereferenced and replaced with the main thread's <code>__dict__</code>. Now the
    dead thread's <code>__dict__</code> has finally been completely dereferenced,
    and the Weeper is deleted.</li>
</ol>
<p>The bug is that <code>_ldict()</code> both returns the local's <code>__dict__</code> for the
current thread, <strong>and</strong> stores a reference to it. This is why the
<code>__dict__</code> isn't deleted as soon as its thread dies: there's a useless
but persistent reference to the <code>__dict__</code> until another thread comes
along and clears it.</p>
<h1 id="thread-locals-in-new-python">Thread Locals in New Python</h1>
<p>In New Python, the architecture's a little more complex. Each
<code>PyThreadState</code>'s dict contains a dummy for each local, and each local
holds a dict mapping weak references of dummies to a per-thread
<code>__dict__</code>.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="new-python-thread-local-architecture.png" title="New Python's thread-local architecture" /></p>
<p>When a thread is dying and its <code>PyThreadState</code> is deleted, weakref
callbacks fire immediately on that thread, removing the thread's
<code>__dict__</code> for each local. Conversely, when a local is deleted, it
removes its dummy from <code>PyThreadState-&gt;dict</code>.</p>
<p><code>_ldict()</code> in New Python acts more sanely than in Old Python. It finds
the current thread's dummy in the <code>PyThreadState</code>, and gets the
<code>__dict__</code> for this thread from the dummy. But unlike in Old Python, it
doesn't store a extra reference to <code>__dict__</code> anywhere. It simply
returns it:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject <span style="color: #666666">*</span> <span style="color: #0000FF">_ldict</span>(localobject <span style="color: #666666">*</span>self)
{
    PyObject <span style="color: #666666">*</span>tdict, <span style="color: #666666">*</span>ldict, <span style="color: #666666">*</span>dummy;
    tdict <span style="color: #666666">=</span> PyThreadState_GetDict();
    dummy <span style="color: #666666">=</span> PyDict_GetItem(tdict, self<span style="color: #666666">-&gt;</span>key);
    <span style="color: #008000; font-weight: bold">if</span> (dummy <span style="color: #666666">==</span> <span style="color: #008000">NULL</span>) {
        ldict <span style="color: #666666">=</span> _local_create_dummy(self);
        <span style="color: #008000; font-weight: bold">if</span> (Py_TYPE(self)<span style="color: #666666">-&gt;</span>tp_init <span style="color: #666666">!=</span> PyBaseObject_Type.tp_init) {
            Py_TYPE(self)<span style="color: #666666">-&gt;</span>tp_init((PyObject<span style="color: #666666">*</span>)self, self<span style="color: #666666">-&gt;</span>args, self<span style="color: #666666">-&gt;</span>kw);
        }
    } <span style="color: #008000; font-weight: bold">else</span> {
        ldict <span style="color: #666666">=</span> ((localdummyobject <span style="color: #666666">*</span>) dummy)<span style="color: #666666">-&gt;</span>localdict;
    }

    <span style="color: #008000; font-weight: bold">return</span> ldict;
}
</pre></div>


<p>This whole weakrefs-to-dummies technique is, apparently, intended to
deal with some cyclic garbage collection problem I don't understand very
well. I believe the real reason why New Python acts as expected when
executing my script, and why Old Python acts weird, is that Old Python stores
the extra useless reference to the <code>__dict__</code> and New Python does not.</p>
<p><strong>Update:</strong> I finally found the bug reports that describe Old Python's weirdness and 2.7.1's solution. See:</p>
<ul>
<li><a href="http://bugs.python.org/issue1868">Issue 1868: threading.local doesn't free attrs when assigning thread exits</a></li>
<li><a href="http://bugs.python.org/issue3757">Issue 3757: threading.local doesn't support cyclic garbage collecting</a></li>
</ul>
