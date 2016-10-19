+++
type = "post"
title = "PyMongo 2.6.2 Released"
date = "2013-09-07T12:10:18"
description = "Yesterday we released PyMongo 2.6.2, which fixes a bug when max_pool_size is None."
category = ["Mongo", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "522b4f475393741a66f6f481"
disqus_url = "https://emptysqua.re/blog/522b4f475393741a66f6f481/"
+++

<p>Bernie Hackett and I released <a href="https://pypi.python.org/pypi/pymongo/2.6.2">PyMongo 2.6.2</a> yesterday. We fixed <a href="https://jira.mongodb.org/browse/PYTHON-566">a bug</a> when <code>max_pool_size</code> is <code>None</code>.</p>
<p><code>max_pool_size</code> is normally an integer, but it's set to <code>None</code> if you're still using one of the deprecated classes, <code>Connection</code> or <code>ReplicaSetConnection</code>, instead of the new classes <code>MongoClient</code> and <code>MongoReplicaSetClient</code>. It so happens that in Python 2, <code>None</code> is less than all integers, so this comparison in our connection pool is wrong, but doesn't raise:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">return_socket</span>(<span style="color: #008000">self</span>, sock):
    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">len</span>(<span style="color: #008000">self</span><span style="color: #666666">.</span>sockets) <span style="color: #666666">&lt;</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>max_size:
        <span style="color: #008000">self</span><span style="color: #666666">.</span>sockets<span style="color: #666666">.</span>add(sock)
</pre></div>


<p>In Python 3 this raises:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">TypeError<span style="color: #666666">:</span> unorderable types<span style="color: #666666">:</span> int<span style="color: #666666">()</span> <span style="color: #666666">&lt;</span> NoneType<span style="color: #666666">()</span>
</pre></div>


<p>Some third-party libraries like Kombu are compatible with Python 3, but <a href="https://github.com/celery/kombu/issues/250">still use the old PyMongo connection classes</a>, revealing this bug.</p>
<p>If you use the old classes directly or via a third-party library, or if you set <code>max_pool_size</code> to <code>None</code> in your own code, please upgrade immediately to get proper connection pooling.</p>
