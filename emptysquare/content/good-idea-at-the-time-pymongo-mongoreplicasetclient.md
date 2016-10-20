+++
type = "post"
title = "It Seemed Like A Good Idea At The Time: MongoReplicaSetClient"
date = "2014-12-17T16:35:33"
description = "Concludes a four-part series about choices we regretted in the design of PyMongo."
category = ["Mongo", "Programming", "Python"]
tag = ["good-idea-at-the-time", "pymongo"]
enable_lightbox = false
thumbnail = "road-4.jpg"
draft = false
disqus_identifier = "547a7ed75393740962f7b3f7"
disqus_url = "https://emptysqua.re/blog/547a7ed75393740962f7b3f7/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="road-4.jpg" alt="Road" title="Road" /></p>
<p><em>The road to hell is paved with good intentions.</em></p>
<p>I'm writing <a href="/good-idea-at-the-time-pymongo/">post mortems for four regrettable decisions in PyMongo</a>, the standard Python driver for MongoDB. Each of these decisions made life painful for Bernie Hackett and me&mdash;PyMongo's maintainers&mdash;and confused our users. This winter we're preparing PyMongo 3.0, and we have the chance to fix them all. As I snip out these regrettable designs I ask, what went wrong?</p>
<p>I conclude the series with the final regrettable decision: MongoReplicaSetClient.</p>
<div class="toc">
<ul>
<li><a href="#the-beginning">The Beginning</a></li>
<li><a href="#reading-from-secondaries">Reading From Secondaries</a></li>
<li><a href="#the-curse">The Curse</a></li>
<li><a href="#the-curse-is-lifted">The Curse Is Lifted</a></li>
<li><a href="#the-moral-of-the-story">The Moral Of The Story</a></li>
</ul>
</div>
<hr />
<h1 id="the-beginning">The Beginning</h1>
<p>In January of 2011, Bernie Hackett was maintaining PyMongo single-handedly. PyMongo's first author Mike Dirolf had left, and I hadn't yet joined.</p>
<p>Replica sets had been released in <a href="http://blog.mongodb.org/post/908172564/mongodb-1-6-released">MongoDB 1.6 the year before</a>, in 2010. They obsoleted the old "master-slave replication" system, which didn't do automatic failover if the master machine died. In replica sets, if the primary dies the secondaries elect a new primary at once.</p>
<p>PyMongo 2.0 had one client class, called Connection. By the time our story begins, Bernie had added most of the replica-set features Connection needed. Given a replica set name and the addresses of one or more members, it could discover the whole set and connect to the primary. For example, with a three-node set and the primary on port 27019:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># Obsolete code.</span>
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> Connection
<span style="color: #666666">&gt;&gt;&gt;</span> c <span style="color: #666666">=</span> Connection(<span style="color: #BA2121">&#39;localhost:27017,localhost:27018&#39;</span>,
<span style="color: #666666">...</span>                replicaset<span style="color: #666666">=</span><span style="color: #BA2121">&#39;repl0&#39;</span>,
<span style="color: #666666">...</span>                safe<span style="color: #666666">=</span><span style="color: #008000">True</span>)
<span style="color: #666666">&gt;&gt;&gt;</span> c
Connection([<span style="color: #BA2121">u&#39;localhost:27019&#39;</span>, <span style="color: #BA2121">&#39;localhost:27017&#39;</span>, <span style="color: #BA2121">&#39;localhost:27018&#39;</span>])
<span style="color: #666666">&gt;&gt;&gt;</span> c<span style="color: #666666">.</span>port  <span style="color: #408080; font-style: italic"># Current primary&#39;s port.</span>
<span style="color: #666666">27019</span>
</pre></div>


<p>If there was a failover, Connection's next operation failed, but it found and connected to the primary on the operation after that:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>insert({})
error: [Errno <span style="color: #666666">61</span>] Connection refused
<span style="color: #666666">&gt;&gt;&gt;</span> c<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>insert({})
ObjectId(<span style="color: #BA2121">&#39;548ef36eca1ce90d91000007&#39;</span>)
<span style="color: #666666">&gt;&gt;&gt;</span> c<span style="color: #666666">.</span>port  <span style="color: #408080; font-style: italic"># What port is the new primary on?</span>
<span style="color: #666666">27018</span>
</pre></div>


<p>(Note that PyMongo 2.0 threw a socket error after a failover: we consistently wrap errors in our <code>ConnectionFailure</code> exception class now.)</p>
<h1 id="reading-from-secondaries">Reading From Secondaries</h1>
<p>The Connection class's replica set features were pretty well-rounded, actually. But a user asked Bernie for a new feature: he wanted <a href="https://jira.mongodb.org/browse/PYTHON-196">a convenient way to query from secondaries</a>. Our Ruby and Node drivers supported this feature using a different connection class. So in late 2011, just as I was joining the company, Bernie wrote a new class, ReplicaSetConnection. Depending on your read preference, it would read from the primary or a secondary:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> ReplicaSetConnection, ReadPreference
<span style="color: #666666">&gt;&gt;&gt;</span> rsc <span style="color: #666666">=</span> ReplicaSetConnection(
<span style="color: #666666">...</span>    <span style="color: #BA2121">&#39;localhost:27017,localhost:27018&#39;</span>,
<span style="color: #666666">...</span>    replicaset<span style="color: #666666">=</span><span style="color: #BA2121">&#39;repl0&#39;</span>,
<span style="color: #666666">...</span>    read_preference<span style="color: #666666">=</span>ReadPreference<span style="color: #666666">.</span>SECONDARY,
<span style="color: #666666">...</span>    safe<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>Besides distributing reads to secondaries, the new ReplicaSetConnection had another difference from Connection: a monitor thread. Every 30 seconds, the thread proactively updated its view of the replica set's topology. This gave ReplicaSetConnection two advantages. First, it could detect when a new secondary had joined the set, and start using it for reads. Second, even if it was idle during a failover, after 30 seconds it would detect the new primary and use it for the next operation, instead of throwing an error on the first try.</p>
<p>ReplicaSetConnection was mostly the same as the existing Connection class. But it was different enough that there was some risk: the new code might have new bugs. Or at least, it might have surprising differences from Connection's behavior.</p>
<p>PyMongo has special burdens, since it's the intersection between two huge groups: <a href="http://db-engines.com/en/ranking">MongoDB users</a> and the Python world, <a href="http://blog.codeeval.com/codeevalblog/2014">possibly the largest language community in history</a>. These days PyMongo is downloaded half a million times a month, and back then its stats were big, too. So Bernie tread very cautiously. He didn't force you to use the new code right away. Instead, he made a separate class you could opt in to. He released ReplicaSetConnection in PyMongo 2.1.</p>
<h1 id="the-curse">The Curse</h1>
<p>But we never merged the two classes.</p>
<p>Ever since November 2011, when Bernie wrote ReplicaSetConnection and I joined MongoDB, we've maintained ReplicaSetConnection's separate code. It gained features. It learned to run mapreduce jobs on secondaries. Its read preference options <a href="/reading-from-mongodb-replica-sets-with-pymongo/">expanded to include members' network latency and tags</a>. Connection gained distinct features, too, diverging further from ReplicaSetConnection: <a href="https://github.com/mongodb/mongo-python-driver/blob/v2.8/doc/examples/high_availability.rst#high-availability-and-mongos">it can connect to the nearest mongos from a list of them</a>, and fail over to the next if that mongos goes down. Other features applied equally to both classes, so we wrote them twice. We had two tests for most of these features. When we <a href="/pymongos-new-default-safe-writes/">renamed Connection to MongoClient</a>, we also renamed ReplicaSetConnection to MongoReplicaSetClient. And still, we didn't merge them.</p>
<p>The persistent, slight differences between the two classes persistently confused our users. I remember my feet aching as I stood at our booth at PyCon in 2013, explaining to a user when he should use MongoClient and when he should use MongoReplicaSetClient&mdash;and I remember his expression growing sourer each minute as he realized how irrational the distinction was.</p>
<p>I explained it again during <a href="http://www.meetup.com/New-York-MongoDB-User-Group/">MongoDB Office Hours</a>, when I sat at a cafeteria table with a couple users, soon after we moved to the office in Times Square. And again, I saw the frustration on their faces. <a href="http://stackoverflow.com/questions/19554764/pymongo-advantage-of-using-mongoreplicasetclient">I explained it on Stack Overflow a couple months later</a>. I've been explaining this for as long as I've worked here.</p>
<h1 id="the-curse-is-lifted">The Curse Is Lifted</h1>
<p>This year, two events conspired to kill MongoReplicaSetClient. First, we resolved to write a PyMongo 3.0 with a cleaned-up API. Second, I wrote the <a href="/server-discovery-and-monitoring-spec/">Server Discovery And Monitoring Spec</a>, a comprehensive description of how all our drivers should connect to a standalone server, a set of mongos servers, or a replica set. This spec closely followed the design of our Java and C# drivers, which never had a ReplicaSetConnection. These drivers each have a single class that connects to any kind of MongoDB topology.</p>
<p>Since the Server Discovery And Monitoring Spec provides the algorithm to connect to any topology with the same class, I just followed my spec and wrote a unified MongoClient for PyMongo 3. For the sake of backwards compatibility, MongoReplicaSetClient lives a while longer <a href="https://github.com/mongodb/mongo-python-driver/blob/3.0/pymongo/mongo_replica_set_client.py">as an empty, deprecated subclass of MongoClient</a>.</p>
<p>The new MongoClient has many advantages over both its ancestors. Mainly, it's concurrent: it connects to all the servers in your deployment in parallel. It runs your operations as soon as it finds any suitable server, while it continues to discover the rest of the deployment using background threads. Since it discovers and monitors all servers in parallel, it isn't hampered by a down server, or a distant one. It will be responsive even with <a href="https://jira.mongodb.org/browse/SERVER-15060">the very large replica sets that will be possible in MongoDB 2.8</a>, or <a href="https://jira.mongodb.org/browse/SERVER-3110">the even larger ones</a> we may someday allow.</p>
<p>Unifying the two classes also makes <a href="http://docs.mongodb.org/manual/reference/connection-string/">MongoDB URIs</a> more powerful. Let's say you develop your Python code against a standalone mongod on your laptop, then you test in a staging environment with a replica set, then deploy to a sharded cluster. If you set the URI with a config file or environment variable, you had to write code like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># PyMongo 2.x.</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo.uri_parse</span> <span style="color: #008000; font-weight: bold">import</span> parse_uri

uri <span style="color: #666666">=</span> os<span style="color: #666666">.</span>environ[<span style="color: #BA2121">&#39;MONGODB_URI&#39;</span>]
<span style="color: #008000; font-weight: bold">if</span> <span style="color: #BA2121">&#39;replicaset&#39;</span> <span style="color: #AA22FF; font-weight: bold">in</span> parse_uri(uri)[<span style="color: #BA2121">&#39;options&#39;</span>]:
    client <span style="color: #666666">=</span> MongoReplicaSetClient(uri)
<span style="color: #008000; font-weight: bold">else</span>:
    client <span style="color: #666666">=</span> MongoClient(uri)
</pre></div>


<p>This is annoying. Now, the URI controls everything:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># PyMongo 3.0.</span>
client <span style="color: #666666">=</span> MongoClient(os<span style="color: #666666">.</span>environ[<span style="color: #BA2121">&#39;MONGODB_URI&#39;</span>])
</pre></div>


<p>Configuration and code are properly separated.</p>
<h1 id="the-moral-of-the-story">The Moral Of The Story</h1>
<p>I need your help&mdash;what <em>is</em> the moral? What should we have done differently?</p>
<p>When Bernie added read preferences and a monitor thread to PyMongo, I understand why he didn't overhaul the Connection class itself. The new code needed a shakedown cruise before it could be the default. You ask, "Why not publish a beta?" Few people install betas of PyMongo. Customers do thoroughly test early releases of the MongoDB server, but for PyMongo they just use the official release. So if we published a beta and received no bug reports, that wouldn't prove anything.</p>
<p>Bernie wanted the new code exercised. So it needed to be in a release. He had to commit to an API, so he published ReplicaSetConnection alongside Connection. Once ReplicaSetConnection was published it had to be supported forever. And worse, we had to maintain the small differences between Connection and ReplicaSetConnection, for backwards compatibility.</p>
<p>Maybe the moment to merge them was when we introduced MongoClient in late 2012. You had to choose to opt into MongoClient, so we could have merged the two classes into one new class, instead of preserving the distinction and creating MongoReplicaSetClient. But the introduction of MongoClient was complex and urgent; we didn't have time to unify the classes, too. It was too much risk at once.</p>
<p>I think the moral is: cultivate beta testers. That's what I did with <a href="http://motor.readthedocs.org/">Motor</a>, my asynchronous driver for Tornado and MongoDB. It had long alpha and beta phases where I pressed developers to try it. I found PyMongo and AsyncMongo users and asked them to try switching to Motor. I kept a list of Motor testers and checked in with them occasionally. I <a href="/eating-your-own-hamster-food/">ate my own hamster food</a>: I used Motor to build the blog you're reading. Once I had some reports of Motor in production, and I saw it mentioned on Stack Overflow, and I discovered projects that depended on Motor in GitHub, I figured I had users and it was time for an official release.</p>
<p>Not all these methods will work for an established project like PyMongo, but still: for PyMongo 3.0, we should ask our community to help shake out the bugs. </p>
<p>When the beta is ready, will you help?</p>
<hr />
<p><em>This is the final installment in <a href="/good-idea-at-the-time-pymongo/">my four-part series on regrettable decisions we made with PyMongo</a>.</em></p>
