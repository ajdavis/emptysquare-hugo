+++
type = "post"
title = "PyMongo's New Default: Safe Writes!"
date = "2012-11-27T09:54:53"
description = "I joyfully announce that we are changing all of 10gen's MongoDB drivers to do \"safe writes\" by default. In the process we're renaming all the connection classes to MongoClient, so all the drivers now use the same term for the central class. [ ... ]"
categories = ["Mongo", "Programming", "Python"]
tags = ["pymongo"]
enable_lightbox = false
thumbnail = "get-last-error.png"
draft = false
+++

<p>I joyfully announce that we are <a href="http://blog.mongodb.org/post/36666163412/introducing-mongoclient">changing all of 10gen's MongoDB drivers</a> to do "safe writes" by default. In the process we're renaming all the connection classes to MongoClient, so all the drivers now use the same term for the central class.</p>
<p><a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a> 2.4, released today, has new classes called <code>MongoClient</code> and <code>MongoReplicaSetClient</code> that have the new default setting, and a new API for configuring write-acknowledgement called "write concerns". PyMongo's old <code>Connection</code> and <code>ReplicaSetConnection</code> classes remain untouched for backward compatibility, but they are now considered deprecated and will disappear in some future release. The changes were implemented by PyMongo's maintainer (and my favorite colleague) Bernie Hackett.</p>
<hr />
<p>Contents:</p>
<ul>
<li><a href="#background">Background</a></li>
<li><a href="#new-defaults">The New Defaults</a></li>
<li><a href="#write-concerns">Write Concerns</a></li>
<li><a href="#auto_start_request">auto_start_request</a></li>
<li><a href="#motor">What About Motor?</a></li>
<li><a href="#conclusion">The Uplifting Conclusion</a></li>
</ul>
<h1 id="background"><a id="background"></a>Background</h1>
<p>MongoDB's writes happen in two phases. First the driver sends the server an <code>insert</code>, <code>update</code>, or <code>remove</code> message. The MongoDB server executes the operation and notes the outcome: it records whether there was an error, how many documents were updated or removed, and whether an <a href="http://www.mongodb.org/display/DOCS/Updating#Updating-%7B%7Bupserts%7D%7D">upsert</a> resulted in an update or an insert.</p>
<p>In the next phase, the driver runs the <a href="http://docs.mongodb.org/manual/applications/replication/#replica-set-write-concern"><code>getLastError</code></a> command on the server and awaits the response:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="get-last-error.png" alt="getLastError" title="get_last_error.png" border="0"   /></p>
<p>This <code>getLastError</code> call can be omitted for speed, in which case the driver just sends all its write messages without awaiting acknowledgment. "Fire-and-forget" mode is obviously very high-performance, because it can take advantage of network <em>throughput</em> without being affected by network <em>latency</em>. But this mode doesn't report errors to your application, and it doesn't guarantee that a write has completed before you do a query. It's not the right mode to use by default, so we're changing it now.</p>
<p>In the past we haven't been particularly consistent in our terms for these modes, sometimes talking about "safe" and "unsafe" writes, at other times "blocking" and "non-blocking", etc. From now on we're trying to stick to "acknowledged" and "unacknowledged," since that goes to the heart of the difference. I'll stick to these terms here.</p>
<p>(In 10gen's ancient history, before my time, the plan was to make a full platform-as-a-service stack with MongoDB as the data layer. It made sense then for <code>getLastError</code> to be a separate operation that was run explicitly, and to <em>not</em> call <code>getLastError</code> automatically by default. But MongoDB is a standalone product and it's clear that the default needs to change.)</p>
<h1 id="the-new-defaults"><a id="new-defaults"></a>The New Defaults</h1>
<p>In earlier versions of PyMongo you would create a connection like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> Connection
connection <span style="color: #666666">=</span> Connection(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>)
</pre></div>


