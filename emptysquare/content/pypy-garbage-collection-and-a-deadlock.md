+++
type = "post"
title = "PyPy, Garbage Collection, And A Deadlock"
date = "2015-04-05T22:31:09"
description = "Yet another danger of __del__."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "ouroboros.jpg"
draft = false
disqus_identifier = "548a1a695393740964aee92c"
disqus_url = "https://emptysqua.re/blog/548a1a695393740964aee92c/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="ouroboros.jpg" alt="Ouroboros" title="Ouroboros" /></p>
<p>I fixed a deadlock in PyMongo 3 and PyPy which, rarely, could happen in PyMongo 2 as well. Diagnosing the deadlock was educational and teaches us a rule about writing <code>__del__</code> methods&mdash;yet another tip about what to expect when you're expiring.</p>
<div class="toc">
<ul>
<li><a href="#a-toy-example">A Toy Example</a></li>
<li><a href="#the-pymongo-bug">The PyMongo Bug</a></li>
<li><a href="#diagnosis">Diagnosis</a></li>
<li><a href="#the-fix">The Fix</a></li>
<li><a href="#what-to-expect-when-youre-expiring">What To Expect When You're Expiring</a></li>
<li><a href="#the-moral-of-the-story-is">The Moral Of The Story Is....</a></li>
</ul>
</div>
<h1 id="a-toy-example">A Toy Example</h1>
<p>This deadlocks in CPython:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">threading</span>

lock <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Lock()

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">C</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__del__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;getting lock&#39;</span>)
        <span style="color: #008000; font-weight: bold">with</span> lock:
            <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;releasing lock&#39;</span>)
            <span style="color: #008000; font-weight: bold">pass</span>

c <span style="color: #666666">=</span> C()
<span style="color: #008000; font-weight: bold">with</span> lock:
    <span style="color: #008000; font-weight: bold">del</span> c
</pre></div>


<p>The statement <code>del c</code> removes the variable <code>c</code> from the namespace. The object that <code>c</code> had referred to has no more references, so CPython immediately calls its <code>__del__</code> method, which tries to get the lock. The lock is held, so the process deadlocks. It prints "getting lock" and hangs forever.</p>
<p>What if we swap the final two statements?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">del</span> c
<span style="color: #008000; font-weight: bold">with</span> lock:
    <span style="color: #008000; font-weight: bold">pass</span>
</pre></div>


<p>This is fine. The <code>__del__</code> method completes and releases the lock before the next statement acquires it.</p>
<p>But consider PyPy. It doesn't use reference counts: unreferenced objects live until the garbage collector frees them. The moment when objects are freed is unpredictable. If the GC happens to kick in while the lock is held, it will deadlock. We can force this situation:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">del</span> c
<span style="color: #008000; font-weight: bold">with</span> lock:
    gc<span style="color: #666666">.</span>collect()
</pre></div>


<p>Just like the first example, this prints "getting lock" and deadlocks.</p>
<h1 id="the-pymongo-bug">The PyMongo Bug</h1>
<p>A few weeks ago, I found a deadlock like this in my code for <a href="/pymongo-3-beta/">the upcoming PyMongo 3.0 release</a>. From there, I discovered a far rarer deadlock in the current release as well.</p>
<p>I'll give you a little context so you can see how the bug arose. With PyMongo you stream results from the MongoDB server like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">for</span> document <span style="color: #AA22FF; font-weight: bold">in</span> collection<span style="color: #666666">.</span>find():
    <span style="color: #008000; font-weight: bold">print</span>(document)
</pre></div>


<p>The <code>find</code> method actually returns an instance of the <code>Cursor</code> class, so you could write this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
<span style="color: #008000; font-weight: bold">for</span> document <span style="color: #AA22FF; font-weight: bold">in</span> cursor:
    <span style="color: #008000; font-weight: bold">print</span>(document)
</pre></div>


<p>As you iterate the cursor, it returns documents from its client-side buffer until the buffer is empty, then it fetches another big batch of documents from the server. After it returns the final document of the final batch, it raises <code>StopIteration</code>.</p>
<p>But what if your code throws an exception before then?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">for</span> document <span style="color: #AA22FF; font-weight: bold">in</span> cursor:
    <span style="color: #666666">1</span> <span style="color: #666666">/</span> <span style="color: #666666">0</span>  <span style="color: #408080; font-style: italic"># Oops.</span>
</pre></div>


<p>The client-side cursor goes out of scope, but the server keeps a small amount of cursor state in memory <a href="http://docs.mongodb.org/manual/core/cursors/#closure-of-inactive-cursors">for 10 minutes</a>. PyMongo wants to clean this up promptly, by telling the server to close the cursor as soon as the client doesn't need it. The Cursor class's destructor is in charge of telling the server:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Cursor</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__del__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>alive:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_mongo_client<span style="color: #666666">.</span>close_cursor(<span style="color: #008000">self</span><span style="color: #666666">.</span>cursor_id)
</pre></div>


