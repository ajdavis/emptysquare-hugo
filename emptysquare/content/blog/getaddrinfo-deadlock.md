+++
type = "post"
title = "How To Deadlock Your Python With getaddrinfo()"
date = "2015-12-21T09:23:30"
description = "On Mac, multiprocessing plus multithreading can easily lead you to hang your process."
"blog/category" = ["C", "Mongo", "Programming", "Python"]
"blog/tag" = ["getaddrinfo"]
enable_lightbox = false
thumbnail = "spectacled-caiman@240.jpg"
draft = false
legacyid = "567793941e31ec1d4885055d"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="spectacled-caiman.jpg" alt="Spectacled caiman and American pipesnake" title="Spectacled caiman and American pipesnake" /></p>
<p>What happens if you run this code?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">os</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">socket</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">threading</span>


<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">lookup</span>():
    socket<span style="color: #666666">.</span>getaddrinfo(<span style="color: #BA2121">&#39;python.org&#39;</span>, <span style="color: #666666">80</span>)

t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>lookup)
t<span style="color: #666666">.</span>start()
<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    <span style="color: #408080; font-style: italic"># Parent waits for child.</span>
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    <span style="color: #408080; font-style: italic"># Child hangs here.</span>
    socket<span style="color: #666666">.</span>getaddrinfo(<span style="color: #BA2121">&#39;mongodb.org&#39;</span>, <span style="color: #666666">80</span>)
</pre></div>


<p>On Linux, it completes in milliseconds. On Mac, it usually hangs. Why?</p>
<hr />
<h1 id="journey-to-the-center-of-the-interpreter">Journey To The Center Of The Interpreter</h1>
<p>Anna Herlihy and I tackled this question a few months ago. It didn't look like the code example above&mdash;not at first. We'd come across an article by Anthony Fejes reporting that the new PyMongo 3.0 didn't work with his software, which combined multithreading with multiprocessing. Often, he'd create a MongoClient, then fork, and in the child process the MongoClient couldn't connect to any servers:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">os</span>

<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient


client <span style="color: #666666">=</span> MongoClient()
<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    <span style="color: #408080; font-style: italic"># Parent waits for child.</span>
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    <span style="color: #408080; font-style: italic"># After 30 sec, &quot;ServerSelectionTimeoutError: No servers found&quot;.</span>
    client<span style="color: #666666">.</span>admin<span style="color: #666666">.</span>command(<span style="color: #BA2121">&#39;ping&#39;</span>)
</pre></div>


<p>In PyMongo 3, a MongoClient begins connecting to your server with a background thread. This lets it parallelize the connections if there are several servers, and it prevents your code from blocking, even if some of the connections are slow. This worked fine, except in Anthony Fejes's scenario: when the MongoClient constructor was immediately followed by a <code>fork</code>, the MongoClient was broken in the child process.</p>
<p>Anna investigated. She could reproduce the timeout on her Mac, but not on a Linux box.</p>
<p>She descended through PyMongo's layers using the PyCharm debugger and print statements, and found that the child process hung when it tried to open its first connection to MongoDB. It reached this line and stopped cold:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">infos = socket.getaddrinfo(host, port)
</pre></div>


<p>It reminded me of the <code>getaddrinfo</code> quirk I'd learned about during a side-trip while I was <a href="/blog/weird-green-bug/">debugging a completely unrelated <code>getaddrinfo</code> deadlock last year</a>. The quirk is this: on some platforms, Python locks around <code>getaddrinfo</code> calls, allowing only one thread to resolve a name at a time. In Python's standard socketmodule.c:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic">/* On systems on which getaddrinfo() is believed to not be thread-safe,</span>
<span style="color: #408080; font-style: italic">   (this includes the getaddrinfo emulation) protect access with a lock. */</span>
<span style="color: #BC7A00">#if defined(WITH_THREAD) &amp;&amp; (defined(__APPLE__) || \</span>
<span style="color: #BC7A00">    (defined(__FreeBSD__) &amp;&amp; __FreeBSD_version+0 &lt; 503000) || \</span>
<span style="color: #BC7A00">    defined(__OpenBSD__) || defined(__NetBSD__) || \</span>
<span style="color: #BC7A00">    defined(__VMS) || !defined(HAVE_GETADDRINFO))</span>
<span style="color: #BC7A00">#define USE_GETADDRINFO_LOCK</span>
<span style="color: #BC7A00">#endif</span>
</pre></div>


<p>So Anna added some printfs in socketmodule.c, rebuilt her copy of CPython on Mac, and descended yet deeper into the layers. Sure enough, the interpreter deadlocks here in the child process:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">static</span> PyObject <span style="color: #666666">*</span>
<span style="color: #0000FF">socket_getaddrinfo</span>(PyObject <span style="color: #666666">*</span>self, PyObject <span style="color: #666666">*</span>args)
{
    <span style="color: #408080; font-style: italic">/* ... */</span>
    Py_BEGIN_ALLOW_THREADS
    printf(<span style="color: #BA2121">&quot;getting gai lock...</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&quot;</span>);
<span style="background-color: #ffffcc">    ACQUIRE_GETADDRINFO_LOCK
</span>    printf(<span style="color: #BA2121">&quot;got gai lock</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&quot;</span>);
    error <span style="color: #666666">=</span> getaddrinfo(hptr, pptr, <span style="color: #666666">&amp;</span>hints, <span style="color: #666666">&amp;</span>res0);
    Py_END_ALLOW_THREADS
    RELEASE_GETADDRINFO_LOCK
</pre></div>


<p>The macro <code>Py_BEGIN_ALLOW_THREADS</code> drops the Global Interpreter Lock, so other Python threads can run while this one waits for <code>getaddrinfo</code>. Then, depending on the platform, <code>ACQUIRE_GETADDRINFO_LOCK</code> does nothing (Linux) or grabs a lock (Mac). Once <code>getaddrinfo</code> returns, this code first reacquires the Global Interpreter Lock, then drops the <code>getaddrinfo</code> lock (if there is one).</p>
<p>So, on Linux, these lines allow concurrent hostname lookups. On Mac, only one thread can wait for <code>getaddrinfo</code> at a time. But why does forking cause a total deadlock?</p>
<h1 id="diagnosis">Diagnosis</h1>
<p>Consider our original example:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">lookup</span>():
    socket<span style="color: #666666">.</span>getaddrinfo(<span style="color: #BA2121">&#39;python.org&#39;</span>, <span style="color: #666666">80</span>)

t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>lookup)
t<span style="color: #666666">.</span>start()
<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    <span style="color: #408080; font-style: italic"># Parent waits for child.</span>
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    <span style="color: #408080; font-style: italic"># Child hangs here.</span>
    socket<span style="color: #666666">.</span>getaddrinfo(<span style="color: #BA2121">&#39;mongodb.org&#39;</span>, <span style="color: #666666">80</span>)
</pre></div>


<p>The <code>lookup</code> thread starts, drops the Global Interpreter Lock, grabs the <code>getaddrinfo</code> lock, and waits for <code>getaddrinfo</code>. Since the GIL is available, the main thread takes it and resumes. The main thread's next call is <code>fork</code>.</p>
<p>When a process forks, only the thread that called <code>fork</code> is copied into the child process. Thus in the child process, the main thread continues and the <code>lookup</code> thread is gone. But that was the thread holding the <code>getaddrinfo</code> lock! In the child process, the <code>getaddrinfo</code> lock will never be released&mdash;the thread whose job it was to release it is kaput.</p>
<p>In this stripped-down example, the next event is the child process calling <code>getaddrinfo</code> on the main thread. The <code>getaddrinfo</code> lock is never released, so the process simply deadlocks. In the actual PyMongo scenario, the main thread isn't blocked, but whenever it tries to use a MongoDB server it times out. Anna explained, "in the child process, the <code>getaddrinfo</code> lock will never be unlocked&mdash;the thread that locked it was not copied to the child&mdash;so the background thread can never resolve the server's hostname and connect. The child's main thread will then time out."</p>
<p>(A digression: If this were a C program it would switch threads unpredictably, and it would not always deadlock. Sometimes the <code>lookup</code> thread would finish <code>getaddrinfo</code> before the main thread forked, sometimes not. But in Python, thread switching is infrequent and predictable. Threads are allowed to switch every 1000 bytecodes in Python 2, or every 15 ms in Python 3. If multiple threads are waiting for the GIL, they will tend to switch every time they drop the GIL with <code>Py_BEGIN_ALLOW_THREADS</code> and wait for a C call like <code>getaddrinfo</code>. So in Python, the deadlock is practically deterministic.)</p>
<h1 id="verification">Verification</h1>
<p>Anna and I had our hypothesis. But could we prove it?</p>
<p>One test was, if we waited until the background thread had probably dropped the <code>getaddrinfo</code> lock before we forked, we shouldn't see a deadlock. Indeed, we avoided the deadlock if we added a tiny sleep before the fork:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoClient()
<span style="background-color: #ffffcc">time<span style="color: #666666">.</span>sleep(<span style="color: #666666">0.1</span>)
</span><span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    <span style="color: #408080; font-style: italic"># ... and so on ...</span>
</pre></div>


<p>We read the <code>ifdef</code> in sockmodule.c again and devised another way to verify our hypothesis: we should deadlock on Mac and OpenBSD, but not Linux or FreeBSD. We created a few kinds of virtual machines and voil&agrave;, they deadlocked or didn't, as expected.</p>
<p>(Windows would deadlock too, except Python on Windows can't fork.)</p>
<h1 id="why-now">Why Now?</h1>
<p>Why was this bug reported in PyMongo 3, and not our previous driver version PyMongo 2?</p>
<p>PyMongo 2 had a simpler, less concurrent design: if you create a single MongoClient it spawns no background threads, so you can <code>fork</code> safely.</p>
<p>The old PyMongo 2 MongoReplicaSetClient did use a background thread, but its constructor blocked until the background thread completed its connections. This code was slow but fairly safe:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Blocks until initial connections are done.</span>
client <span style="color: #666666">=</span> MongoReplicaSetClient(hosts, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&quot;rs&quot;</span>)

<span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    client<span style="color: #666666">.</span>admin<span style="color: #666666">.</span>command(<span style="color: #BA2121">&#39;ping&#39;</span>)
</pre></div>


<p>In PyMongo 3, however, MongoReplicaSetClient is gone. MongoClient now handles connections to single servers or replica sets. The new client's constructor spawns one or more threads to begin connecting, and it returns immediately instead of blocking. Thus, a background thread is <em>usually</em> holding the <code>getaddrinfo</code> lock while the main thread executes its next few statements.</p>
<h1 id="just-dont-do-that-then">Just Don't Do That, Then</h1>
<p>Unfortunately, there is no real solution to this bug. We won't go back to the old single-threaded, blocking MongoClient&mdash;the new code's advantages are too great. Besides, even the slow old code didn't make it completely safe to fork. You were less <em>likely</em> to fork while a thread was holding the <code>getaddrinfo</code> lock, but if you used MongoReplicaSetClient the risk of deadlock was always there.</p>
<p>Anna and I decided that the use-case for forking right after constructing a MongoClient isn't common or necessary, anyway. You're better off forking first:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    <span style="color: #408080; font-style: italic"># Safe to create the client in the child process.</span>
    client <span style="color: #666666">=</span> MongoClient()
    client<span style="color: #666666">.</span>admin<span style="color: #666666">.</span>command(<span style="color: #BA2121">&#39;ping&#39;</span>)
</pre></div>


<p>Forking first is a good idea with PyMongo or any other network library&mdash;it's terribly hard to make libraries fork-proof, best not to risk it.</p>
<p>If you must create the client first, you can tell it not to start its background threads until needed, like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="background-color: #ffffcc">client <span style="color: #666666">=</span> MongoClient(connect<span style="color: #666666">=</span><span style="color: #008000">False</span>)
</span><span style="color: #008000; font-weight: bold">if</span> os<span style="color: #666666">.</span>fork():
    os<span style="color: #666666">.</span>wait()
<span style="color: #008000; font-weight: bold">else</span>:
    <span style="color: #408080; font-style: italic"># Threads start on demand and connect to server.</span>
    client<span style="color: #666666">.</span>admin<span style="color: #666666">.</span>command(<span style="color: #BA2121">&#39;ping&#39;</span>)
</pre></div>


<h1 id="warning-deadlock-ahead">Warning, Deadlock Ahead!</h1>
<p>We had convenient workarounds. But how do we prevent the next user like Anthony from spending days debugging this?</p>
<p>Anna found a way to detect if MongoClient was being used riskily and print a warning from the child process:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    UserWarning: MongoClient opened before fork. Create MongoClient
    with connect=False, or create client after forking. See PyMongo&#39;s
    documentation for details:

    http://bit.ly/pymongo-faq#using-pymongo-with-multiprocessing    
</pre></div>


<p>We shipped this fix with PyMongo 3.1 in November.</p>
<hr />
<p>Next time: the <code>getaddrinfo</code> lock strikes again, <a href="/blog/mac-python-getaddrinfo-queueing/">causing spurious timeouts when connecting to localhost</a>.</p>
<p>References:</p>
<ul>
<li><a href="https://jira.mongodb.org/browse/PYTHON-961">Anthony Fejes's bug report</a></li>
<li><a href="https://hg.python.org/cpython/file/d2b8354e87f5/Modules/socketmodule.c#l187">The <code>getaddrinfo</code> lock in socketmodule.c</a></li>
<li><a href="https://github.com/mongodb/mongo-python-driver/commit/07ff7ea721cda71e6adaa2f5dbc78928f116501b#diff-03c28c992fc572c14be4a1b39cb26850R68">Anna's fix</a></li>
<li><a href="http://bit.ly/pymongo-faq#using-pymongo-with-multiprocessing">Her FAQ entry</a></li>
</ul>
<hr />
<p><a href="http://www.oldbookillustrations.com/illustrations/spectacled-caiman/"><span style="color:gray">Image: Spectacled Caiman and American Pipe Snake</span></a></p>
    