<p>By default, <code>Connection</code> did unacknowledged writes&mdash;it didn't call <code>getLastError</code> at all. You could change that with the <code>safe</code> option like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> Connection(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>, safe<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>You could also configure arguments that were passed to every <code>getLastError</code> call that made it wait for specific events, e.g. to <a href="http://docs.mongodb.org/manual/applications/replication/#replica-set-write-concern">wait for the primary and two secondaries to replicate the write</a>, you could pass <code>w=3</code>, and to wait for the primary to <a href="http://www.mongodb.org/display/DOCS/Journaling#Journaling-CommitAcknowledgement">commit the write to its journal</a>, you could pass <code>j=True</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">connection <span style="color: #666666">=</span> Connection(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>, w<span style="color: #666666">=3</span>, j<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>(The "w" terminology comes from the Dynamo whitepaper that's foundational to the NoSQL movement.)</p>
<p><code>Connection</code> hasn't changed in PyMongo 2.4, but we've added a <code>MongoClient</code> which does acknowledged writes by default:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>)
</pre></div>


<p><code>MongoClient</code> lets you pass arguments to <code>getLastError</code> just like <code>Connection</code> did:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>, w<span style="color: #666666">=3</span>, j<span style="color: #666666">=</span><span style="color: #008000">True</span>)
</pre></div>


<p>Instead of an odd overlap between the <code>safe</code> and <code>w</code> options, we've now standardized on using <code>w</code> only. So you can get the old behavior of unacknowledged writes with the new classes using <code>w=0</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MongoClient(<span style="color: #BA2121">&#39;localhost&#39;</span>, <span style="color: #666666">27017</span>, w<span style="color: #666666">=0</span>)
</pre></div>


<p><code>w=0</code> is the new way to say <code>safe=False</code>.</p>
<p><code>w=1</code> is the new <code>safe=True</code> and it's now the default. Other options like <code>j=True</code> or <code>w=3</code> work the same as before. You can still set options per-operation:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;foo&#39;</span>: <span style="color: #BA2121">&#39;bar&#39;</span>}, w<span style="color: #666666">=1</span>)
</pre></div>


