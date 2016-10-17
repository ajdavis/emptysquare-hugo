+++
type = "post"
title = "Breaking Change In PyMongo"
date = "2012-12-01T20:15:48"
description = "In my excitement about the big changes in PyMongo 2.4, I forgot to mention a smaller one you should watch out for: from now on, if the initial connection to MongoDB fails, PyMongo raises ConnectionFailure instead of AutoReconnect. This is [ ... ]"
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
draft = false
+++

<p>In my excitement about <a href="/blog/pymongos-new-default-safe-writes/">the big changes in PyMongo 2.4</a>, I forgot to mention a smaller one you should watch out for: from now on, if the initial connection to MongoDB fails, PyMongo raises <code>ConnectionFailure</code> instead of <code>AutoReconnect</code>. This is a more intuitive exception to throw, but it does mean you need to change your exception handlers. If you've been doing this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">try</span>:
    connection <span style="color: #666666">=</span> Connection(<span style="color: #BA2121">&#39;mongo_host&#39;</span>)
<span style="color: #008000; font-weight: bold">except</span> AutoReconnect:
    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;Can&#39;t connect to MongoDB!&quot;</span>
</pre></div>


<p>...then you need to start catching <code>ConnectionFailure</code> from now on. This change only applies to the initial creation of <code>Connection</code> or <code>ReplicaSetConnection</code>, not to the <code>AutoReconnect</code> exceptions PyMongo raises if there's a network error on an established connection. The change <strong>does</strong> apply to PyMongo 2.4's new <code>MongoClient</code> and <code>MongoReplicaSetClient</code> classes.</p>
<p>Since <code>AutoReconnect</code> inherits from <code>ConnectionFailure</code>, you might already be catching <code>ConnectionFailure</code>. In that case, carry on.</p>
<p><a href="https://jira.mongodb.org/browse/PYTHON-396">Here's the full bug report that motivated the change.</a> This is subtle enough that I missed it a few times in PyMongo's own unittests, so check your code and make sure you're catching the right exception.</p>
    