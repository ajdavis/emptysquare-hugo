+++
type = "post"
title = "Yes, Every MongoDB Driver Supports Every Command"
date = "2012-12-17T17:29:54"
description = ""
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "50cf9b1c5393745f960f20d0"
disqus_url = "https://emptysqua.re/blog/50cf9b1c5393745f960f20d0/"
+++

<p>This post is in response to a persistent form of question I receive about MongoDB drivers: "Does driver X support feature Y?" The answer is nearly always "yes," but you can't know that unless you understand MongoDB commands.</p>
<p>There are only four kinds of operations a MongoDB driver can perform on the server: insert, update, remove, query, and commands.</p>
<p>Almost two years ago my colleague Kristina wrote about "<a href="http://www.kchodorow.com/blog/2011/01/25/why-command-helpers-suck/">Why Command Helpers Suck</a>," and she is still right: if you only use the convenience methods without understanding the unifying concept of a "command," you're unnecessarily tied to a particular driver's API, and you don't know how MongoDB really works.</p>
<p>So let's do a pop quiz:</p>
<ol>
<li>Which MongoDB drivers support the Aggregation Framework?</li>
<li>Which support the "group" operation?</li>
<li>Which drivers are compatible with MongoDB's mapreduce feature?</li>
<li>Which drivers let you run "count" or "distinct" on a collection?</li>
</ol>
<p>If you answered, "all of them," you're right&mdash;every driver supports commands, and all the features I asked about are commands.</p>
<p>Let's consider three MongoDB drivers for Python and show examples of using the <code>distinct</code> command in each.</p>
<h1 id="pymongo">PyMongo</h1>
<p>PyMongo has two convenience methods for <code>distinct</code>. One is on the <code>Collection</code> class, the other on <code>Cursor</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
<span style="color: #666666">&gt;&gt;&gt;</span> db <span style="color: #666666">=</span> MongoClient()<span style="color: #666666">.</span>test
<span style="color: #666666">&gt;&gt;&gt;</span> db<span style="color: #666666">.</span>test_collection<span style="color: #666666">.</span>distinct(<span style="color: #BA2121">&#39;my_key&#39;</span>)
[<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]
<span style="color: #666666">&gt;&gt;&gt;</span> db<span style="color: #666666">.</span>test_collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>distinct(<span style="color: #BA2121">&#39;my_key&#39;</span>)
[<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]
</pre></div>


<p>But this all boils down to the same MongoDB command. We can look up its arguments in the <a href="http://docs.mongodb.org/manual/reference/commands/">MongoDB Command Reference</a> and see that <a href="http://docs.mongodb.org/manual/reference/commands/#distinct">distinct</a> takes the form:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ distinct: collection, key: &lt;field&gt;, query: &lt;query&gt; }
</pre></div>


<p>So let's use PyMongo's generic <code>command</code> method to run <code>distinct</code> directly. We'll pass the <code>collection</code> and <code>key</code> arguments and omit <code>query</code>. We need to use PyMongo's <code>SON</code> class to ensure we pass the arguments in the right order:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">bson</span> <span style="color: #008000; font-weight: bold">import</span> SON
<span style="color: #666666">&gt;&gt;&gt;</span> db<span style="color: #666666">.</span>command(SON([(<span style="color: #BA2121">&#39;distinct&#39;</span>, <span style="color: #BA2121">&#39;test_collection&#39;</span>), (<span style="color: #BA2121">&#39;key&#39;</span>, <span style="color: #BA2121">&#39;my_key&#39;</span>)]))
{<span style="color: #BA2121">u&#39;ok&#39;</span>: <span style="color: #666666">1.0</span>,
 <span style="color: #BA2121">u&#39;stats&#39;</span>: {<span style="color: #BA2121">u&#39;cursor&#39;</span>: <span style="color: #BA2121">u&#39;BasicCursor&#39;</span>,
            <span style="color: #BA2121">u&#39;n&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscanned&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscannedObjects&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;timems&#39;</span>: <span style="color: #666666">0</span>},
 <span style="color: #BA2121">u&#39;values&#39;</span>: [<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]}
</pre></div>


<p>The answer is in <code>values</code>.</p>
<h1 id="motor">Motor</h1>
<p>My async driver for Tornado and MongoDB, called <a href="/motor/">Motor</a>, supports a similar conveniences for <code>distinct</code>. It has both the <code>MotorCollection.distinct</code> method:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.ioloop</span> <span style="color: #008000; font-weight: bold">import</span> IOLoop
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> gen
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">motor</span>
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">motor</span> <span style="color: #008000; font-weight: bold">import</span> MotorConnection
<span style="color: #666666">&gt;&gt;&gt;</span> db <span style="color: #666666">=</span> MotorConnection()<span style="color: #666666">.</span>open_sync()<span style="color: #666666">.</span>test
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #AA22FF">@gen.engine</span>
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="background-color: #ffffcc"><span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span> (<span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(db<span style="color: #666666">.</span>test_collection<span style="color: #666666">.</span>distinct, <span style="color: #BA2121">&#39;my_key&#39;</span>))
</span><span style="color: #666666">...</span>     IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>stop()
<span style="color: #666666">...</span> 
<span style="color: #666666">&gt;&gt;&gt;</span> f()
<span style="color: #666666">&gt;&gt;&gt;</span> IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
[<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]
</pre></div>


<p>... and <code>MotorCursor.distinct</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #AA22FF">@gen.engine</span>
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="background-color: #ffffcc"><span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span> (<span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(db<span style="color: #666666">.</span>test_collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>distinct, <span style="color: #BA2121">&#39;my_key&#39;</span>))
</span><span style="color: #666666">...</span>     IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>stop()
<span style="color: #666666">...</span> 
<span style="color: #666666">&gt;&gt;&gt;</span> f()
<span style="color: #666666">&gt;&gt;&gt;</span> IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
[<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]
</pre></div>


<p>Again, these are just convenient alternatives to using <code>MotorDatabase.command</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #AA22FF">@gen.engine</span>
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="background-color: #ffffcc"><span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span> (<span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(db<span style="color: #666666">.</span>command,
</span><span style="background-color: #ffffcc"><span style="color: #666666">...</span>         SON([(<span style="color: #BA2121">&#39;distinct&#39;</span>, <span style="color: #BA2121">&#39;test_collection&#39;</span>), (<span style="color: #BA2121">&#39;key&#39;</span>, <span style="color: #BA2121">&#39;my_key&#39;</span>)])))
</span><span style="color: #666666">...</span>     IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>stop()
<span style="color: #666666">...</span> 
<span style="color: #666666">&gt;&gt;&gt;</span> f()
<span style="color: #666666">&gt;&gt;&gt;</span> IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
{<span style="color: #BA2121">u&#39;ok&#39;</span>: <span style="color: #666666">1.0</span>,
 <span style="color: #BA2121">u&#39;stats&#39;</span>: {<span style="color: #BA2121">u&#39;cursor&#39;</span>: <span style="color: #BA2121">u&#39;BasicCursor&#39;</span>,
            <span style="color: #BA2121">u&#39;n&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscanned&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscannedObjects&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;timems&#39;</span>: <span style="color: #666666">0</span>},
 <span style="color: #BA2121">u&#39;values&#39;</span>: [<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]}
</pre></div>


<h1 id="asyncmongo">AsyncMongo</h1>
<p>AsyncMongo is another driver for Tornado and MongoDB. Its interface isn't nearly so rich as Motor's, so I often hear questions like, "Does AsyncMongo support <code>distinct</code>? Does it support <code>aggregate</code>? What about <code>group</code>?" In fact, it's those questions that prompted this post. And of course the answer is yes, AsyncMongo supports all commands:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.ioloop</span> <span style="color: #008000; font-weight: bold">import</span> IOLoop
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">asyncmongo</span>
<span style="color: #666666">&gt;&gt;&gt;</span> db <span style="color: #666666">=</span> asyncmongo<span style="color: #666666">.</span>Client(
<span style="color: #666666">...</span>     pool_id<span style="color: #666666">=</span><span style="color: #BA2121">&#39;mydb&#39;</span>, host<span style="color: #666666">=</span><span style="color: #BA2121">&#39;127.0.0.1&#39;</span>, port<span style="color: #666666">=27017</span>,
<span style="color: #666666">...</span>     maxcached<span style="color: #666666">=10</span>, maxconnections<span style="color: #666666">=50</span>, dbname<span style="color: #666666">=</span><span style="color: #BA2121">&#39;test&#39;</span>)
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #AA22FF">@gen.engine</span>
<span style="color: #666666">...</span> <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="background-color: #ffffcc"><span style="color: #666666">...</span>     results <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(db<span style="color: #666666">.</span>command,
</span><span style="background-color: #ffffcc"><span style="color: #666666">...</span>         SON([(<span style="color: #BA2121">&#39;distinct&#39;</span>, <span style="color: #BA2121">&#39;test_collection&#39;</span>), (<span style="color: #BA2121">&#39;key&#39;</span>, <span style="color: #BA2121">&#39;my_key&#39;</span>)]))
</span><span style="color: #666666">...</span>     <span style="color: #008000; font-weight: bold">print</span> results<span style="color: #666666">.</span>args[<span style="color: #666666">0</span>]
<span style="color: #666666">...</span>     IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>stop()
<span style="color: #666666">...</span> 
<span style="color: #666666">&gt;&gt;&gt;</span> f()
<span style="color: #666666">&gt;&gt;&gt;</span> IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
{<span style="color: #BA2121">u&#39;ok&#39;</span>: <span style="color: #666666">1.0</span>,
 <span style="color: #BA2121">u&#39;stats&#39;</span>: {<span style="color: #BA2121">u&#39;cursor&#39;</span>: <span style="color: #BA2121">u&#39;BasicCursor&#39;</span>,
            <span style="color: #BA2121">u&#39;n&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscanned&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;nscannedObjects&#39;</span>: <span style="color: #666666">3</span>,
            <span style="color: #BA2121">u&#39;timems&#39;</span>: <span style="color: #666666">0</span>},
 <span style="color: #BA2121">u&#39;values&#39;</span>: [<span style="color: #666666">1.0</span>, <span style="color: #666666">2.0</span>, <span style="color: #666666">3.0</span>]}
</pre></div>


<h1 id="exceptions">Exceptions</h1>
<p>There are some areas where drivers really differ, like <a href="http://docs.mongodb.org/manual/replication/">Replica Set</a> support, or <a href="/reading-from-mongodb-replica-sets-with-pymongo/">Read Preferences</a>. 10gen's drivers are much more consistent than third-party drivers. But if the underlying operation is a command, then all drivers are essentially the same.</p>
<h1 id="so-go-learn-how-to-run-commands">So Go Learn How To Run Commands</h1>
<p>So the next time you're about to ask, "Does driver X support feature Y," first check if Y is a command by looking for it in the <a href="http://docs.mongodb.org/manual/reference/commands/">command reference</a>. Chances are it's there, and if so, you know how to run it.</p>
