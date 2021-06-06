+++
type = "post"
title = "Python's Thread Locals Are Weird"
date = "2012-05-27T16:46:58"
description = ""
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "new-python-thread-local-architecture.png"
draft = false
disqus_identifier = "564 http://emptysquare.net/blog/?p=564"
disqus_url = "https://emptysqua.re/blog/564 http://emptysquare.net/blog/?p=564/"
+++

<h1 id="the-weirdness">The Weirdness</h1>
<p>What do you think this script prints?:</p>

```py
import thread, threading, sys

class Weeper(object):
    def del(self):
        sys.stdout.write('oh cruel world %s\n' % thread.get_ident())

local = threading.local()

def target():
    local.weeper = Weeper()

t = threading.Thread(target=target)
t.start()
t.join()
sys.stdout.write('done %s\n' % thread.get_ident())
getattr(local, 'whatever', None)
```

<p>If you guessed something like this:</p>

{{<highlight plain>}}
oh cruel world 4475731968
done 140735297751392
{{< / highlight >}}

<p>...then you'd be right, <em>in Python after 2.7.1</em>. In Python 2.7.0 and
older (including the whole 2.6 series), the order of messages is reversed:</p>

{{<highlight plain>}}
done 140735297751392
oh cruel world 140735297751392
{{< / highlight >}}

<p>In New Python, the Weeper is deleted as soon as its thread dies, and
__del__ runs on the dying thread. In Old Python, the Weeper isn't
deleted until the thread is dead <strong>and</strong> a different thread accesses the
local's __dict__. Thus the Weeper is deleted at the line
<code>getattr(local, 'whatever', None)</code>, after the thread dies, and
<code>Weeper.__del__</code> runs on the main thread.</p>
<p>What if we remove the <code>getattr</code> call? In Old Python, this happens:</p>

{{<highlight plain>}}
done 140735297751392
Exception AttributeError: "'NoneType' object has no attribute 'get_ident'"
    in <bound method Weeper.__del__ of <__main__.Weeper object at 0x104f95590>>
    ignored
{{< / highlight >}}

<p>Without <code>getattr</code>, the Weeper isn't deleted until interpreter shutdown.
The shutdown sequence is complex and hard to predict—in this case the
<code>thread</code> module has been set to <code>None</code> before the Weeper is deleted, so
Weeper.__del__ can't do <code>thread.get_ident()</code>.</p>
<h1 id="thread-locals-in-old-python">Thread Locals in Old Python</h1>
<p>To understand why locals act this way in Old Python, let's
look at the implementation in C. The core interpreter's <code>PyThreadState</code>
struct has a <code>dict</code> attribute, and each <code>threading.local</code> object has a
<code>key</code> attribute formatted like
<code>"thread.local.<memory address of self>"</code>. Each local has a <code>__dict__</code>
of attributes per thread, stored in <code>PyThreadState</code>'s <code>dict</code> with the
local's key.</p>
<p>threadmodule.c includes a function <code>_ldict(localobject \*self)</code> which
takes a local and finds its <code>__dict__</code> for the current thread.
<code>_ldict()</code> finds and returns the local's <code>__dict__</code> for this thread,
<strong>and</strong> stores it in <code>self‑>dict</code>.</p>
<p><img src="old-python-thread-local-architecture.png" style="display:block; margin-left:auto; margin-right:auto;" title="Old Python's thread-local architecture"/></p>
<p>This architecture has, in my opinion, a bug. Here's the implementation
of <code>_ldict()</code>:</p>

```c
static PyObject  _ldict(localobject self)
{
    /* get PyThreadState->dict for this thread */
    PyObject tdict = PyThreadState_GetDict();
    PyObject ldict = PyDict_GetItem(tdict, self‑>key);
    if (ldict == NULL) {
        ldict = PyDict_New(); /* we own ldict /
        PyDict_SetItem(tdict, self‑>key, ldict);
        Py_CLEAR(self‑>dict);
        Py_INCREF(ldict);
        self‑>dict = ldict; /* still borrowed */

        if (Py_TYPE(self)->tp_init != PyBaseObject_Type.tp_init) {
            Py_TYPE(self)->tp_init((PyObject*)self, self‑>args, self‑>kw);
        }
    }

    /* The call to tp_init above may have caused another thread to run.
       Install our ldict again. */
    if (self‑>dict != ldict) {
        Py_CLEAR(self‑>dict);
        Py_INCREF(ldict);
        self‑>dict = ldict;
    }

    return ldict;
}
```

