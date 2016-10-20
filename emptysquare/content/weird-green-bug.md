+++
type = "post"
title = "Weird Green Bug"
date = "2014-01-16T11:47:58"
description = "A mysterious deadlock with PyMongo and Gevent."
category = ["Mongo", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "Green_caterpillar.jpg"
draft = false
disqus_identifier = "52d76ee55393742deae448a4"
disqus_url = "https://emptysqua.re/blog/52d76ee55393742deae448a4/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Green_caterpillar.jpg" alt="Green caterpillar" title="Green caterpillar" /></p>
<p><span style="color:gray"><a href="http://commons.wikimedia.org/wiki/File:Green_caterpillar_(1).jpg">Source: Andrew Magill</a></span></p>
<p>Working on PyMongo exposes me to a vexing swarm of issues in the Python interpreter itself. I've dealt with <a href="/another-thing-about-pythons-threadlocals/">bugs in Python's threadlocals</a>, <a href="/night-of-the-living-thread/">a race condition in the Thread class</a>, and <a href="/python-c-extensions-and-mod-wsgi/">the awful things that happen when you run C extensions in multiple sub interpreters</a>.</p>
<p>Last month I was faced with a real stumper. A user reported a deadlock in the following code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey
monkey<span style="color: #666666">.</span>patch_all()

<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoReplicaSetClient
MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1&#39;</span>, use_greenlets<span style="color: #666666">=</span><span style="color: #008000">False</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;rs&#39;</span>)
</pre></div>


<p>When he hit Control-C, the exception traceback indicated the process was stuck in <code>getaddrinfo</code>. The deadlock only occurred with <code>MongoReplicaSetClient</code>, not <code>MongoClient</code>. It happened with Gevent 1.0 but not the previous version, 0.13.8. And here's the kicker: the code itself ran fine. It was when the file was <em>imported</em> that it deadlocked.</p>
<p>So I stepped through the <code>MongoReplicaSetClient</code> initialization code in PyCharm's debugger. To my surprise, the first call to <code>getaddrinfo</code> succeeded: the client acquired the IP address of "host1" and connected promptly to the MongoDB running there. So where was the deadlock?</p>
<p>Once the client connected to the first host, it asked it for a list of other hosts in the replica set. MongoDB returned the list as BSON, and PyMongo represents all BSON strings as unicode. So, whereas the first <code>getaddrinfo</code> was called on the string <code>'host1'</code>, subsequent calls were on unicodes <code>u'host2'</code>, <code>u'host3'</code>, and so on. PyMongo hung on the first attempt to resolve a unicode hostname. (This discussion is about Python 2, obviously; Gevent doesn't do Python 3 yet.)</p>
<p>I reproduced the deadlock with ever-simpler versions of the test script. I arrived at this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">gevent</span> <span style="color: #008000; font-weight: bold">import</span> monkey
monkey<span style="color: #666666">.</span>patch_all()

<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">socket</span>
socket<span style="color: #666666">.</span>getaddrinfo(
    <span style="color: #BA2121">u&#39;mongodb.org&#39;</span>,
    <span style="color: #666666">80</span>,
    socket<span style="color: #666666">.</span>AF_INET,
    socket<span style="color: #666666">.</span>SOCK_STREAM)
</pre></div>


<p>Again, the script finished promptly when I ran with it <code>python script.py</code>, but it hung when I imported it with <code>python -c "import script"</code>. Changing the unicode hostname to a <code>str</code> avoided the deadlock, as did downgrading Gevent to 0.13.8.</p>
<p>The changelog for Gevent 1.0 says that it runs <code>getaddrinfo</code> on a thread to make it asynchronous. So I tried running <code>getaddrinfo</code> on a thread, without involving Gevent at all:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">socket</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">threading</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">resolve</span>():
    <span style="color: #008000; font-weight: bold">print</span> socket<span style="color: #666666">.</span>getaddrinfo(
        <span style="color: #BA2121">u&#39;mongodb.org&#39;</span>,
        <span style="color: #666666">80</span>,
        socket<span style="color: #666666">.</span>AF_INET,
        socket<span style="color: #666666">.</span>SOCK_STREAM)

t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>resolve)
t<span style="color: #666666">.</span>start()
t<span style="color: #666666">.</span>join()
</pre></div>


<p>This script, too, hung when imported. Now that PyMongo and Gevent were both out of the picture, it looked to me like a Python bug. I looked at <a href="http://hg.python.org/cpython/file/84cf25da86e8/Modules/socketmodule.c#l4134">the implementation of Python's <code>getaddrinfo</code> wrapper</a>. What does it do differently if the hostname is unicode?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">if</span> (PyUnicode_Check(hobj)) {
    idna <span style="color: #666666">=</span> PyObject_CallMethod(
        hobj, <span style="color: #BA2121">&quot;encode&quot;</span>, <span style="color: #BA2121">&quot;s&quot;</span>, <span style="color: #BA2121">&quot;idna&quot;</span>);
    <span style="color: #008000; font-weight: bold">if</span> (<span style="color: #666666">!</span>idna)
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">NULL</span>;
    hptr <span style="color: #666666">=</span> PyString_AsString(idna);
} <span style="color: #008000; font-weight: bold">else</span> <span style="color: #008000; font-weight: bold">if</span> (PyString_Check(hobj)) {
    hptr <span style="color: #666666">=</span> PyString_AsString(hobj);
}
</pre></div>


