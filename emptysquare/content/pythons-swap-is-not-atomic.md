+++
type = "post"
title = "Python's swap is not atomic"
date = "2012-04-28T15:49:13"
description = "I rewrote PyMongo's connection pool over the last few months. Among the concurrency issues I had to nail down was, if a thread is resetting the connection pool as another thread is using the pool, how do I keep them from stepping on each [ ... ]"
category = ["Programming", "Python", "MongoDB"]
tag = ["threading"]
enable_lightbox = false
draft = false
+++

<p>I <a href="/requests-in-python-and-mongodb/">rewrote PyMongo's connection
pool</a> over the last few months.
Among the concurrency issues I had to nail down was, if a thread is
resetting the connection pool as another thread is using the pool, how
do I keep them from stepping on each other?</p>
<p>I thought I nailed this, but of course I didn't. There's a race
condition in here:</p>

{{<highlight python3>}}
class Pool(object):
    def __init__(self):
        self.sockets = set()

    def reset(self):
        # Close sockets before deleting them
        sockets, self.sockets = self.sockets, set()
        for sock_info in sockets: sock_info.close()
{{< / highlight >}}

<p>I thought that the swap would be atomic: the first thread to enter
<code>reset()</code> would replace self.sockets with an empty set, then close all
the old sockets, and all subsequent threads would find that self.sockets
was empty. That turns out not to be the case.</p>
<p>The race condition was occasionally revealed in runs of PyMongo's huge
test suite. One of the tests spins up 40 concurrent threads. Each thread
queries MongoDB, calls reset(), and queries MongoDB again. Here's how
the test fails:</p>

{{<highlight plain>}}
test_disconnect (test.test_pooling.TestPooling) ... Exception in thread Thread-45:
Traceback (most recent call last):
 < ... snip ... >
 File "pymongo/pool.py", line 159, in reset
   for sock_info in sockets: sock_info.close()
RuntimeError: Set changed size during iteration
{{< / highlight >}}

<p>As I said, I'd thought the swap was atomic, but in fact it takes half a
dozen bytecode instructions. That one swap line:</p>

{{<highlight plain>}}
sockets, self.sockets = self.sockets, set()
{{< / highlight >}}

<p>...disassembles to:</p>

{{<highlight python3>}}
            0 LOAD_FAST                0 (self)
            3 LOAD_ATTR                0 (sockets)
            6 LOAD_GLOBAL              1 (set)
            9 CALL_FUNCTION            0
           12 ROT_TWO          <- this is the swap
           13 STORE_FAST               1 (sockets)
           16 LOAD_FAST                0 (self)
           19 STORE_ATTR               0 (sockets)
{{< / highlight >}}

<p>Say that Thread 1 is executing this function. Thread 1 loads
self.sockets and the empty set onto its stack and swaps them, and before
it gets to <code>STORE_ATTR</code> (where self.sockets is actually replaced), it
gets interrupted by Thread 2. Thread 2 runs some other part of the
connection pool's code, e.g.:</p>

{{<highlight python3>}}
def return_socket(self, sock_info):
    self.sockets.add(sock_info)
{{< / highlight >}}

<p>This disassembles to:</p>

{{<highlight python3>}}
           24 LOAD_FAST                0 (self)
           27 LOAD_ATTR                1 (sockets)
           30 LOAD_ATTR                3 (add)
           33 LOAD_FAST                1 (sock_info)
           36 CALL_FUNCTION            1
{{< / highlight >}}

<p>Let's say Thread 2 reaches the <code>LOAD_ATTR 1</code> bytecode. Now it has
self.sockets on its stack, and it gets interrupted by Thread 1, which is
still in reset(). Thread 1 replaces self.sockets with the empty set. But
alas, Thread 1's "old" list of sockets and Thread 2's "self.sockets" are
the <strong>same</strong> set. Thread 1 starts iterating over the old list of
sockets, closing them:</p>

{{<highlight python3>}}
for sock_info in sockets: sock_info.close()
{{< / highlight >}}

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

{{<highlight c>}}
static PyObject * sock_close(PySocketSockObject *s) {
    SOCKET_T fd;

    if ((fd = s->sock_fd) != -1) {
        s->sock_fd = -1;
        Py_BEGIN_ALLOW_THREADS
        (void) SOCKETCLOSE(fd);
        Py_END_ALLOW_THREADS
    }
    Py_INCREF(Py_None);
    return Py_None;
}
{{< / highlight >}}

<p>That <code>Py_BEGIN_ALLOW_THREADS</code> macro releases the <a href="http://wiki.python.org/moin/GlobalInterpreterLock">Global Interpreter
Lock</a> and
<code>Py_END_ALLOW_THREADS</code> waits to reacquire it. In a multithreaded Python
program, releasing the GIL makes it very likely that another thread
which is waiting for the GIL will immediately acquire it.
(Notwithstanding <a href="http://pyvideo.org/video/588/mindblowing-python-gil">David Beazley's talk on the
GIL</a>—he
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

{{<highlight python3>}}
class Pool(object):
    def __init__(self):
        self.sockets = set()
        self.lock = threading.Lock()

    def reset(self):
        self.lock.acquire()
        try:
            # Close sockets before deleting them
            sockets, self.sockets = self.sockets, set()
        finally:
            self.lock.release()

        # Now only this thread can have a reference to this set of sockets
        for sock_info in sockets: sock_info.close()

   def return_socket(self, sock_info):
        self.lock.acquire()
        try:
            self.sockets.add(sock_info)
        finally:
            self.lock.release()
{{< / highlight >}}

<p>Single-bytecode instructions in Python <strong>are</strong> atomic, and if you can
use this atomicity to avoid mutexes then I believe you should—not only
is your code faster and simpler, but you avoid the risk of deadlocks,
which are the worst concurrency bugs. But not everything that looks
atomic is. When in doubt, use the
<a href="http://docs.python.org/py3k/library/dis.html">dis</a> module to examine
your bytecode and find out for sure.</p>
