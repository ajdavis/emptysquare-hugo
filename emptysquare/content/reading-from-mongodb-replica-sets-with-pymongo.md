+++
type = "post"
title = "Reading from MongoDB Replica Sets with PyMongo"
date = "2012-12-06T08:15:02"
description = ""
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "bookwheel@240.jpg"
draft = false
disqus_identifier = "50c014485393745fa585a1ca"
disqus_url = "https://emptysqua.re/blog/50c014485393745fa585a1ca/"
+++

<p><a href="http://en.wikipedia.org/wiki/Bookwheel"><img style="display:block; margin-left:auto; margin-right:auto;" src="bookwheel.jpg" alt="Book Wheel" title="bookwheel.jpg" border="0"   /></a></p>
<p>Read preferences are a new feature in MongoDB 2.2 that lets you finely control how queries are routed to replica set members. With fine control comes complexity, but fear not: I'll explain how to use read preferences to route your queries with PyMongo.</p>
<p>(I helped write 10gen's spec for read preferences, and I did the implementation for PyMongo 2.3.)</p>
<hr />
<p>Contents:</p>
<ul>
<li><a href="#problem">The Problem</a></li>
<li><a href="#read-preferences">Read Preferences</a></li>
<li><a href="#algorithm">The Algorithm</a></li>
<li><a href="#code">Finally, Some Code</a></li>
<li><a href="#slave_okay">Remember slave_okay?</a></li>
<li><a href="#commands">Commands</a></li>
<li><a href="#sharding">Sharding</a></li>
<li><a href="#use-cases">Use Cases</a></li>
<li><a href="#monitoring">Monitoring</a></li>
<li><a href="#conclusion">In Conclusion</a></li>
</ul>
<h2 id="the-problem"><a id="problem"></a>The Problem</h2>
<p>Which member of a replica set should PyMongo use for a <code>find</code>, or for a read-only command like <code>count</code>? Should it query the primary or a secondary? If it queries a secondary, which one should it use? How can you control this choice?</p>
<p>When your application queries a replica set, you have the opportunity to trade off consistency, availability, latency, and throughput for each kind of query. This is the problem that read preferences solve: how to specify your preferences among these four variables, so you read from the best member of the replica set for each query.</p>
<p>First I'll describe what a read preference is. Then I'll show PyMongo's algorithm for choosing a member. Finally, I'll discuss a list of use cases and recommend a read preference to use for each.</p>
<h2 id="read-preferences"><a id="read-preferences"></a>Read Preferences</h2>
<p>A read preference has three parts:</p>
<p><strong>Mode</strong>. This determines whether to read from the primary or secondaries. There are five modes:</p>
<ul>
<li><code>PRIMARY</code>: The default mode. Always read from the primary. If there's no primary raise an exception, "AutoReconnect: No replica set primary available for query".</li>
<li><code>SECONDARY</code>: read from a secondary if there is one, otherwise raise an exception: <code>AutoReconnect: No replica set secondary available for query</code>. PyMongo prefers secondaries with short ping times.</li>
<li><code>PRIMARY_PREFERRED</code>: read from the primary if there is one, otherwise a secondary.</li>
<li><code>SECONDARY_PREFERRED</code>: read from a secondary if there is one, otherwise the primary. Again, low-latency secondaries are preferred.</li>
<li><code>NEAREST</code>: read from any low-latency member.</li>
</ul>
<p><a id="tag-sets"></a><strong>Tag Sets</strong>. If you've <a href="http://www.mongodb.org/display/DOCS/Data+Center+Awareness#DataCenterAwareness-Tagging%28version2.0%29">tagged your replica set members</a>, you can use tags to specify which members to read from. Let's say you've tagged your members according to which data centers they're in. Your replica-set config is like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{
    _id <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;someSet&quot;</span>,
    members <span style="color: #666666">:</span> [
        {_id <span style="color: #666666">:</span> <span style="color: #666666">0</span>, host <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;A&quot;</span>, tags <span style="color: #666666">:</span> {<span style="color: #BA2121">&quot;dc&quot;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&quot;ny&quot;</span>}},
        {_id <span style="color: #666666">:</span> <span style="color: #666666">1</span>, host <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;B&quot;</span>, tags <span style="color: #666666">:</span> {<span style="color: #BA2121">&quot;dc&quot;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&quot;ny&quot;</span>}},
        {_id <span style="color: #666666">:</span> <span style="color: #666666">2</span>, host <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;C&quot;</span>, tags <span style="color: #666666">:</span> {<span style="color: #BA2121">&quot;dc&quot;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&quot;sf&quot;</span>}},
        {_id <span style="color: #666666">:</span> <span style="color: #666666">3</span>, host <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;D&quot;</span>, tags <span style="color: #666666">:</span> {<span style="color: #BA2121">&quot;dc&quot;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&quot;sf&quot;</span>}},
        {_id <span style="color: #666666">:</span> <span style="color: #666666">4</span>, host <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;E&quot;</span>, tags <span style="color: #666666">:</span> {<span style="color: #BA2121">&quot;dc&quot;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&quot;uk&quot;</span>}}
    ]
}
</pre></div>


<p>You could configure PyMongo to use this array of tag sets:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">[{<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;ny&#39;</span>}, {<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span><span style="color: #BA2121">&#39;sf&#39;</span>}, {}]
</pre></div>


<p>The driver searches through the array, from first tag set to last, looking for a tag set that matches one or more members. So if any members are online that match <code>{'dc': 'ny'}</code>, the driver picks among them, preferring those with the shortest ping times. If no members match <code>{'dc': 'ny'}</code>, PyMongo looks for members matching <code>{'dc':'sf'}</code>, and so on down the list.</p>
<p>The final, empty tag set <code>{}</code> means, "read from any member regardless of tags." It's a fail-safe. If you would rather raise an exception than read from a member that doesn't match a tag set, omit the empty set from the end of the array:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">[{<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;ny&#39;</span>}, {<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span><span style="color: #BA2121">&#39;sf&#39;</span>}]
</pre></div>


<p>In this case, if all members in New York and San Francisco are down, PyMongo will raise an exception instead of trying the member in the UK.</p>
<p>You can have multiple tags in a set. A member has to match all the tags. E.g., if your array of tag sets is like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">[{<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;ny&#39;</span>, <span style="color: #BA2121">&#39;disk&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;ssd&#39;</span>}]
</pre></div>


<p>... then only a member tagged <strong>both</strong> with <code>'dc': 'ny'</code> and with <code>'disk': 'ssd'</code> is a match. A member's extra tags, like <code>'rack': 2</code>, have no effect.</p>
<p>Each mode interacts a little differently with tag sets:</p>
<ul>
<li><code>PRIMARY</code>: You can't combine tag sets with PRIMARY. After all, there's only one primary, so it's senseless to ask for a primary with particular tags.</li>
<li><code>PRIMARY_PREFERRED</code>: If the primary is up, read from it no matter how it's tagged. If the primary is down, read from a secondary matching the tags provided. If there is no such secondary, raise an error.</li>
<li><code>SECONDARY</code>: Read from a secondary that matches the first tag set for which there are any matches.</li>
<li><code>SECONDARY_PREFERRED</code>: Like <code>SECONDARY</code>, or if there are no matching secondaries, like <code>PRIMARY</code>.</li>
<li><code>NEAREST</code>: Like <code>SECONDARY</code>, but treat the primary the same as the secondaries.</li>
</ul>
<p><a id="ping-time"></a><strong>secondary_acceptable_latency_ms</strong>. PyMongo tracks each member's ping time (see <a href="#monitoring">monitoring</a> below) and queries only the "nearest" member, or any random member no more than 15ms "farther" than it.</p>
<p>Say you have members who are 10, 20, and 30 milliseconds away:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="servers.png" alt="Servers" title="servers.png" border="0"   /></p>
<p>PyMongo distributes queries evenly between the 10- and 20-millisecond member. It excuses the 30-millisecond member, because it's more than 15ms farther than the closest member. You can override the 15ms default by setting the snappily-named <code>secondary_acceptable_latency_ms</code> option.</p>
<h2 id="the-algorithm"><a id="algorithm"></a>The Algorithm</h2>
<p>PyMongo chooses a member using the three parts of a read preference as a three-stage filter, removing ineligible members at each stage. For <code>PRIMARY</code>, the driver just picks the primary, or if there's no primary, raises an exception. For <code>SECONDARY</code> and <code>NEAREST</code>:</p>
<ol>
<li>Apply the mode. For <code>SECONDARY</code>, filter out the primary and continue. For <code>NEAREST</code>, keep all the members and continue.</li>
<li>Apply the tag sets. If there are no tag sets configured, then pass all the members to the next stage. Otherwise, search through the array of tag sets looking for a tag set that matches some members, and pass those members to the next stage.</li>
<li>Apply ping times. First, find the nearest member who's survived filtration so far. Then filter out any members more than 15ms farther.</li>
</ol>
<p>If several members are left at the end of the final stage, the driver picks one at random and sends it your query.</p>
<p><code>PRIMARY_PREFERRED</code> uses the primary if there is one, otherwise it runs the <code>SECONDARY</code> algorithm.</p>
<p><code>SECONDARY_PREFERRED</code> first runs the <code>SECONDARY</code> algorithm, and if there's no member left at the end, it uses the primary.</p>
<p>I can hear your objections: "It's complicated," you say. It <em>is</em> a bit complicated, but we chose this algorithm because we think it can be configured to work for any use-case you throw at it. (See <a href="#use-cases">use cases</a> below.) "It's expensive," you object. The algorithm is cheaper than it sounds because it does no I/O at all. It just uses what it already knows about your replica set from periodic <a href="#monitoring">monitoring</a>.</p>
<h2 id="finally-some-code"><a id="code"></a>Finally, Some Code</h2>
<p>Let's actually use read preferences with PyMongo. The simplest method is to configure a MongoReplicaSetClient. By default, the mode is <code>PRIMARY</code>, the tag sets are empty, and <code>secondary_acceptable_latency_ms</code> is 15ms:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.mongo_replica_set_client</span> <span style="color: #008000; font-weight: bold">import</span> MongoReplicaSetClient

rsc <span style="color: #666666">=</span> MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1,host2,host3&#39;</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>)
</pre></div>


<p>You can override any of these options with keyword arguments.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.mongo_replica_set_client</span> <span style="color: #008000; font-weight: bold">import</span> MongoReplicaSetClient
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.read_preferences</span> <span style="color: #008000; font-weight: bold">import</span> ReadPreference

rsc <span style="color: #666666">=</span> MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1,host2,host3&#39;</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>,
    read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY_PREFERRED,
    tag_sets<span style="color: #666666">=</span>[{<span style="color: #BA2121">&#39;dc&#39;</span>: <span style="color: #BA2121">&#39;ny&#39;</span>}, {}],
    secondary_acceptable_latency_ms<span style="color: #666666">=50</span>)
</pre></div>


<p>(Note that what I'm calling the "mode" is configured with the <code>read_preference</code> option.)</p>
<p>If you initialize a MongoReplicaSetClient like this then all reads use the mode, tag sets, and latency you've configured. You can also override any of these three options post-hoc:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsc <span style="color: #666666">=</span> MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1,host2,host3&#39;</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>)
rsc<span style="color: #666666">.</span>read_preference <span style="color: #666666">=</span> ReadPreference<span style="color: #666666">.</span>NEAREST
rsc<span style="color: #666666">.</span>tag_sets <span style="color: #666666">=</span> [{<span style="color: #BA2121">&#39;disk&#39;</span>: <span style="color: #BA2121">&#39;ssd&#39;</span>}]
rsc<span style="color: #666666">.</span>secondary_acceptable_latency_ms <span style="color: #666666">=</span> <span style="color: #666666">1000</span>
</pre></div>


<p>You can do the same when accessing a database from a MongoReplicaSetClient:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db <span style="color: #666666">=</span> rsc<span style="color: #666666">.</span>my_database
db<span style="color: #666666">.</span>read_preference <span style="color: #666666">=</span> ReadPreference<span style="color: #666666">.</span>SECONDARY
</pre></div>


<p>Or a collection:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">collection <span style="color: #666666">=</span> db<span style="color: #666666">.</span>my_collection
collection<span style="color: #666666">.</span>tag_sets <span style="color: #666666">=</span> [{<span style="color: #BA2121">&#39;dc&#39;</span>: <span style="color: #BA2121">&#39;cloud&#39;</span>}]
</pre></div>


<p>You can even set your preference on individual method calls:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">results <span style="color: #666666">=</span> <span style="color: #008000">list</span>(
    collection<span style="color: #666666">.</span>find({}, secondary_acceptable_latency_ms<span style="color: #666666">=0</span>))

document <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find_one(
    {<span style="color: #BA2121">&#39;field&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}, read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>NEAREST)
</pre></div>


<p>Each of these four levels&mdash;connection, database, collection, method&mdash;inherits the options of the previous level and allows you to override them.</p>
<p>(Further reading: <a href="http://api.mongodb.org/python/current/api/pymongo/index.html#pymongo.read_preferences.ReadPreference">PyMongo read preferences</a>, <a href="http://api.mongodb.org/python/current/examples/high_availability.html">PyMongo's MongoReplicaSetClient</a>.)</p>
<h2 id="remember-slave_okay"><a id="slave_okay"></a>Remember slave_okay?</h2>
<p>The old ReplicaSetConnection had a <code>slave_okay</code> option. That's deprecated now, but it still works. It's treated like <code>SECONDARY_PREFERRED</code>.</p>
<h2 id="commands"><a id="commands"></a>Commands</h2>
<p>Some commands like <code>findAndModify</code> write data, others like <code>count</code> only read it. The read-only commands obey your read preference, the rest are always sent to the primary. Here are the commands that obey read preferences:</p>
<ul>
<li>count</li>
<li>distinct</li>
<li>group</li>
<li>aggregate</li>
<li>inline mapreduce</li>
<li>collStats, dbStats</li>
<li>geoNear, geoSearch, geoWalk</li>
</ul>
<p>If you want, you can override the read preference while executing an individual command:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">stats <span style="color: #666666">=</span> rsc<span style="color: #666666">.</span>my_database<span style="color: #666666">.</span>command(
    <span style="color: #BA2121">&#39;dbStats&#39;</span>, read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
</pre></div>


<h2 id="sharding"><a id="sharding"></a>Sharding</h2>
<p>When you run <code>find</code> on a sharded cluster of replica sets, PyMongo sends your read preference to mongos. E.g., if you do a query like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">collection<span style="color: #666666">.</span>find(
    {<span style="color: #BA2121">&#39;field&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>},
    read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY_PREFERRED,
    tag_sets<span style="color: #666666">=</span>[{<span style="color: #BA2121">&#39;dc&#39;</span>: <span style="color: #BA2121">&#39;ny&#39;</span>}, {}])
</pre></div>


<p>Then PyMongo sends a query to mongos like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{
    $query<span style="color: #666666">:</span> {field<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;value&#39;</span>},
    $readPreference<span style="color: #666666">:</span> {
        mode<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;secondaryPreferred&#39;</span>,
        tags<span style="color: #666666">:</span> [{<span style="color: #BA2121">&#39;dc&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;ny&#39;</span>}, {}],
    }
}
</pre></div>


<p>Mongos interprets this <code>$readPreference</code> field and applies the read-preference logic to each replica set in the sharded cluster.</p>
<p>There are two limitations:</p>
<ol>
<li>You can't override mongos's <code>secondary_acceptable_latency_ms</code>, only its mode and tag sets.</li>
<li><a href="https://jira.mongodb.org/browse/SERVER-10947">You can't send the <code>text</code> command to secondaries</a>. This will probably remain unfixed, since we plan for <a href="https://jira.mongodb.org/browse/SERVER-9063">the <code>text</code> command to be superseded by the <code>$text</code> query operator</a>, which <strong>will</strong> run on secondaries in a sharded cluster as expected.</li>
</ol>
<h2 id="use-cases"><a id="use-cases"></a>Use Cases</h2>
<p><strong>I want maximum consistency.</strong> By "consistency" you mean you don't want stale reads under any circumstances. As soon as you've modified some data, you want all your reads to reflect the change. In this case use <code>PRIMARY</code>, and be aware that when you have no primary (e.g. during an election, or if a majority of the replica set is offline) that every query will raise an exception.</p>
<p><strong>I want maximum availability.</strong> You want to be able to query if possible. Use <code>PRIMARY_PREFERRED</code>: when there's a primary you'll get consistent reads, but if there's no primary you can query secondaries. I like this option, because it lets your app stay online, read-only, during a failover. Be careful to test that your app behaves well under these circumstances, obviously.</p>
<p><strong>I want minimum latency.</strong> Use <code>NEAREST</code>. The driver or mongos will read from the fastest member and those within 15ms of it. Be aware that you risk inconsistency: if the nearest member to your app server is a secondary with some <a href="http://docs.mongodb.org/manual/administration/replica-sets/#replica-set-replication-lag">replication lag</a>, you could read stale data. Also note that <code>NEAREST</code> merely minimizes network lag, rather than reading from the member with the lowest IO or CPU load.</p>
<p><strong>I use replica sets to distribute my data.</strong> If you have a replica set with members spread around the globe, you can tag them like in the <a href="#tag-sets">tag sets</a> example above. Then, configure your application servers to query the members nearby. For example, your New York app servers do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsc<span style="color: #666666">.</span>read_preference <span style="color: #666666">=</span> ReadPreference<span style="color: #666666">.</span>NEAREST
rsc<span style="color: #666666">.</span>tag_sets <span style="color: #666666">=</span> [{<span style="color: #BA2121">&#39;dc&#39;</span>: <span style="color: #BA2121">&#39;ny&#39;</span>}, {}]
</pre></div>


<p>Although <code>NEAREST</code> favors nearby secondaries anyway, including the tag makes the choice more predictable.</p>
<p><strong>I want maximum throughput.</strong> Use <code>NEAREST</code> and set <code>secondary_acceptable_latency_ms</code> very high, like 500ms. This will distribute the query load equally among all members, thus (under most circumstances) giving you maximum read throughput.</p>
<p>If you want to move read load off your primary, use mode <code>SECONDARY</code>. It's tempting to use <code>SECONDARY_PREFERRED</code>, but if your primary can't take your full read load, you probably prefer for your queries to fail than to move all the load to the primary whenever your secondaries are unavailable.</p>
<h2 id="monitoring"><a id="monitoring"></a>Monitoring</h2>
<p>PyMongo needs to know a lot about the state of your replica set to know which members to use for your read preference.
If you create a MongoReplicaSetClient like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">rsc <span style="color: #666666">=</span> MongoReplicaSetClient(<span style="color: #BA2121">&#39;host1,host2,host3&#39;</span>, replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>)
</pre></div>


<p>...then the MongoReplicaSetClient tries to connect to each server, in random order, until it finds one that's up. It runs the <a href="http://docs.mongodb.org/manual/reference/commands/#isMaster"><code>isMaster</code> command</a> on that server. The server's response tells the MongoReplicaSetClient which members are in the replica set now, how they're tagged, and who's primary. MongoReplicaSetClient then calls <code>isMaster</code> on each member currently in the set and records the latency. This is what I called "<a href="#ping-time">ping time</a>" above.</p>
<p>Once all that's complete, the MongoReplicaSetClient launches a background thread called the Monitor. The Monitor wakes every 30 seconds and refreshes its view of the replica set: it runs <code>isMaster</code> on all the members again, marks as "down" any members it can't reach, and notes new members who've joined. It also updates its latency measurement for each member. It uses a 5-sample moving average to track each member's latency.</p>
<p>If a member goes down, MongoReplicaSetClient won't take 30 seconds to notice. As soon as it gets a network error attempting to query a member it thought was up, it wakes the Monitor to refresh ASAP.</p>
<h2 id="in-conclusion"><a id="conclusion"></a>In Conclusion</h2>
<p>There's a lot of options and details here. If you just want to query the primary, then accept the default, and if you just want to move load to your secondaries, use <code>SECONDARY</code>. But if you're the kind of hotrodder who needs to optimize for consistency, availability, latency, or throughput with every query, read preferences give you total control.</p>
