+++
type = "post"
title = "Announcing PyMongo 3"
date = "2015-04-07T21:45:04"
description = "This is a partial rewrite of the Python driver for MongoDB, our biggest and best release ever."
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "leaf@240.jpg"
draft = false
legacyid = "552481ce5393741c65d1b65b"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="leaf.jpg" alt="Leaf" title="Leaf" /></p>
<p>PyMongo 3.0 is a partial rewrite of the Python driver for MongoDB. More than six years after the first release of the driver, this is the biggest release in PyMongo's history. Bernie Hackett, Luke Lovett, Anna Herlihy, and I are proud of its many improvements and eager for you to try it out. I will shoehorn the major improvements into four shoes: conformance, responsiveness, robustness, and modernity.</p>
<p>(This article will be cross-posted on <a href="http://www.mongodb.com/blog/">the MongoDB Blog</a>.)</p>
<hr />
<div class="toc">
<ul>
<li><a href="#conformance">Conformance</a><ul>
<li><a href="#crud-api">CRUD API</a></li>
<li><a href="#one-client-class">One Client Class</a></li>
<li><a href="#non-conforming-features">Non-Conforming Features</a></li>
</ul>
</li>
<li><a href="#responsiveness">Responsiveness</a><ul>
<li><a href="#replica-set-discovery-and-monitoring">Replica Set Discovery And Monitoring</a></li>
<li><a href="#mongos-load-balancing">Mongos Load-Balancing</a></li>
<li><a href="#throughput">Throughput</a></li>
</ul>
</li>
<li><a href="#robustness">Robustness</a><ul>
<li><a href="#disconnected-startup">Disconnected Startup</a></li>
<li><a href="#one-monitor-thread-per-server">One Monitor Thread Per Server</a></li>
<li><a href="#thread-safety">Thread Safety</a></li>
</ul>
</li>
<li><a href="#modernity">Modernity</a></li>
<li><a href="#motor">Motor</a></li>
</ul>
</div>
<h1 id="conformance">Conformance</h1>
<p>The motivation for PyMongo's overhaul is to supersede or remove its many idiosyncratic APIs. We want you to have a clean interface that is easy to learn and closely matches the interfaces of our other drivers.</p>
<h2 id="crud-api">CRUD API</h2>
<p>Mainly, "conformance" means we have implemented the same interface for create, read, update, and delete operations as the other drivers have, as standardized in Craig Wilson's <a href="https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst">CRUD API Spec</a>. The familiar old methods work the same in PyMongo 3, but they are deprecated:</p>
<ul>
<li><code>save</code></li>
<li><code>insert</code></li>
<li><code>update</code></li>
<li><code>remove</code></li>
<li><code>find_and_modify</code></li>
</ul>
<p>These methods were vaguely named. For example, <code>update</code> updates or replaces some or all matching documents depending on its arguments. The arguments to <code>save</code> and <code>remove</code> are likewise finicky, and the many options for <code>find_and_modify</code> are intimidating. Other MongoDB drivers do not have exactly the same arguments in the same order for all these methods. If you or other developers on your team are using a driver from a different language, it makes life a lot easier to have consistent interfaces.</p>
<p>The new CRUD API names its methods like <code>update_one</code>, <code>insert_many</code>, <code>find_one_and_delete</code>: they say what they mean and mean what they say. Even better, all MongoDB drivers have exactly the same methods with the same arguments. <a href="https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst">See the spec</a> for details.</p>
<h2 id="one-client-class">One Client Class</h2>
<p>In the past we had three client classes: Connection for any one server, and ReplicaSetConnection to connect to a replica set. We also had a MasterSlaveConnection that could distribute reads to slaves in a master-slave set. In November 2012 we created new classes, MongoClient and MongoReplicaSetClient, with better default settings, so now PyMongo had five clients! Even more confusingly, MongoClient could connect to a set of mongos servers and do hot failover.</p>
<p><a href="/blog/good-idea-at-the-time-pymongo-mongoreplicasetclient/">As I wrote earlier</a>, the fine distinctions between the client classes baffled users. And the set of clients we provided did not conform with other drivers. But since PyMongo is among the most-used of all Python libraries we waited long, and thought hard, before making major changes.</p>
<p>The day has come. MongoClient is now the one and only client class for a single server, a set of mongoses, or a replica set. It includes the functionality that had been split into MongoReplicaSetClient: it can connect to a replica set, discover all its members, and monitor the set for stepdowns, elections, and reconfigs. MongoClient now also supports the full <a href="http://api.mongodb.org/python/current/examples/high_availability.html#secondary-reads">ReadPreference API</a>. MongoReplicaSetClient lives on for a time, for compatibility's sake, but new code should use MongoClient exclusively. The obsolete Connection, ReplicaSetConnection, and MasterSlaveConnection are removed.</p>
<p>The options you pass to MongoClient in the URI now completely control the client's behavior:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Connect to one standalone, mongos, or replica set member.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;mongodb://server&#39;</span>)
<span style="color: #666666">&gt;&gt;&gt;</span>
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Connect to a replica set.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(
<span style="color: #666666">...</span>     <span style="color: #BA2121">&#39;mongodb://member1,member2/?replicaSet=my_rs&#39;</span>)
<span style="color: #666666">&gt;&gt;&gt;</span>
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Load-balance among mongoses.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;mongodb://mongos1,mongos2&#39;</span>)
</pre></div>


<p>This is exciting because PyMongo applications are now so easy to deploy: your code simply loads a MongoDB URI from an environment variable or config file and passes it to a MongoClient. Code and configuration are cleanly separated. You can move smoothly from your laptop to a test server to the cloud, simply by changing the URI.</p>
<h2 id="non-conforming-features">Non-Conforming Features</h2>
<p>PyMongo 2 had some quirky features it did not share with other drivers. For one, we had a <code>copy_database</code> method that only one other driver had, and which almost no one used. <a href="/blog/good-idea-at-the-time-pymongo-copy-database/">It was hard to maintain</a> and we believe you want us to focus on the features you use, so we removed it.</p>
<p>A more pernicious misfeature was the <code>start_request</code> method. It bound a thread to a socket, which hurt performance without actually guaranteeing monotonic write consistency. It was overwhelmingly misused, too: new PyMongo users naturally called <code>start_request</code> before starting a request, but in truth the feature had nothing to do with its name. For the history and details, including some entertaining (in retrospect) tales of Python threadlocal bugs, <a href="/blog/good-idea-at-the-time-pymongo-start-request/">see my article on the removal of start_request</a>.</p>
<p>Finally, the Python team rewrote our distributed-systems internals to conform to the new standards we have specified for all our drivers. But if you are a Python programmer you may care only a little that the new code conforms to a spec; it is more interesting to you that the new code is responsive and robust.</p>
<h1 id="responsiveness">Responsiveness</h1>
<p>PyMongo 3's MongoClient can connect to a single server, a replica set, or a set of mongoses. It finds servers and reacts to changing conditions according to <a href="http://www.mongodb.com/blog/post/server-discovery-and-monitoring-next-generation-mongodb-drivers">the Server Discovery And Monitoring spec</a>, and it chooses which server to use for each operation according to <a href="http://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">the Server Selection Spec</a>. David Golden and I explained these specs in general in the linked articles, but I can describe PyMongo&rsquo;s implementation here.</p>
<h2 id="replica-set-discovery-and-monitoring">Replica Set Discovery And Monitoring</h2>
<p>In PyMongo 2, MongoReplicaSetClient used a single background thread to monitor all replica set members in series. So a slow or unresponsive member could block the thread for some time before the thread moved on to discover information about the other members, like their network latencies or which member is primary. If your application was waiting for that information&mdash;say, to write to the new primary after an election&mdash;these delays caused unneeded seconds of downtime.</p>
<p>When PyMongo 3's new MongoClient connects to a replica set it starts one thread per mongod server. The threads fan out to connect to all members of the set in parallel, and they start additional threads as they discover more members. As soon as any thread discovers the primary, your application is unblocked, even while the monitor threads collect more information about the set. This new design improves PyMongo's response time tremendously. If some members are slow or down, or you have many members in your set, PyMongo's discovery is still just as fast.</p>
<p>I explained the new design in <a href="http://www.mongodb.com/blog/post/server-discovery-and-monitoring-next-generation-mongodb-drivers">Server Discovery And Monitoring In Next Generation MongoDB Drivers</a>, and I'll actually demonstrate it in my <a href="http://mongodbworld.com/">MongoDB World</a> talk, Drivers And High Availability: Deep Dive.</p>
<h2 id="mongos-load-balancing">Mongos Load-Balancing</h2>
<p>Our multi-mongos behavior is improved, too. A MongoClient can connect to a set of mongos servers:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Two mongoses.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;mongodb://mongos1,mongos2&#39;</span>)
</pre></div>


<p>The behavior in PyMongo 2 was "high availability": the client connected to the lowest-latency mongos in the list, and used it until a network error prompted it to re-evaluate their latencies and reconnect to one of them. If the driver chose unwisely at first, it stayed pinned to a higher-latency mongos for some time. In PyMongo 3, the background threads monitor the client's network latency to all the mongoses continuously, and the client distributes operations evenly among those with the lowest latency. See <a href="http://api.mongodb.org/python/current/examples/high_availability.html#mongos-load-balancing">mongos Load Balancing</a> for more information.</p>
<h2 id="throughput">Throughput</h2>
<p>Besides PyMongo's improved responsiveness to changing conditions in your deployment, its throughput is better too. We have written <a href="https://jira.mongodb.org/browse/PYTHON-346">a faster and more memory efficient pure python BSON module</a>, which is particularly important for PyPy, and made substantial optimizations in our C extensions.</p>
<h1 id="robustness">Robustness</h1>
<h2 id="disconnected-startup">Disconnected Startup</h2>
<p>The first change you may notice is, MongoClient's constructor no longer blocks while connecting. It does not raise ConnectionFailure if it cannot connect:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;mongodb://no-host.com&#39;</span>)
<span style="color: #666666">&gt;&gt;&gt;</span> client
MongoClient(<span style="color: #BA2121">&#39;no-host.com&#39;</span>, <span style="color: #666666">27017</span>)
</pre></div>


<p>The constructor returns immediately and launches the connection process on background threads. Of course, foreground operations might time out:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find_one()
AutoReconnect: No servers found yet
</pre></div>


<p>Meanwhile, the client's background threads keep trying to reach the server. This is a big win for web applications that use PyMongo&mdash;in a crisis, your app servers might be restarted while your MongoDB servers are unreachable. Your applications should not throw an exception at startup, when they construct the client object. In PyMongo 3 the client can now start up disconnected; it tries to reach your servers until it succeeds.</p>
<p>On the other hand if you wrote code like this to check if mongod is up:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">try</span>:
<span style="color: #666666">...</span>     MongoClient()
<span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;it&#39;s working&quot;</span>)
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">except</span> pymongo<span style="color: #666666">.</span>errors<span style="color: #666666">.</span>ConnectionFailure:
<span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;please start mongod&quot;</span>)
<span style="color: #666666">...</span>
</pre></div>


<p>This will not work any more, since the constructor never throws ConnectionFailure now. Instead, choose how long to wait before giving up by setting <code>serverSelectionTimeoutMS</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient(serverSelectionTimeoutMS<span style="color: #666666">=500</span>)
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">try</span>:
<span style="color: #666666">...</span>     client<span style="color: #666666">.</span>admin<span style="color: #666666">.</span>command(<span style="color: #BA2121">&#39;ping&#39;</span>)
<span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;it&#39;s working&quot;</span>)
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">except</span> pymongo<span style="color: #666666">.</span>errors<span style="color: #666666">.</span>ConnectionFailure:
<span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span>(<span style="color: #BA2121">&quot;please start mongod&quot;</span>)
</pre></div>


<h2 id="one-monitor-thread-per-server">One Monitor Thread Per Server</h2>
<p>Even during regular operations, connections may hang up or time out, and servers go down for periods; monitoring each on a separate thread keeps PyMongo abreast of changes before they cause errors. You will see fewer network exceptions than with PyMongo 2, and the new driver will recover much faster from the unexpected.</p>
<h2 id="thread-safety">Thread Safety</h2>
<p>Another source of fragility in PyMongo 2 was APIs that were not designed for multithreading. Too many of PyMongo's options could be changed at runtime. For example, if you created a database handle:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> db <span style="color: #666666">=</span> client<span style="color: #666666">.</span>test
</pre></div>


<p>...and changed the handle's read preference on a thread, the change appeared in all threads:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">thread_fn</span>():
<span style="color: #666666">...</span>     db<span style="color: #666666">.</span>read_preference <span style="color: #666666">=</span> ReadPreference<span style="color: #666666">.</span>SECONDARY
</pre></div>


<p>Making these options mutable encouraged such mistakes, so we made them immutable. Now you configure handles to databases and collections using thread-safe APIs:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">thread_fn</span>():
<span style="color: #666666">...</span>     my_db <span style="color: #666666">=</span> client<span style="color: #666666">.</span>get_database(
<span style="color: #666666">...</span>         <span style="color: #BA2121">&#39;test&#39;</span>,
<span style="color: #666666">...</span>         read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY)
</pre></div>


<h1 id="modernity">Modernity</h1>
<p>Last, and most satisfying to the team, we have completed our transition to modern Python.</p>
<p>While PyMongo 2 already supported the latest version of Python 3, it did so tortuously by executing <code>auto2to3</code> on its source at install time. This made it too hard for the open source community to contribute to our code, and it led to some <a href="/blog/a-normal-accident-in-python-and-mod-wsgi/">absurdly obscure bugs</a>. We have updated to a single code base that is compatible with Python 2 and 3. We had to drop support for the ancient Pythons 2.4 and 2.5; we were encouraged by recent download statistics to believe that these zombie Python versions are finally at rest.</p>
<h1 id="motor">Motor</h1>
<p><a href="http://motor.readthedocs.org/en/stable/">Motor</a>, my async driver for <a href="http://www.tornadoweb.org/en/stable/">Tornado</a> and MongoDB, has <em>not</em> yet been updated to wrap PyMongo 3. The current release, Motor 0.4, wraps PyMongo 2.8. Motor's still compatible with the latest MongoDB server version, but it lacks the new PyMongo 3 features&mdash;for example, it doesn't have the new CRUD API, and it still monitors replica set members serially instead of in parallel. The next release, Motor 0.5, <em>still</em> won't wrap PyMongo 3, because Motor 0.5 will focus on asyncio support instead. It won't be until version 0.6 that I update Motor with the latest PyMongo changes.</p>
