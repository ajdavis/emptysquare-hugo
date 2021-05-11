+++
type = "post"
title = "Python's swap is not atomic"
date = "2012-04-28T15:49:13"
description = "I rewrote PyMongo's connection pool over the last few months. Among the concurrency issues I had to nail down was, if a thread is resetting the connection pool as another thread is using the pool, how do I keep them from stepping on each [ ... ]"
category = ["Programming", "Python", "MongoDB"]
tag = ["threading"]
enable_lightbox = false
draft = false
disqus_identifier = "494 http://emptysquare.net/blog/?p=494"
disqus_url = "https://emptysqua.re/blog/494 http://emptysquare.net/blog/?p=494/"
+++

<p>I <a href="/requests-in-python-and-mongodb/">rewrote PyMongo's connection
pool</a> over the last few months.
Among the concurrency issues I had to nail down was, if a thread is
resetting the connection pool as another thread is using the pool, how
do I keep them from stepping on each other?</p>
<p>I thought I nailed this, but of course I didn't. There's a race
condition in here:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Pool</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">set</span>()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">reset</span>(<span style="color: #008000">self</span>):
        <span style="color: #408080; font-style: italic"># Close sockets before deleting them</span>
<span style="background-color: #ffffcc">        sockets, <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets, <span style="color: #008000">set</span>()
</span>        <span style="color: #008000; font-weight: bold">for</span> sock_info <span style="color: #AA22FF; font-weight: bold">in</span> sockets: sock_info<span style="color: #666666">.</span>close()
</pre></div>


<p>I thought that the swap would be atomic: the first thread to enter
<code>reset()</code> would replace self.sockets with an empty set, then close all
the old sockets, and all subsequent threads would find that self.sockets
was empty. That turns out not to be the case.</p>
<p>The race condition was occasionally revealed in runs of PyMongo's huge
test suite. One of the tests spins up 40 concurrent threads. Each thread
queries MongoDB, calls reset(), and queries MongoDB again. Here's how
the test fails:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">test_disconnect (test.test_pooling.TestPooling) ... Exception in thread Thread-45:
Traceback (most recent call last):
 &lt; ... snip ... &gt;
 File &quot;pymongo/pool.py&quot;, line 159, in reset
   for sock_info in sockets: sock_info.close()
RuntimeError: Set changed size during iteration
</pre></div>


<p>As I said, I'd thought the swap was atomic, but in fact it takes half a
dozen bytecode instructions. That one swap line:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">       sockets, <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets, <span style="color: #008000">set</span>()
</pre></div>


<p>...disassembles to:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">            <span style="color: #666666">0</span> LOAD_FAST                <span style="color: #666666">0</span> (self)
            <span style="color: #666666">3</span> LOAD_ATTR                <span style="color: #666666">0</span> (sockets)
            <span style="color: #666666">6</span> LOAD_GLOBAL              <span style="color: #666666">1</span> (set)
            <span style="color: #666666">9</span> CALL_FUNCTION            <span style="color: #666666">0</span>
           <span style="color: #666666">12</span> ROT_TWO          <span style="color: #666666">&lt;-</span> this is the swap
           <span style="color: #666666">13</span> STORE_FAST               <span style="color: #666666">1</span> (sockets)
           <span style="color: #666666">16</span> LOAD_FAST                <span style="color: #666666">0</span> (self)
           <span style="color: #666666">19</span> STORE_ATTR               <span style="color: #666666">0</span> (sockets)
</pre></div>


<p>Say that Thread 1 is executing this function. Thread 1 loads
self.sockets and the empty set onto its stack and swaps them, and before
it gets to <code>STORE_ATTR</code> (where self.sockets is actually replaced), it
gets interrupted by Thread 2. Thread 2 runs some other part of the
connection pool's code, e.g.:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">return_socket</span>(<span style="color: #008000">self</span>, sock_info):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets<span style="color: #666666">.</span>add(sock_info)
</pre></div>


<p>This disassembles to:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">           24 LOAD_FAST                0 (self)
           27 LOAD_ATTR                1 (sockets)
           30 LOAD_ATTR                3 (add)
           33 LOAD_FAST                1 (sock_info)
           36 CALL_FUNCTION            1
</pre></div>