<p><code>ReplicaSetConnection</code> is also obsolete, of course, and succeeded by <code>MongoReplicaSetClient</code>.</p>
<h1 id="write-concerns"><a id="write-concerns"></a>Write Concerns</h1>
<p>The old <code>Connection</code> class let you set the <code>safe</code> attribute to <code>True</code> or <code>False</code>, or call <code>set_lasterror_options()</code> for more complex configuration. These are deprecated, and you should now use the <code>MongoClient.write_concern</code> attribute. <code>write_concern</code> is a dict whose keys may include <code>w</code>, <code>wtimeout</code>, <code>j</code>, and <code>fsync</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> client <span style="color: #666666">=</span> MongoClient()
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #408080; font-style: italic"># default empty dict means &quot;w=1&quot;</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern
{}
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern <span style="color: #666666">=</span> {<span style="color: #BA2121">&#39;w&#39;</span>: <span style="color: #666666">2</span>, <span style="color: #BA2121">&#39;wtimeout&#39;</span>: <span style="color: #666666">1000</span>}
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern
{<span style="color: #BA2121">&#39;wtimeout&#39;</span>: <span style="color: #666666">1000</span>, <span style="color: #BA2121">&#39;w&#39;</span>: <span style="color: #666666">2</span>}
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern[<span style="color: #BA2121">&#39;j&#39;</span>] <span style="color: #666666">=</span> <span style="color: #008000">True</span>
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern
{<span style="color: #BA2121">&#39;wtimeout&#39;</span>: <span style="color: #666666">1000</span>, <span style="color: #BA2121">&#39;j&#39;</span>: <span style="color: #008000">True</span>, <span style="color: #BA2121">&#39;w&#39;</span>: <span style="color: #666666">2</span>}
<span style="color: #666666">&gt;&gt;&gt;</span> client<span style="color: #666666">.</span>write_concern[<span style="color: #BA2121">&#39;w&#39;</span>] <span style="color: #666666">=</span> <span style="color: #666666">0</span> <span style="color: #408080; font-style: italic"># disable write acknowledgement</span>
</pre></div>


<p>You can see that the default <code>write_concern</code> is an empty dictionary. It's equivalent to <code>w=1</code>, meaning "do regular acknowledged writes".</p>
<h1 id="auto95start95request"><a id="auto_start_request"></a>auto_start_request</h1>
<p>This is very nerdy, but my personal favorite. The default value for <code>auto_start_request</code> is changing from <code>True</code> to <code>False</code>.</p>
<p>The short explanation is this: with the old <code>Connection</code>, you could write some data to the server without acknowledgment, and then read that data back immediately afterward, provided there wasn't an error <em>and</em> that you used the same socket for the write and the read. If you used a different socket for the two operations then there was no guarantee of "read your writes consistency," because the write could still be enqueued on one socket while you completed the read on the other.</p>
<p>You could pin the current thread to a single socket with <code>Connection.start_request()</code>, and in fact the default was for <code>Connection</code> to start a request for you with every operation. That's <code>auto_start_request</code>. It offers some consistency guarantees but requires the driver to open extra sockets.</p>
<p>Now that <code>MongoClient</code> waits for acknowledgment of every write, <code>auto_start_request</code> is no longer needed. If you do this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> collection <span style="color: #666666">=</span> MongoClient()<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection
<span style="color: #666666">&gt;&gt;&gt;</span> collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;foo&#39;</span>: <span style="color: #BA2121">&#39;bar&#39;</span>})
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">print</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;foo&#39;</span>: <span style="color: #BA2121">&#39;bar&#39;</span>})
</pre></div>


<p>... then the <code>find_one</code> won't run until the <code>insert</code> is acknowledged, which means your document has definitely been inserted and you can query for it confidently on any socket. We turned off <code>auto_start_request</code> for improved performance and fewer sockets. If you're doing unacknowledged writes with <code>w=0</code> followed by reads, you should consider whether to call <code>MongoClient.start_request()</code>. See the details (with charts!) in <a href="/blog/requests-in-python-and-mongodb/">my blog post on requests</a> from April.</p>
<h1 id="migration"><a id="migration"></a>Migration</h1>
<p><code>Connection</code> and <code>ReplicaSetConnection</code> will remain for a while (not forever), so your existing code will work the same and you have time to migrate. We are working to update all documentation and example code to use the new classes. In time we'll add deprecation warnings to the old classes and methods before removing them completely.</p>
<p>If you maintain a library built on PyMongo, you can check for the new classes with code like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">try</span>:
    <span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">pymongo</span> <span style="color: #008000; font-weight: bold">import</span> MongoClient
    has_mongo_client <span style="color: #666666">=</span> <span style="color: #008000">True</span>
<span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">ImportError</span>:
    has_mongo_client <span style="color: #666666">=</span> <span style="color: #008000">False</span>
</pre></div>


<h1 id="what-about-motor"><a id="motor"></a>What About Motor?</h1>
<p>Motor's in beta, so I'll break backwards compatibility ruthlessly for the sake of cleanliness. In the next week or two I'll merge the official PyMongo changes into <a href="https://github.com/ajdavis/mongo-python-driver/tree/motor/">my fork</a>, and I'll nuke <code>MotorConnection</code> and <code>MotorReplicaSetConnection</code>, to be replaced with <code>MotorClient</code> and <code>MotorReplicaSetClient</code>.</p>
<h1 id="the-uplifting-conclusion"><a id="conclusion"></a>The Uplifting Conclusion</h1>
<p>We've known for a while that unacknowledged writes were the wrong default. Now it's finally time to fix it. The new <code>MongoClient</code> class lets you migrate from the old default to the new one at your leisure, and brings a bonus: all the drivers agree on the name of the main entry-point. For programmers new to MongoDB, turning on write-acknowledgment by default is a huge win, and makes it much more intuitive to write applications on MongoDB.</p>
    