<p>If the host object, <code>hobj</code>, is unicode, it's encoded as "idna". (That stands for <a href="http://docs.python.org/2/library/codecs.html#module-encodings.idna">Internationalized Domain Names in Applications</a> if you're curious, and I know you are.) I put some printfs in the C code and sure enough, <code>getaddrinfo</code> was hanging at the encoding step. Why? Following the call tree and sprinkling printfs throughout, I found that the hang occurred in Python's encodings module, when it tried to import <code>encodings.idna</code>. I finally understood the problem.</p>
<p>Importing <code>script.py</code> locks Python's import machinery until the import finishes. My script spawns a thread and calls <code>getaddrinfo</code> on the thread. If the hostname is unicode, <code>getaddrinfo</code> tries to encode it as "idna". If this is the first time the "idna" encoding has been used in this interpreter's life, then the thread must import <code>encodings.idna</code>, but the import machinery is locked by the main thread. The <code>getaddrinfo</code> thread waits for the import lock, while the main thread waits for the <code>getaddrinfo</code> thread to finish. Forever.</p>
<p>Gevent 1.0 is prone to this problem because it runs <code>getaddrinfo</code> on a thread. But the deadlock can be triggered without Gevent, by importing a contrived script like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">connect</span>():
    MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1&#39;</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;rs&#39;</span>)

t <span style="color: #666666">=</span> threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>connect)
t<span style="color: #666666">.</span>start()
t<span style="color: #666666">.</span>join()
</pre></div>


<p>It's just as <a href="http://docs.python.org/2/library/threading.html">the Python docs say</a>:</p>
<blockquote>
<p>Other than in the main module, an import should not have the side effect of spawning a new thread and then waiting for that thread in any way. Failing to abide by this restriction can lead to a deadlock if the spawned thread directly or indirectly attempts to import a module.</p>
</blockquote>
<p>It's obvious once you know. Even without this admonition, it's my opinion that a module shouldn't spawn threads or do network I/O when you import it. It seems like an anti-pattern.</p>
<p>But my job is to fix bugs, not give style tips. I've <a href="https://github.com/surfly/gevent/pull/350">submitted a patch to Gevent to prevent the deadlock</a>, and <a href="https://github.com/facebook/tornado/commit/6049e2db60ab0b7919622a2e52ede6442db173e8">I fixed a similar hang in Tornado</a>. Python 3.4's <code>asyncio</code> also runs <code>getaddrinfo</code> on a thread, but it can't deadlock on import, because the import machinery was rewritten in Python 3.3 with <a href="http://docs.python.org/3/whatsnew/3.3.html#a-finer-grained-import-lock">per-module locking</a>.</p>
<p>In any case there are a number of easy workarounds to this issue. <a href="https://jira.mongodb.org/browse/PYTHON-607">I've detailed them in the bug report</a>, but I'll show my favorite here:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #BA2121">u&#39;foo&#39;</span><span style="color: #666666">.</span>encode(<span style="color: #BA2121">&#39;idna&#39;</span>)
</pre></div>


<p>Do that in the main thread before any calls to <code>getaddrinfo</code>. This will cache the imported encoder and avoid importing it in a thread later on. If I were you, I'd replace "foo" with a mysterious-looking string and add a comment implying that <a href="http://www.catb.org/jargon/html/magic-story.html">the string is magic</a>, just to confound future generations.</p>
