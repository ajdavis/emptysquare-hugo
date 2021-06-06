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

<p><a href="http://commons.wikimedia.org/wiki/File:Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG"><img alt="Young Woman Contemplating a Skull by Alessandro Casolani Statens Museum for Kunst DSC08131" border="0" src="Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG" style="display:block; margin-left:auto; margin-right:auto;" title="Young_Woman_Contemplating_a_Skull_by_Alessandro_Casolani_-_Statens_Museum_for_Kunst_-_DSC08131.JPG"/>
</a></p>
<p>A few months ago I had to solve a problem in PyMongo that is harder than it seems: how do you register for notifications when the current thread has died?</p>
<p>The circumstances are these: when you call <a href="http://api.mongodb.org/python/2.8/examples/requests.html"><code>start_request</code></a> in PyMongo, it gets a socket from its pool and assigns the socket to the current thread. We need some way to know when the current thread dies so we can reclaim the socket and return it to the socket pool for future use, rather than wastefully allowing it to be closed.</p>
<p>PyMongo can assume nothing about what kind of thread this is: It could've been started from the <code>threading</code> module, or the more primitive <code>thread</code> module, or it could've been started outside Python entirely, in C, as when PyMongo is running under mod_wsgi.</p>
<p>Here's what I came up with:</p>

{{<highlight python3>}}
import threading
import weakref

class ThreadWatcher(object):
    class Vigil(object):
        pass

    def __init__(self):
        self._refs = {}
        self._local = threading.local()

    def _on_death(self, vigil_id, callback, ref):
        self._refs.pop(vigil_id)
        callback()

    def watch(self, callback):
        if not self.is_watching():
            self._local.vigil = v = ThreadWatcher.Vigil()
            on_death = partial(
                self._on_death, id(v), callback)

            ref = weakref.ref(v, on_death)
            self._refs[id(v)] = ref

    def is_watching(self):
        "Is the current thread being watched?"
        return hasattr(self._local, 'vigil')

    def unwatch(self):
        try:
            v = self._local.vigil
            del self._local.vigil
            self._refs.pop(id(v))
        except AttributeError:
            pass
{{< / highlight >}}

<p>The key lines are highlighted, in <code>watch()</code>. First, I make a <a href="http://docs.python.org/2/library/weakref.html#weakref.ref">weakref</a> to a thread local. Weakrefs are permitted on subclasses of <code>object</code> but not <code>object</code> itself, so I use an inner class called Vigil. I initialize the weakref with a callback, which will be executed when the vigil is deleted.</p>
<p>The callback only fires if the weakref outlives the vigil, so I keep the weakref alive by storing it as a value in the <code>_refs</code> dict. The key into <code>_refs</code> can't be the vigil itself, since then the vigil would have a strong reference and wouldn't be deleted when the thread dies. I use <code>id(key)</code> instead.</p>
<p>Let's step through this. When a thread calls <code>watch()</code>, the only strong reference to the vigil is a thread-local. When a thread dies its locals are cleaned up, the vigil is dereferenced, and <code>_on_death</code> runs. <code>_on_death</code> cleans up <code>_refs</code> and then voilà, it runs the original callback.</p>
<p>When exactly is the vigil deleted? This is a subtle point, as the sages among you know. First, PyPy uses occasional <a href="http://doc.pypy.org/en/latest/gc_info.html">mark and sweep garbage collection</a> instead of reference-counting, so the vigil isn't deleted until some time after the thread dies. In unittests, I force the issue with <code>gc.collect()</code>.</p>
<p>Second, there's a <a href="http://bugs.python.org/issue1868">bug in CPython 2.6</a> and earlier, fixed by Antoine Pitrou in CPython 2.7.1, where thread locals aren't cleaned up until the thread dies <em>and</em> some other thread accesses the local. I <a href="/pythons-thread-locals-are-weird/">wrote about this in detail</a> last year when I was struggling with it. <code>gc.collect()</code> won't help in this case.</p>
<p>Thirdly, when is the local cleaned up in Python 2.7.1 and later? It happens as soon as the interpreter deletes the underlying <code>PyThreadState</code>, but that can actually come <em>after</em> <code>Thread.join()</code> returns—<code>join()</code> is simply waiting for a <a href="http://docs.python.org/2/library/threading.html#condition-objects">Condition</a> to be set at the end of the thread's run, which comes before the locals are cleared. So in Python 2.7.1 we need to sleep a few milliseconds after joining the thread to be certain it's truly gone.</p>
<p>Thus a reliable test for my ThreadWatcher class might look like:</p>