<p>Let's say Thread 2 reaches the <code>LOAD_ATTR 1</code> bytecode. Now it has
self.sockets on its stack, and it gets interrupted by Thread 1, which is
still in reset(). Thread 1 replaces self.sockets with the empty set. But
alas, Thread 1's "old" list of sockets and Thread 2's "self.sockets" are
the <strong>same</strong> set. Thread 1 starts iterating over the old list of
sockets, closing them:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">        <span style="color: #008000; font-weight: bold">for</span> sock_info <span style="color: #AA22FF; font-weight: bold">in</span> sockets: sock_info<span style="color: #666666">.</span>close()
</pre></div>


<p>...but it gets interrupted again by Thread 2, which does
<code>self.sockets.add(sock_info)</code>, increasing the set's size by one. When
Thread 1 is next resumed, it tries to continue iterating, and raises the
"Set changed size during iteration" exception.</p>
<p>Let's dive deeper for a minute. You may be thinking that in practice two
Python threads wouldn't interrupt each other this often. Indeed, the
interpreter <a href="http://docs.python.org/library/sys.html#sys.setcheckinterval">executes 100 bytecodes at a time before it even thinks of
switching
threads</a>.
But in our case, Thread 1 is repeatedly calling <code>socket.close()</code>, which
is written in socketmodule.c like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject <span style="color: #666666">*</span> <span style="color: #0000FF">sock_close</span>(PySocketSockObject <span style="color: #666666">*</span>s) {
    SOCKET_T fd;

    <span style="color: #008000; font-weight: bold">if</span> ((fd <span style="color: #666666">=</span> s<span style="color: #666666">-&gt;</span>sock_fd) <span style="color: #666666">!=</span> <span style="color: #666666">-1</span>) {
        s<span style="color: #666666">-&gt;</span>sock_fd <span style="color: #666666">=</span> <span style="color: #666666">-1</span>;
<span style="background-color: #ffffcc">        Py_BEGIN_ALLOW_THREADS
</span>        (<span style="color: #B00040">void</span>) SOCKETCLOSE(fd);
<span style="background-color: #ffffcc">        Py_END_ALLOW_THREADS
</span>    }
    Py_INCREF(Py_None);
    <span style="color: #008000; font-weight: bold">return</span> Py_None;
}
</pre></div>


<p>That <code>Py_BEGIN_ALLOW_THREADS</code> macro releases the <a href="http://wiki.python.org/moin/GlobalInterpreterLock">Global Interpreter
Lock</a> and
<code>Py_END_ALLOW_THREADS</code> waits to reacquire it. In a multithreaded Python
program, releasing the GIL makes it very likely that another thread
which is waiting for the GIL will immediately acquire it.
(Notwithstanding <a href="http://pyvideo.org/video/588/mindblowing-python-gil">David Beazley's talk on the
GIL</a>&mdash;he
demonstrates that CPU-bound and IO-bound threads competing for the GIL
on a multicore system interrupt each other too <strong>rarely</strong>, but in this
case I'm only dealing with IO-bound threads.)</p>
<p>So calling socket.close() in a loop ensures that this thread will be
constantly interrupted. The probability that some thread in
return_socket() gets a reference to the set, and modifies it,
interleaved with some other thread in reset() getting a reference to the
<strong>same</strong> set and iterating it, is high enough to break PyMongo's
unittest about 1% of the time.</p>
<p>The solution was obvious once I understood the problem:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Pool</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">set</span>()
<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>lock <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Lock()
</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">reset</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>lock<span style="color: #666666">.</span>acquire()
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #408080; font-style: italic"># Close sockets before deleting them</span>
            sockets, <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets, <span style="color: #008000">set</span>()
        <span style="color: #008000; font-weight: bold">finally</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>lock<span style="color: #666666">.</span>release()

        <span style="color: #408080; font-style: italic"># Now only this thread can have a reference to this set of sockets</span>
        <span style="color: #008000; font-weight: bold">for</span> sock_info <span style="color: #AA22FF; font-weight: bold">in</span> sockets: sock_info<span style="color: #666666">.</span>close()

   <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">return_socket</span>(<span style="color: #008000">self</span>, sock_info):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>lock<span style="color: #666666">.</span>acquire()
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets<span style="color: #666666">.</span>add(sock_info)
        <span style="color: #008000; font-weight: bold">finally</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>lock<span style="color: #666666">.</span>release()
</pre></div>


<p>Single-bytecode instructions in Python <strong>are</strong> atomic, and if you can
use this atomicity to avoid mutexes then I believe you should—not only
is your code faster and simpler, but you avoid the risk of deadlocks,
which are the worst concurrency bugs. But not everything that looks
atomic is. When in doubt, use the
<a href="http://docs.python.org/py3k/library/dis.html">dis</a> module to examine
your bytecode and find out for sure.</p>
