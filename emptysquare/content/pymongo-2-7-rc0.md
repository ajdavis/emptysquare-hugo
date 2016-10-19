+++
type = "post"
title = "Announcing PyMongo 2.7 release candidate"
date = "2014-02-15T15:20:14"
description = "Try it out: \"pip install https://github.com/mongodb/mongo-python-driver/archive/2.7rc0.tar.gz\""
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "Green_leaf_leaves@240.jpg"
draft = false
legacyid = "52ffc52c5393747fe3c1d9c9"
+++

<p><a href="http://commons.wikimedia.org/wiki/File:Green_leaf_leaves.jpg"><img style="display:block; margin-left:auto; margin-right:auto;" src="Green_leaf_leaves.jpg" alt="Leaf" title="Leaf" /></a></p>
<p>Yesterday afternoon Bernie Hackett and I shipped a release candidate for PyMongo 2.7, with substantial contributions from Amalia Hawkins and Kyle Erf. This version supports new features in the upcoming MongoDB 2.6, and includes major internal improvements in the driver code. We rarely make RCs before releases, but given the scope of changes it seems wise.</p>
<p>Install the RC like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install \
  https://github.com/mongodb/mongo-python-driver/archive/2.7rc0.tar.gz
</pre></div>


<p>Please <a href="https://jira.mongodb.org/browse/PYTHON">tell us if you find bugs</a>.</p>
<h1 id="mongodb-26-support">MongoDB 2.6 support</h1>
<p>For the first time in years, the MongoDB wire protocol is changing. Bernie Hackett updated PyMongo to support the new protocol, while maintaining backwards compatibility with old servers. He also added support for MongoDB's new <code>parallelCollectionScan</code> command, which <a href="http://api.mongodb.org/python/current/api/pymongo/collection.html#pymongo.collection.Collection.parallel_scan">scans a whole collection with multiple cursors in parallel</a>.</p>
<p>Amalia Hawkins wrote a feature for <a href="http://api.mongodb.org/python/current/api/pymongo/cursor.html#pymongo.cursor.Cursor.max_time_ms">setting a server-side timeout for long-running operations</a> with the <code>max_time_ms</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">try</span>:
    <span style="color: #008000; font-weight: bold">for</span> doc <span style="color: #AA22FF; font-weight: bold">in</span> collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>max_time_ms(<span style="color: #666666">1000</span>):
        <span style="color: #008000; font-weight: bold">pass</span>
<span style="color: #008000; font-weight: bold">except</span> ExecutionTimeout:
    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;Aborted after one second.&quot;</span>
</pre></div>


<p>She also added support for the new aggregation operator, <code>$out</code>, which <a href="http://docs.mongodb.org/master/reference/operator/aggregation/out/">creates a collection directly from an aggregation pipeline</a>. While she was at it, she made PyMongo log a warning whenever your read preference is "secondary" but a command has to run on the primary:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>client <span style="color: #666666">=</span> MongoReplicaSetClient(
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #BA2121">&#39;localhost&#39;</span>,
<span style="color: #000080; font-weight: bold">... </span>    replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;repl0&#39;</span>,
<span style="color: #000080; font-weight: bold">... </span>    read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>command({<span style="color: #BA2121">&#39;reIndex&#39;</span>: <span style="color: #BA2121">&#39;collection&#39;</span>})
<span style="color: #888888">UserWarning: reindex does not support SECONDARY read preference</span>
<span style="color: #888888">and will be routed to the primary instead.</span>
<span style="color: #888888">{&#39;ok&#39;: 1}</span>
</pre></div>


<h1 id="bulk-write-api">Bulk write API</h1>
<p>Bernie added a <a href="http://api.mongodb.org/python/current/examples/bulk.html">bulk write API</a>. It's now possible to specify a series of inserts, updates, upserts, replaces, and removes, then execute them all at once:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">bulk <span style="color: #666666">=</span> db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>initialize_ordered_bulk_op()
bulk<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
bulk<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">2</span>})
bulk<span style="color: #666666">.</span>find({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})<span style="color: #666666">.</span>update({<span style="color: #BA2121">&#39;$set&#39;</span>: {<span style="color: #BA2121">&#39;foo&#39;</span>: <span style="color: #BA2121">&#39;bar&#39;</span>}})
bulk<span style="color: #666666">.</span>find({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">3</span>})<span style="color: #666666">.</span>remove()
result <span style="color: #666666">=</span> bulk<span style="color: #666666">.</span>execute()
</pre></div>


<p>PyMongo collects the operations into a minimal set of messages to the server. Compared to the old style, bulk operations have lower network costs. You can use PyMongo's bulk API with any version of MongoDB, but you only get the network advantage when talking to MongoDB 2.6.</p>
<h1 id="improved-c-code">Improved C code</h1>
<p>After great effort, I understand why our C extensions didn't like running in <code>mod_wsgi</code>. I <a href="/blog/python-c-extensions-and-mod-wsgi">wrote an explanation</a> that's more detailed than you want to read. But even better, Bernie fixed our C code so <code>mod_wsgi</code> no longer slows it down or makes it log weird warnings. Finally, I put <a href="http://api.mongodb.org/python/current/examples/mod_wsgi.html">clear configuration instructions</a> in the PyMongo docs.</p>
<p>Bernie fixed all remaining platform-specific C code. Now you can run PyMongo with its C extensions on ARM, for example if you talk to MongoDB from a Raspberry Pi.</p>
<h1 id="thundering-herd">Thundering herd</h1>
<p>I overhauled <code>MongoClient</code> so its concurrency control is closer to <a href="/blog/wasps-nest-read-copy-update-python/">what I did for <code>MongoReplicaSetClient</code> in the last release</a>. With the new MongoClient, a heavily multithreaded Python application will be much more robust in the face of network hiccups or downed MongoDB servers. You can read details in the <a href="https://jira.mongodb.org/browse/PYTHON-487">bug report</a>.</p>
<h1 id="gridfs-cursor">GridFS cursor</h1>
<p>We had several feature requests for querying <a href="http://docs.mongodb.org/manual/reference/glossary/#term-gridfs">GridFS</a> with PyMongo, so Kyle Erf implemented a GridFS cursor:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>fs <span style="color: #666666">=</span> gridfs<span style="color: #666666">.</span>GridFS(client<span style="color: #666666">.</span>db)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># Find large files:</span>
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>fs<span style="color: #666666">.</span>find({<span style="color: #BA2121">&#39;length&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: <span style="color: #666666">1024</span>}})<span style="color: #666666">.</span>count()
<span style="color: #888888">42</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># Find files whose names start with &quot;Kyle&quot;:</span>
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>pattern <span style="color: #666666">=</span> bson<span style="color: #666666">.</span>Regex(<span style="color: #BA2121">&#39;kyle.*&#39;</span>, <span style="color: #BA2121">&#39;i&#39;</span>)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>cursor <span style="color: #666666">=</span> fs<span style="color: #666666">.</span>find({<span style="color: #BA2121">&#39;filename&#39;</span>: pattern})
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">for</span> grid_out_file <span style="color: #AA22FF; font-weight: bold">in</span> cursor:
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">print</span> grid_out_file<span style="color: #666666">.</span>filename
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #888888">Kyle</span>
<span style="color: #888888">Kyle1</span>
<span style="color: #888888">Kyle Erf</span>
</pre></div>


<p>You can <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/12892">browse all 53 new features and fixes</a> in our tracker.</p>
<p>Enjoy!</p>
