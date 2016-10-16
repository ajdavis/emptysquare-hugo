+++
type = "post"
title = "Against ResourceWarnings in Python 3"
date = "2012-04-30T16:23:42"
description = "Update: Nick Coghlan has changed my mind, see our comment thread for the explanation. Allow me to grumble. Consider this function from Python 3.2.3's socketmodule.c: /* Deallocate a socket object in response to the last Py_DECREF(). [ ... ]"
categories = ["Programming", "Python"]
tags = []
enable_lightbox = false
draft = false
+++

<p><strong>Update</strong>: Nick Coghlan has changed my mind, <a href="/blog/against-resourcewarnings-in-python-3/#comment-514722438">see our comment
thread</a>
for the explanation.</p>
<hr />
<p>Allow me to grumble. Consider this function from Python 3.2.3's
socketmodule.c:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic">/* Deallocate a socket object in response to the last Py_DECREF().                                                                                                                                                                   </span>
<span style="color: #408080; font-style: italic">   First close the file description. */</span>

<span style="color: #008000; font-weight: bold">static</span> <span style="color: #B00040">void</span>
<span style="color: #0000FF">sock_dealloc</span>(PySocketSockObject <span style="color: #666666">*</span>s)
{
    <span style="color: #008000; font-weight: bold">if</span> (s<span style="color: #666666">-&gt;</span>sock_fd <span style="color: #666666">!=</span> <span style="color: #666666">-1</span>) {
        PyObject <span style="color: #666666">*</span>exc, <span style="color: #666666">*</span>val, <span style="color: #666666">*</span>tb;
        Py_ssize_t old_refcount <span style="color: #666666">=</span> Py_REFCNT(s);
        <span style="color: #666666">++</span>Py_REFCNT(s);
        PyErr_Fetch(<span style="color: #666666">&amp;</span>exc, <span style="color: #666666">&amp;</span>val, <span style="color: #666666">&amp;</span>tb);
<span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">if</span> (PyErr_WarnFormat(PyExc_ResourceWarning, <span style="color: #666666">1</span>,
</span><span style="background-color: #ffffcc">                             <span style="color: #BA2121">&quot;unclosed %R&quot;</span>, s))
</span>            <span style="color: #408080; font-style: italic">/* Spurious errors can appear at shutdown */</span>
            <span style="color: #008000; font-weight: bold">if</span> (PyErr_ExceptionMatches(PyExc_Warning))
                PyErr_WriteUnraisable((PyObject <span style="color: #666666">*</span>) s);
        PyErr_Restore(exc, val, tb);
        (<span style="color: #B00040">void</span>) SOCKETCLOSE(s<span style="color: #666666">-&gt;</span>sock_fd);
        Py_REFCNT(s) <span style="color: #666666">=</span> old_refcount;
    }
    Py_TYPE(s)<span style="color: #666666">-&gt;</span>tp_free((PyObject <span style="color: #666666">*</span>)s);
}
</pre></div>


<p>Let's ignore that "file description" has persisted as a misspelling of
"descriptor" in that comment since at least as far back as Python 2.4.
There's a new annoyance in this function: it now junks up my terminal
window with a ResourceWarning about an unclosed socket, <em>just before it
closes the socket</em>.</p>
<p>Any sane, informed Python developer knows she doesn't have to close
sockets explicitly, rather than letting the garbage collector close
them. There are two great reasons <strong>not</strong> to close sockets explicitly:</p>
<ol>
<li>In complex code it can be hard to know when the last reference to a
    socket is deleted. CPython knows precisely when the last reference
    goes away—that's when it calls <code>sock_dealloc</code>.</li>
<li>If you do know when a socket should be closed, it's <strong>still</strong>
    pointless to close it explicitly, because CPython is about to do it
    for you.</li>
