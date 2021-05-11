+++
type = "post"
title = "Real-time Profiling a MongoDB Sharded Cluster"
date = "2013-06-25T11:29:02"
description = "Let's experiment with queries and commands in a sharded cluster. We'll learn how shard keys and read preferences determine where your operations are run."
category = ["MongoDB", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "blue-shards.jpg"
draft = false
disqus_identifier = "51bf5c6e5393747680ca1ba1"
disqus_url = "https://emptysqua.re/blog/51bf5c6e5393747680ca1ba1/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="blue-shards.jpg" alt="Blue shards" title="Blue shards" border="0"   />
<span style="color: gray; font-style: italic"><a href="http://www.flickr.com/photos/cybasheep/41105405/">[Source]</a></span></p>
<p>In a sharded cluster of replica sets, which server or servers handle each of your queries? What about each insert, update, or command? If you know how a MongoDB cluster routes operations among its servers, you can predict how your application will scale as you add shards and add members to shards.</p>
<p>Operations are routed according to the type of operation, your shard key, and your read preference. Let's set up a cluster and use the system profiler to <em>see</em> where each operation is run. This is an interactive, experimental way to learn how your cluster really behaves and how your architecture will scale.</p>
<hr />
<h1 id="setup">Setup</h1>
<p>You'll need a recent install of MongoDB (I'm using 2.4.4), Python, a recent version of PyMongo (at least 2.4&mdash;I'm using 2.5.2) and the code in <a href="https://github.com/ajdavis/cluster-profile">my cluster-profile repository on GitHub</a>. If you install the <a href="https://pypi.python.org/pypi/colorama">Colorama</a> Python package you'll get cute colored output. These scripts were tested on my Mac.</p>
<h2 id="sharded-cluster-of-replica-sets">Sharded cluster of replica sets</h2>
<p>Run the <code>cluster_setup.py</code> script in my repository. It sets up a standard sharded cluster for you running on your local machine. There's a <code>mongos</code>, three config servers, and two shards, each of which is a three-member replica set. The first shard's replica set is running on ports 4000 through 4002, the second shard is on ports 5000 through 5002, and the three config servers are on ports 6000 through 6002:</p>
<p><img alt="The setup" src="https://raw.github.com/ajdavis/cluster-profile/master/_static/setup.png" title="The setup" /></p>
<p>For the finale, <code>cluster_setup.py</code> makes a collection named <code>sharded_collection</code>, sharded on a key named <code>shard_key</code>.</p>
<p>In a normal deployment, we'd let MongoDB's <a href="http://docs.mongodb.org/manual/core/sharded-clusters/#sharding-balancing">balancer</a> automatically distribute chunks of data among our two shards. But for this demo we want documents to be on predictable shards, so my script disables the balancer. It makes a chunk for all documents with <code>shard_key</code> less than 500 and another chunk for documents with <code>shard_key</code> greater than or equal to 500. It moves the high chunk to <code>replset_1</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoClient()  <span style="color: #408080; font-style: italic"># Connect to mongos.</span>
admin <span style="color: #666666">=</span> client<span style="color: #666666">.</span>admin  <span style="color: #408080; font-style: italic"># admin database.</span>

<span style="color: #408080; font-style: italic"># Pre-split.</span>
admin<span style="color: #666666">.</span>command(
    <span style="color: #BA2121">&#39;split&#39;</span>, <span style="color: #BA2121">&#39;test.sharded_collection&#39;</span>,
    middle<span style="color: #666666">=</span>{<span style="color: #BA2121">&#39;shard_key&#39;</span>: <span style="color: #666666">500</span>})

admin<span style="color: #666666">.</span>command(
    <span style="color: #BA2121">&#39;moveChunk&#39;</span>, <span style="color: #BA2121">&#39;test.sharded_collection&#39;</span>,
    find<span style="color: #666666">=</span>{<span style="color: #BA2121">&#39;shard_key&#39;</span>: <span style="color: #666666">500</span>},
    to<span style="color: #666666">=</span><span style="color: #BA2121">&#39;replset_1&#39;</span>)
</pre></div>


<p>If you connect to <code>mongos</code> with the MongoDB shell, <code>sh.status()</code> shows there's one chunk on each of the two shards:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ <span style="color: #BA2121">&quot;shard_key&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;$minKey&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> } } <span style="color: #666666">--&gt;&gt;</span> { <span style="color: #BA2121">&quot;shard_key&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">500</span> } on <span style="color: #666666">:</span> replset_0 { <span style="color: #BA2121">&quot;t&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>, <span style="color: #BA2121">&quot;i&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> }
{ <span style="color: #BA2121">&quot;shard_key&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">500</span> } <span style="color: #666666">--&gt;&gt;</span> { <span style="color: #BA2121">&quot;shard_key&quot;</span> <span style="color: #666666">:</span> { <span style="color: #BA2121">&quot;$maxKey&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">1</span> } } on <span style="color: #666666">:</span> replset_1 { <span style="color: #BA2121">&quot;t&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>, <span style="color: #BA2121">&quot;i&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">0</span> }
</pre></div>


<p>The setup script also inserts a document with a <code>shard_key</code> of 0 and another with a <code>shard_key</code> of 500. Now we're ready for some profiling.</p>
<h2 id="profiling">Profiling</h2>
<p>Run the <code>tail_profile.py</code> script from my repository. It connects to all the replica set members. On each, it sets the profiling level to 2 ("log everything") on the <code>test</code> database, and creates a <a href="http://docs.mongodb.org/manual/tutorial/create-tailable-cursor/">tailable cursor</a> on the <code>system.profile</code> collection. The script filters out some noise in the profile collection&mdash;for example, the activities of the tailable cursor show up in the <code>system.profile</code> collection that it's tailing. Any legitimate entries in the profile are spat out to the console in pretty colors.</p>
<h1 id="experiments">Experiments</h1>
<h2 id="targeted-queries-versus-scatter-gather">Targeted queries versus scatter-gather</h2>
<p>Let's run a query from Python in a separate terminal:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #408080; font-style: italic"># Connect to mongos.</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection <span style="color: #666666">=</span> MongoClient()<span style="color: #666666">.</span>test<span style="color: #666666">.</span>sharded_collection
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;shard_key&#39;</span>: <span style="color: #666666">0</span>})
<span style="color: #888888">{&#39;_id&#39;: ObjectId(&#39;51bb6f1cca1ce958c89b348a&#39;), &#39;shard_key&#39;: 0}</span>
</pre></div>


<p><code>tail_profile.py</code> prints:</p>
<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #00bebe">replset_0 primary on 4000: query test.sharded_collection {"shard_key": 0}</span><br/></p>
<p>The query includes the shard key, so <code>mongos</code> reads from the shard that can satisfy it. Adding shards can scale out your throughput on a query like this. What about a query that doesn't contain the shard key?:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({})
</pre></div>


<p><code>mongos</code> sends the query to both shards:</p>
<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #00bebe">replset_0 primary on 4000: query test.sharded_collection {"shard_key": 0}</span><br/>
<span style="font-family:monospace; font-weight: bold; font-size: 12px; color:#BA2121">replset_1 primary on 5000: query test.sharded_collection {"shard_key": 500}</span></p>
<p>For fan-out queries like this, adding more shards won't scale out your query throughput as well as it would for targeted queries, because every shard has to process every query. But we can scale throughput on queries like these by reading from secondaries.</p>
<h2 id="queries-with-read-preferences">Queries with read preferences</h2>
<p>We can use <a href="/reading-from-mongodb-replica-sets-with-pymongo/">read preferences</a> to read from secondaries:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.read_preferences</span> <span style="color: #008000; font-weight: bold">import</span> ReadPreference
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>find_one({}, read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
</pre></div>


<p><code>tail_profile.py</code> shows us that <code>mongos</code> chose a random secondary from each shard:</p>
<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: green">replset_0 secondary on 4001: query test.sharded_collection {"$readPreference": {"mode": "secondary"}, "$query": {}}</span><br/>
<span style="font-family:monospace; font-weight: bold; font-size: 12px; color: blue">replset_1 secondary on 5001: query test.sharded_collection {"$readPreference": {"mode": "secondary"}, "$query": {}}</span></p>
<p>Note how PyMongo passes the read preference to <code>mongos</code> in the query, as the <code>$readPreference</code> field. <code>mongos</code> targets one secondary in each of the two replica sets.</p>
<h2 id="updates">Updates</h2>
<p>With a sharded collection, updates must either include the shard key or be "multi-updates". An update with the shard key goes to the proper shard, of course:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>update({<span style="color: #BA2121">&#39;shard_key&#39;</span>: <span style="color: #666666">-100</span>}, {<span style="color: #BA2121">&#39;$set&#39;</span>: {<span style="color: #BA2121">&#39;field&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}})
</pre></div>


<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #00bebe">replset_0 primary on 4000: update test.sharded_collection {"shard_key": -100}</span></p>
<p><code>mongos</code> only sends the update to <code>replset_0</code>, because we put the chunk of documents with <code>shard_key</code> less than 500 there.</p>
<p>A multi-update hits all shards:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>update({}, {<span style="color: #BA2121">&#39;$set&#39;</span>: {<span style="color: #BA2121">&#39;field&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}}, multi<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #00bebe">replset_0 primary on 4000: update test.sharded_collection {}</span><br/>
<span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #BA2121">replset_1 primary on 5000: update test.sharded_collection {}</span></p>
<p>A multi-update on a range of the shard key need only involve the proper shard:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>collection<span style="color: #666666">.</span>update({<span style="color: #BA2121">&#39;shard_key&#39;</span>: {<span style="color: #BA2121">&#39;$gt&#39;</span>: <span style="color: #666666">1000</span>}}, {<span style="color: #BA2121">&#39;$set&#39;</span>: {<span style="color: #BA2121">&#39;field&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}}, multi<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #BA2121">replset_1 primary on 5000: update test.sharded_collection {"shard_key": {"$gt": 1000}}</span></p>
<p>So targeted updates that include the shard key can be scaled out by adding shards. Even multi-updates can be scaled out if they include a range of the shard key, but multi-updates without the shard key won't benefit from extra shards.</p>
<h2 id="commands">Commands</h2>
<p>In version 2.4, <code>mongos</code> can use secondaries not only for queries, but also for <a href="http://docs.mongodb.org/manual/core/read-preference/#database-commands">some commands</a>. You can run <code>count</code> on secondaries if you pass the right read preference:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find(read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>cursor<span style="color: #666666">.</span>count()
</pre></div>


<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: green">replset_0 secondary on 4001: command count: sharded_collection</span><br/>
<span style="font-family:monospace; font-weight: bold; font-size: 12px; color: blue">replset_1 secondary on 5001: command count: sharded_collection</span></p>
<p>Whereas <code>findAndModify</code>, since it modifies data, is run on the primaries no matter your read preference:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>db <span style="color: #666666">=</span> MongoClient()<span style="color: #666666">.</span>test
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>test<span style="color: #666666">.</span>command(
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #BA2121">&#39;findAndModify&#39;</span>,
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #BA2121">&#39;sharded_collection&#39;</span>,
<span style="color: #000080; font-weight: bold">... </span>    query<span style="color: #666666">=</span>{<span style="color: #BA2121">&#39;shard_key&#39;</span>: <span style="color: #666666">-1</span>},
<span style="color: #000080; font-weight: bold">... </span>    remove<span style="color: #666666">=</span><span style="color: #008000">True</span>,
<span style="color: #000080; font-weight: bold">... </span>    read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
</pre></div>


<p><span style="font-family:monospace; font-weight: bold; font-size: 12px; color: #00bebe">replset_0 primary on 4000: command findAndModify: sharded_collection</span></p>
<h1 id="go-forth-and-scale">Go Forth And Scale</h1>
<p>To scale a sharded cluster, you should understand how operations are distributed: are they scatter-gather, or targeted to one shard? Do they run on primaries or secondaries? If you set up a cluster and test your queries interactively like we did here, you can see how your cluster behaves in practice, and design your application for future growth.</p>