<p>I've edited for brevity. There's a few interesting things here—one is
the check for a custom <code>__init__</code> method. If this object is a subclass
of local which overrides <code>__init__</code>, then <code>__init__</code> is called whenever
a new thread accesses this local's attributes for the first time.</p>
<p>But the main thing I'm showing you is the two calls to
<code>Py_CLEAR(self‑>dict)</code>, which decrements <code>self‑>dict</code>'s refcount. It's
called when a thread accesses this local's attributes for the first
time, <strong>or</strong> if this thread is accessing the local's attributes after a
different thread has accessed them—that is, if <code>self‑>dict != ldict</code>.</p>
<p>So now we clearly understand why a thread's locals aren't deleted
immediately after it dies:</p>
<ol>
<li>The worker thread stores a Weeper in <code>local.weeper</code>. <code>_ldict()</code>
    creates a new <code>__dict__</code> for this thread and stores it as a value in
    <code>PyThreadState‑>dict</code>, <strong>and</strong> stores it in <code>local‑>dict</code>. So there
    are two references to this thread's <code>__dict__</code>: one from
    <code>PyThreadState</code>, one from local.</li>
<li>The worker thread dies, and the interpreter deletes its
    <code>PyThreadState</code>. Now there's one reference to the dead thread's
    <code>__dict__</code>: <code>local‑>dict</code>.</li>
<li>Finally, we do <code>getattr(local, 'whatever', None)</code> from the main
    thread. In <code>_ldict()</code>, <code>self‑>dict != ldict</code>, so <code>self‑>dict</code> is
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
<p><img src="new-python-thread-local-architecture.png" style="display:block; margin-left:auto; margin-right:auto;" title="New Python's thread-local architecture"/></p>
<p>When a thread is dying and its <code>PyThreadState</code> is deleted, weakref
callbacks fire immediately on that thread, removing the thread's
<code>__dict__</code> for each local. Conversely, when a local is deleted, it
removes its dummy from <code>PyThreadState->dict</code>.</p>
<p><code>_ldict()</code> in New Python acts more sanely than in Old Python. It finds
the current thread's dummy in the <code>PyThreadState</code>, and gets the
<code>__dict__</code> for this thread from the dummy. But unlike in Old Python, it
doesn't store a extra reference to <code>__dict__</code> anywhere. It simply
returns it:</p>

```c
static PyObject _ldict(localobject self)
{
    PyObject tdict, ldict, dummy;
    tdict = PyThreadState_GetDict();
    dummy = PyDict_GetItem(tdict, self->key);
    if (dummy == NULL) {
        ldict = _local_create_dummy(self);
        if (Py_TYPE(self)->tp_init != PyBaseObject_Type.tp_init) {
            Py_TYPE(self)->tp_init((PyObject)self, self->args, self->kw);
        }
    } else {
        ldict = ((localdummyobject *) dummy)->localdict;
    }

    return ldict;
}
```

<p>This whole weakrefs-to-dummies technique is, apparently, intended to
deal with some cyclic garbage collection problem I don't understand very
well. I believe the real reason why New Python acts as expected when
executing my script, and why Old Python acts weird, is that Old Python stores
the extra useless reference to the <code>\_\_dict\_\_</code> and New Python does not.</p>
<p><strong>Update:</strong> I finally found the bug reports that describe Old Python's weirdness and 2.7.1's solution. See:</p>
<ul>
<li><a href="http://bugs.python.org/issue1868">Issue 1868: threading.local doesn't free attrs when assigning thread exits</a></li>
<li><a href="http://bugs.python.org/issue3757">Issue 3757: threading.local doesn't support cyclic garbage collecting</a></li>
</ul>