</ol>
<p>"But Jython doesn't reference-count!" you howl. Relax, you're not using
Jython and neither am I. (Let us not speak of IronPython, either.)</p>
<p>"But what about PyPy!" you cry, and there you have a point. PyPy doesn't
use a reference-counting GC, and PyPy is going to be increasingly
popular. But PyPy is smart: it doesn't raise the ResourceWarning.</p>
<p>PyMongo now supports Python 3, and Python 3 is now pooping
ResourceWarnings to stderr, so at 10gen we've had to go through
PyMongo's socket-management code ensuring we know when a socket will be
deleted, and closing it. Even though the interpreter closes it again
immediately afterward.</p>
<p>Closing sockets is easy in PyMongo, but in other applications that use
sockets (or files or whatever) less deterministically than PyMongo does,
getting rid of ResourceWarnings is a total pain. Consider all the ways
we're used to dealing with resource deallocation, ordered from most to
least convenient. (When I get mad I make ordered lists.)</p>
<ol>
<li>Implicit reference counting: This is what CPython does and it's both
    automatic and predictable. I've loved this about CPython ever since
    I started using it.</li>
<li><a href="http://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization">Resource acquisition is
    initialization</a>:
    a reasonably elegant approach in C++ that wraps resources in objects
    allocated on the stack, so when the stack frame is destroyed the
    resource is freed, or at least its refcount is decremented. Library
    classes like <code>auto_ptr</code> make this style robust, even in the face of
    exceptions.</li>
<li>Explicit reference counting: Objective-C programmers are familiar
    with this. It's a pain, and error-prone, and mistakes lead to leaks
    and crashes. But with experience and frequent review of Apple's
    coding guidelines you can stamp out most of the bugs.</li>
<li>Malloc/free in C: You know what sucks? Manual memory management in
    C. In C, most of the bugs come from calling free() too early or not
    at all, and they are the worst bugs. In complex data structures it
    can be very difficult to determine when an object's lifetime is
    over.</li>
</ol>
<p>By adding the ResourceWarning, Python has gone from the top of the list
to the bottom. We are no longer able to rely on the interpreter to clean
up resources correctly, <strong>even though it still does,</strong> because then our
terminals will be littered with warnings. Since Python has not developed
any of the other languages' resource management techniques (because it
has no need for them whatsoever), we are left in the worst possible
situation: C-style manual resource management.</p>
<p>"You can just use a <a href="http://docs.python.org/reference/datamodel.html#context-managers">Context
Manager</a>
and the 'with' statement," you whine. That has two problems:</p>
<ol>
<li>Python 2.4 doesn't have the 'with' statement, so ResourceWarnings in
    Python 3 make it even harder to write code compatible both with
    Python 2.4 and Python 3.2, and Python 2.4 is far more widely
    installed and will be for some time. For 10gen, at least, ending
    Python 2.4 support is not an option. Thus ResourceWarnings are
    further discouraging adoption of Python 3.</li>
<li>If you only use a resource within a single block of code, your
    resource management was always trivially easy. I'm talking about
    interesting code where it's hard to tell when you're done with a
    resource. This is what garbage collection was supposed to fix for
    us.</li>
</ol>
<p>Besides manual management, there are two alternatives:</p>
<ol>
<li>Implement our own manual reference-counting, à la Objective-C, for
    cases where it's hard to know when a resource should be closed. For
    example, we could wrap our sockets in objects that implement
    incref() and decref(), and which close the underlying socket when
    the refcount goes to zero.</li>
<li>Rely on the garbage collector to clean up resources, just like we
    always have, and tolerate the useless warnings.</li>
</ol>
<p>Either is less convenient and more error-prone than resource management
was prior to ResourceWarnings.</p>
<p>I think ResourceWarnings are a terrible idea. I propose that we remove
them. Intelligent programmers can either clean up resources when they
know they're not needed, or rely on the garbage-collector to clean them
up. Python should leave it up to us to make that decision, rather than
forcing our hand. The alternative, which is to implement manual
management in Python for all resources, is too horrible to contemplate.</p>
    