+++
type = "post"
title = "Synchronously Build Indexes On a Whole MongoDB Replica Set"
date = "2013-07-05T15:14:58"
description = "How do you know when an index has finished building on all the members of a replica set?"
"blog/category" = ["Mongo", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
draft = false
+++

<p>I help maintain PyMongo, 10gen's Python driver for MongoDB. Mainly this means I write a lot of tests, and writing tests sometimes requires me to solve problems no normal person would encounter. I'll describe one such problem and the fix: I'm going to explain how to wait for an index build to finish on all secondary members of a replica set.</p>
<p>Normally, this is how I'd build an index on a replica set:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoReplicaSetClient(
    <span style="color: #BA2121">&#39;server0,server1,server2&#39;</span>,
    replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;replica_set_name&#39;</span>)

collection <span style="color: #666666">=</span> client<span style="color: #666666">.</span>test<span style="color: #666666">.</span>collection
collection<span style="color: #666666">.</span>create_index([(<span style="color: #BA2121">&#39;key&#39;</span>, ASCENDING)])
<span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;All done!&quot;</span>)
</pre></div>


<p>Once "All done!" is printed, I know the index has finished building on the primary. (I could pass <code>background=True</code> if I didn't want to wait for the build to finish.) Once the index is built on the primary, the primary inserts a description of the index into the <code>system.indexes</code> collection, and appends the <code>insert</code> operation to its oplog:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{
    <span style="color: #BA2121">&quot;ts&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;t&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1373049049</span>, <span style="color: #BA2121">&quot;i&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> },
    <span style="color: #BA2121">&quot;op&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;i&quot;</span>,
    <span style="color: #BA2121">&quot;ns&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;test.system.indexes&quot;</span>,
    <span style="color: #BA2121">&quot;o&quot;</span> <span style="color: #666666">:</span> {
        <span style="color: #BA2121">&quot;ns&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;test.collection&quot;</span>,
        <span style="color: #BA2121">&quot;key&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;key&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> },
        <span style="color: #BA2121">&quot;name&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;key_1&quot;</span>
    }
}
</pre></div>


<p>The <code>ts</code> is the timestamp for the operation. <code>"op": "i"</code> means this is an insert, and the <code>"o"</code> subdocument is the index description itself. The secondaries see the entry and start their own index builds.</p>
<p>But now my call to PyMongo's <code>create_index</code> returns and Python prints "All done!" In one of the tests I wrote, I couldn't start testing until the index was ready on the secondaries, too. How do I wait until then?</p>
<p>The trick is to insert the index description into <code>system.indexes</code> manually. This way I can insert with a <a href="http://docs.mongodb.org/manual/core/write-concern/">write concern</a> so I wait for the insert to be replicated:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoReplicaSetClient(
    <span style="color: #BA2121">&#39;server0,server1,server2&#39;</span>,
    replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;replica_set_name&#39;</span>)

<span style="color: #408080; font-style: italic"># Count the number of replica set members.</span>
w <span style="color: #666666">=</span> <span style="color: #666666">1</span> <span style="color: #666666">+</span> <span style="color: #008000">len</span>(client<span style="color: #666666">.</span>secondaries)

<span style="color: #408080; font-style: italic"># Manually form the index description.</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.collection</span> <span style="color: #008000; font-weight: bold">import</span> _gen_index_name
index <span style="color: #666666">=</span> {
    <span style="color: #BA2121">&#39;ns&#39;</span>: <span style="color: #BA2121">&#39;test.collection&#39;</span>,
    <span style="color: #BA2121">&#39;name&#39;</span>: _gen_index_name([(<span style="color: #BA2121">&#39;key&#39;</span>, <span style="color: #666666">1</span>)]),
    <span style="color: #BA2121">&#39;key&#39;</span>: {<span style="color: #BA2121">&#39;key&#39;</span>: ASCENDING}}

client<span style="color: #666666">.</span>test<span style="color: #666666">.</span>system<span style="color: #666666">.</span>indexes<span style="color: #666666">.</span>insert(index, w<span style="color: #666666">=</span>w)

<span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;All done!&quot;</span>)
</pre></div>


<p>Setting the <code>w</code> parameter to the number of replica set members (one primary plus N secondaries) makes <code>insert</code> wait for the operation to complete on all members. First the primary builds its index, then it adds it to its oplog, then the secondaries all start building the index. Only once all secondaries have finished building the index is the <code>insert</code> operation considered complete. Once Python prints "All done!" we know the index is finished everywhere.</p>
    