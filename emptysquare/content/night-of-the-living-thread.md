+++
type = "post"
title = "Night Of The Living Thread"
date = "2013-10-16T10:06:09"
description = "A fun series about a race condition I fixed in Python's threading implementation."
category = ["Programming", "Python"]
tag = ["threading"]
enable_lightbox = false
thumbnail = "bloodthirsty-lust.jpg"
draft = false
+++

<p>What should this Python code print?:</p>

{{<highlight python3>}}
t = threading.Thread()
t.start()
if os.fork() == 0:
    # We're in the child process.
    print t.isAlive()
{{< / highlight >}}

<p>In Unix, only the thread that calls <code>fork()</code> is copied to the child process; all other threads are dead. So <code>t.isAlive()</code> in the child process should always return False. But <em>sometimes</em>, it returns True! It's the....</p>
<p><img alt="Night of the Living Thread" src="night-of-the-living-thread.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Night of the Living Thread"/></p>
<p>How did I discover this horrifying zombie thread? A project I work on, PyMongo, uses a background thread to monitor the state of the database server. If a user initializes PyMongo and then forks, the monitor is absent in the child. PyMongo should notice that the monitor thread's <code>isAlive</code> is False, and raise an error:</p>

{{<highlight python3>}}
# Starts monitor:
client = pymongo.MongoReplicaSetClient()
os.fork()

# Should raise error, "monitor is dead":
client.db.collection.find_one()
{{< / highlight >}}

<p>But intermittently, the monitor is still alive after the fork! It keeps coming back in a bloodthirsty lust for HUMAN FLESH!</p>
<p>I put on my Sixties scientist outfit (lab coat, thick-framed glasses) and sought the cause of this unnatural reanimation. To begin with, what does <code>Thread.isAlive()</code> do?:</p>

{{<highlight python3>}}
class Thread(object):
    def isAlive(self):
        return self.__started.is_set() and not self.__stopped
{{< / highlight >}}

<p>After a fork, <code>__stopped</code> should be True on all threads but one. Whose job is it to set <code>__stopped</code> on all the threads that <em>didn't</em> call <code>fork()</code>? In <code>threading.py</code> I discovered the <code>_after_fork()</code> function, which I've simplified here:</p>

{{<highlight python3>}}
# Globals.
_active = {}
_limbo = {}

def _after_fork():
    # This function is called by PyEval_ReInitThreads
    # which is called from PyOS_AfterFork.  Here we
    # clean up threading module state that should not
    # exist after a fork.

    # fork() only copied current thread; clear others.
    new_active = {}
    current = current_thread()
    for thread in _active.itervalues():
        if thread is current:
            # There is only one active thread.
            ident = _get_ident()
            new_active[ident] = thread
        else:
            # All the others are already stopped.
            thread._Thread__stop()

    _limbo.clear()
    _active.clear()
    _active.update(new_active)
    assert len(_active) == 1
{{< / highlight >}}

<p>This function iterates all the Thread objects in a global dict called <code>_active</code>; each is removed and marked as "stopped", except for the current thread. How could this go wrong?</p>
<p><img alt="Night of the living dead" src="night_of_the_living_dead_3.jpg" style="display:block; margin-left:auto; margin-right:auto; border:1px solid black" title="Night of the living dead"/></p>
<p>Well, consider how a thread starts:</p>

{{<highlight python3>}}
class Thread(object):
    def start(self):
        _limbo[self] = self
        _start_new_thread(self.__bootstrap)

    def __bootstrap(self):
        self.__started.set()
        _active[self.__ident] = self
        del _limbo[self]
        self.run()
{{< / highlight >}}

<p>(Again, I've simplified this.) The Thread object's <code>start</code> method adds the object to the <code>_limbo</code> list, then creates a new OS-level thread. The new thread, before it gets to work, marks itself as "started" and moves itself from <code>_limbo</code> to <code>_active</code>.</p>
<p>Do you see the bug now? Perhaps the thread was <a href="http://en.wikipedia.org/wiki/Night_of_the_living_dead#Plot_summary">reanimated by space rays from Venus</a> and craves the flesh of the living!</p>
<p><img alt="Night of the living dead 4" src="night_of_the_living_dead_4.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Night of the living dead 4"/></p>
<p>Or perhaps there's a race condition:</p>
<ol>
<li>Main thread calls worker's <code>start()</code>.</li>
<li>Worker calls <code>self.__started.set()</code>, but is interrupted before it adds itself to <code>_active</code>.</li>
<li>Main thread calls <code>fork()</code>.</li>
<li>In child process, main thread calls <code>_after_fork</code>, which doesn't find the worker in <code>_active</code> and doesn't mark it "stopped".</li>
<li><code>isAlive()</code> now returns True because the worker is started and not stopped.</li>
</ol>
<p><br/>
Now we know the cause of the grotesque revenant. What's the cure? Headshot?</p>
<p>I <a href="http://bugs.python.org/issue18418">submitted a patch to Python</a> that simply swapped the order of operations: first the thread adds itself to <code>_active</code>, then it marks itself started:</p>

{{<highlight python3>}}
def __bootstrap(self):
    _active[self.__ident] = self
    self.__started.set()
    self.run()
{{< / highlight >}}

<p>If the thread is interrupted by a fork after adding itself to <code>_active</code>, then <code>_after_fork()</code> finds it there and marks it stopped. The thread ends up stopped but not started, rather than the reverse. In this case <code>isAlive()</code> correctly returns False.</p>
<p>The Python core team looked at my patch, and Charles-François Natali suggested a cleaner fix. If the zombie thread is not yet in <code>_active</code>, it <em>is</em> in the global <code>_limbo</code> list. So <code>_after_fork</code> should iterate over both <code>_limbo</code> and <code>_active</code>, instead of just <code>_active</code>. Then it will mark the zombie thread as "stopped" along with the other threads.</p>

{{<highlight python3>}}
def _enumerate():
    return _active.values() + _limbo.values()

def _after_fork():
    new_active = {}
    current = current_thread()
    for thread in _enumerate():
        if thread is current:
            # There is only one active thread.
            ident = _get_ident()
            new_active[ident] = thread
        else:
            # All the others are already stopped.
            thread._Thread__stop()
{{< / highlight >}}

<p>This fix will be included in the next Python 2.7 and 3.3 releases. The zombie threads will stay good and dead...for now!</p>
<p>(Now read the sequels: <a href="/dawn-of-the-thread/">Dawn of the Thread</a>, in which I battle zombie threads in the abandoned tunnels of Python 2.6; and <a href="/day-of-the-thread/">Day of the Thread</a>, a post-apocalyptic thriller in which a lone human survivor tries to get a patch accepted via bugs.python.org.)</p>
<p><img alt="They keep coming back in a bloodthirsty lust for human flesh!" src="bloodthirsty-lust.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="They keep coming back in a bloodthirsty lust for human flesh!"/></p>