<p>In order to send the message to the server, PyMongo 3.0 has to do some work: it gets a lock on the internal Topology class so it can retrieve the connection pool, then it locks the pool so it can check out a socket. In PyPy, we do this work at a wholly unpredictable moment: it's whenever garbage collection is triggered. If any thread is holding either lock at this moment, the process deadlocks.</p>
<p>(Some details: By default, objects with a <code>__del__</code> method are only <a href="https://pypy.readthedocs.org/en/release-2.4.x/garbage_collection.html#minimark-gc">freed by PyPy's garbage collector during a full GC</a>, which is triggered <a href="https://pypy.readthedocs.org/en/release-2.4.x/gc_info.html#minimark-environment-variables">when memory has grown 82% since the last full GC</a>. So if you let an open cursor go out of scope, it won't be freed for some time.)</p>
<h1 id="diagnosis">Diagnosis</h1>
<p>I first found this deadlock in the unreleased code for PyMongo 3.0. Our test suite was occasionally hanging under PyPy in Jenkins. When I signaled the hanging test with Control-C it printed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Exception KeyboardInterrupt in method __del__
of &lt;pymongo.cursor.Cursor object&gt; ignored
</pre></div>


<p>The exception is "ignored" and printed to stderr, <a href="https://docs.python.org/2/reference/datamodel.html#object.__del__">as all exceptions in <code>__del__</code> are</a>. Once it printed the error, the test suite resumed and completed. So I added two bits of debugging info. First, whenever a cursor was created it stored a stack trace so it could remember where it came from. And second, if it caught an exception in <code>__del__</code>, it printed the stored traceback and the current traceback:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Cursor</span>(<span style="color: #008000">object</span>):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>tb <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;&#39;</span><span style="color: #666666">.</span>join(traceback<span style="color: #666666">.</span>format_stack())

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__del__</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>_mongo_client<span style="color: #666666">.</span>close_cursor(<span style="color: #008000">self</span><span style="color: #666666">.</span>cursor_id)
        <span style="color: #008000; font-weight: bold">except</span>:
            <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&#39;&#39;&#39;</span>
<span style="color: #BA2121">I came from:</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">.</span>
<span style="color: #BA2121">I caught:</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">.</span>
<span style="color: #BA2121">&#39;&#39;&#39;</span> <span style="color: #666666">%</span> (<span style="color: #008000">self</span><span style="color: #666666">.</span>tb, <span style="color: #BA2121">&#39;&#39;</span><span style="color: #666666">.</span>join(traceback<span style="color: #666666">.</span>format_stack()))
</pre></div>


<p>The next time the test hung, I hit Control-C and it printed something like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">I came from:
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;test/test_cursor.py&quot;</span>, line <span style="color: #666666">431</span>, in test_limit_and_batch_size
    curs <span style="color: #666666">=</span> db<span style="color: #666666">.</span>test<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>limit(<span style="color: #666666">0</span>)<span style="color: #666666">.</span>batch_size(<span style="color: #666666">10</span>)
  File <span style="color: #008000">&quot;pymongo/collection.py&quot;</span>, line <span style="color: #666666">828</span>, in find
    <span style="color: #008000; font-weight: bold">return</span> Cursor(<span style="color: #008000">self</span>, <span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)
  File <span style="color: #008000">&quot;pymongo/cursor.py&quot;</span>, line <span style="color: #666666">93</span>, in __init__
    <span style="color: #008000">self</span><span style="color: #666666">.</span>tb <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;&#39;</span><span style="color: #666666">.</span>join(traceback<span style="color: #666666">.</span>format_stack())

I caught:
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;pymongo/cursor.py&quot;</span>, line <span style="color: #666666">211</span>, in __del__
    <span style="color: #008000">self</span><span style="color: #666666">.</span>_mongo_client<span style="color: #666666">.</span>close_cursor(<span style="color: #008000">self</span><span style="color: #666666">.</span>cursor_id)
  File <span style="color: #008000">&quot;pymongo/mongo_client.py&quot;</span>, line <span style="color: #666666">908</span>, in close_cursor
    <span style="color: #008000">self</span><span style="color: #666666">.</span>_topology<span style="color: #666666">.</span>open()
  File <span style="color: #008000">&quot;pymongo/topology.py&quot;</span>, line <span style="color: #666666">58</span>, in open
    <span style="color: #008000; font-weight: bold">with</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_lock:
</pre></div>