{{<highlight python3>}}
class TestWatch(unittest.TestCase):
    def test_watch(self):
        watcher = ThreadWatcher()
        callback_ran = [False]

        def callback():
            callback_ran[0] = True

        def target():
            watcher.watch(callback)

        t = threading.Thread(target=target)
        t.start()
        t.join()

        # Trigger collection in Py 2.6
        # See http://bugs.python.org/issue1868
        watcher.is_watching()
        gc.collect()

        # Cleanup can take a few ms in
        # Python >= 2.7
        for _ in range(10):
            if callback_ran[0]:
                break
            else:
                time.sleep(.1)


        assert callback_ran[0]
        # id(v) removed from _refs?
        assert not watcher._refs
{{< / highlight >}}

<p>The <code>is_watching()</code> call accesses the local object from the main thread after the child has died, working around the Python 2.6 bug, and the <code>gc.collect()</code> call makes the test pass in PyPy. The sleep loop gives Python 2.7.1 a chance to finish tearing down the thread state, including locals.</p>
<p>Two final cautions. The first is, you can't predict which thread runs the callback. In Python 2.6 it's whichever thread accesses the local <em>after</em> the child dies. In later versions, with Pitrou's improved thread-local implementation, the callback is run on the dying child thread. In PyPy it's whichever thread is active when the garbage collector decides to run.</p>
<p>The second caution is, there's an unreported memory-leak bug in Python 2.6, which Pitrou fixed in Python 2.7.1 along with the other bug I linked to. If you access a thread-local from <em>within</em> the weakref callback, you're touching the local in an inconsistent state, and the <em>next</em> object stored in the local will never be dereferenced. So don't do that. Here's a demonstration:</p>

{{<highlight python3>}}
class TestRefLeak(unittest.TestCase):
    def test_leak(self):
        watcher = ThreadWatcher()
        n_callbacks = [0]
        nthreads = 10

        def callback():
            # BAD, NO!:
            # Accessing thread-local in callback
            watcher.is_watching()
            n_callbacks[0] += 1

        def target():
            watcher.watch(callback)

        for _ in range(nthreads):
            t = threading.Thread(target=target)
            t.start()
            t.join()

        watcher.is_watching()
        gc.collect()
        for _ in range(10):
            if n_callbacks[0] == nthreads:
                break
            else:
                time.sleep(.1)

        self.assertEqual(nthreads, n_callbacks[0])
{{< / highlight >}}

<p>In Python 2.7.1 and later the test passes because all ten threads' locals are cleaned up, and the callback runs ten times. But in Python 2.6 only five locals are deleted.</p>
<p>I discovered this bug when I rewrote the connection pool in PyMongo 2.2 and a user reported that in Python 2.6 and mod_wsgi, every <em>second</em> request leaked one socket! I fixed PyMongo in version 2.2.1 by avoiding accessing thread locals while they're being torn down. (See bug <a href="https://jira.mongodb.org/browse/PYTHON-353">PYTHON-353</a>.)</p>
<p><strong>Update:</strong> I've discovered that in Python 2.7.0 and earlier, you need to lock around the assignment to <code>self._local.vigil</code>, see <a href="/another-thing-about-pythons-threadlocals/">"Another Thing About Threadlocals"</a>.</p>
<p>For further reading:</p>
<ul>
<li><a href="https://gist.github.com/4644641">My whole gist for ThreadWatcher and its tests</a></li>
<li><a href="http://bugs.python.org/issue1868">Pitrou's new thread-local implementation for Python 2.7.1</a></li>
<li><a href="https://github.com/mongodb/mongo-python-driver/blob/master/pymongo/thread_util.py">PyMongo's thread utilities</a></li>
</ul>
<hr/>
<p>Post-script: The image up top is a <a href="http://en.wikipedia.org/wiki/Memento_mori">memento mori</a>, a "reminder you will die," by Alessandro Casolani from the 16th Century. The memento mori genre is intended to offset a portrait subject's vanity—you look good now, but your beauty won't make a difference when you face your final judgment.</p>
<p>This was painted circa 1502 by Andrea Previtali:</p>
<p><a href="http://commons.wikimedia.org/wiki/File:Andrea_Previtali_-_Memento_Mori_%28verso%29_-_WGA18406.jpg"><img alt="Andrea Previtali Memento Mori WGA18406" border="0" src="Andrea_Previtali_Memento_Mori_WGA18406.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Andrea_Previtali_Memento_Mori_WGA18406.jpg"/></a></p>
<p>The inscription is "Hic decor hec forma manet, hec lex omnibus unam," which my Latin-nerd friends translate as, "This beauty endures only in this form, this law is the same for everyone." It was painted upside-down on the back of this handsome guy:</p>
<p><img alt="Andrea Previtali portrait of a man" border="0" src="Andrea_Previtali-portrait-of-a-man.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Andrea_Previtali-portrait-of-a-man.jpg"/></p>
<p>The painting was mounted on an axle so the face and the skull could be rapidly alternated and compared. Think about that the next time you start a thread—it may be running now, but soon enough it will terminate and even its thread-id will be recycled.</p>