<p>Great, so a test had left a cursor open, and about 30 tests <em>later</em> that cursor's destructor hung waiting for a lock. It only hung in PyPy, so I guessed it had something to do with the differences between CPython's and PyPy's garbage collection systems.</p>
<p>I was doing the dishes that night when my mind's background processing completed a diagnosis. As soon as I thought of it I knew I had the answer, and I wrote a test that proved it the next morning.</p>
<h1 id="the-fix">The Fix</h1>
<p>PyMongo 2's concurrency design is unsophisticated and the fix was easy. I followed the code path that leads from the cursor's destructor and saw two places it could take a lock. First, if it finds that the MongoClient was recently disconnected from the server, it briefly locks it to initiate a reconnect. <a href="https://github.com/mongodb/mongo-python-driver/commit/8ebd553">I updated that code path</a> to give up immediately if the client is disconnected&mdash;better to leave the cursor open on the server for 10 minutes than to risk a deadlock.</p>
<p>Second, if the client is <em>not</em> disconnected, the cursor destructor locks the connection pool to check out a socket. Here, there's no easy way to avoid the lock, so I came at the problem from the other side: how do I prevent a GC while the pool is locked? If the pool is never locked at the beginning of a GC, then the cursor destructor can safely lock it. The fix is here, in <code>Pool.reset</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Pool</span>:
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">reset</span>(<span style="color: #008000">self</span>):
        sockets <span style="color: #666666">=</span> <span style="color: #008000">None</span>
        <span style="color: #008000; font-weight: bold">with</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>lock:
            sockets <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets
            <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> <span style="color: #008000">set</span>()

        <span style="color: #008000; font-weight: bold">for</span> s <span style="color: #AA22FF; font-weight: bold">in</span> sockets:
            s<span style="color: #666666">.</span>close()
</pre></div>


<p>This is the one place we allocate data while the pool is locked. Allocating the new set while holding the lock could trigger a garbage collection, which could destroy a cursor, which could attempt to lock the pool <em>again</em>, and deadlock. So I moved the allocation outside the lock:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">reset</span>(<span style="color: #008000">self</span>):
        sockets <span style="color: #666666">=</span> <span style="color: #008000">None</span>
<span style="background-color: #ffffcc">        new_sockets <span style="color: #666666">=</span> <span style="color: #008000">set</span>()
</span>        <span style="color: #008000; font-weight: bold">with</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>lock:
            sockets <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets
<span style="background-color: #ffffcc">            <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets <span style="color: #666666">=</span> new_sockets
</span>
        <span style="color: #008000; font-weight: bold">for</span> s <span style="color: #AA22FF; font-weight: bold">in</span> sockets:
            s<span style="color: #666666">.</span>close()
</pre></div>


<p>Now, the two lines of <code>reset</code> that run while holding the lock can't trigger a garbage collection, so the cursor destructor knows it isn't called by a GC that interrupted this section of code.</p>
<p>And what about PyMongo 3? The new PyMongo's concurrency design is much superior, but it spends much <em>more</em> time holding a lock than PyMongo 2 does. It locks its internal Topology class whenever it reads or updates information about your MongoDB servers. This makes the deadlock trickier to fix.</p>
<p>I borrowed a technique from the MongoDB Java Driver: I deferred the job of closing cursors to a background thread. Now, when an open cursor is garbage collected, it doesn't immediately tell the server. Instead, it safely adds its ID to a list. Each MongoClient has <a href="https://github.com/mongodb/mongo-python-driver/blob/master/pymongo/periodic_executor.py">a thread that runs once a second</a> checking the list for new cursor IDs. If there are any, the thread safely takes the locks it needs to send the message to the server&mdash;unlike the garbage collector, the cursor-cleanup thread cooperates normally with your application's threads when it needs a lock.</p>
<h1 id="what-to-expect-when-youre-expiring">What To Expect When You're Expiring</h1>
<p>I already knew that a <code>__del__</code> method:</p>
<ul>
<li>Must not reference globals or builtins, <a href="/a-normal-accident-in-python-and-mod-wsgi/">see my "normal accidents" article</a>.</li>
<li>Must not access threadlocals, to avoid a refleak in Python 2.6 and older (see <a href="https://jira.mongodb.org/browse/PYTHON-353">the bug that cost me a month</a>).</li>
</ul>
<p>Now, add a third rule:</p>
<ul>
<li>It must not take a lock.</li>
</ul>
<p><a href="https://docs.python.org/2/library/weakref.html">Weakref callbacks</a> must follow these three rules, too.</p>
<h1 id="the-moral-of-the-story-is">The Moral Of The Story Is....</h1>
<p>Don't use <code>__del__</code> if you can possibly avoid it. Don't design APIs that rely on it. If you maintain a library like PyMongo that has already committed to such an API, you must follow the rules above impeccably.</p>
<hr />
<p><span style="color:gray"><em>Image: <a href="http://commons.wikimedia.org/wiki/File:Michael_Maier_Atalanta_Fugiens_Emblem_14.jpeg">Ouroboros, Michael Maier (1568&#8211;1622)</a>.</em></span></p>
