+++
type = "post"
title = "Motor Progress Report: The Road to 0.2"
date = "2013-12-23T15:47:26"
description = "Big changes are coming in the next release of my async MongoDB driver."
"blog/category" = ["Mongo", "Motor", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
legacyid = "52b89e9d53937479d528dfac"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p><strong>Update</strong>: Motor 0.2rc0 is out, <a href="http://motor.readthedocs.org/en/latest/changelog.html">its manual and changelog are on ReadTheDocs</a>.</p>
<hr />
<p><a href="https://motor.readthedocs.org/en/latest/">Motor</a>, my non-blocking driver for MongoDB and Tornado, is approaching the next big release, version 0.2. The improvements fall into three buckets: ease of use, features, and server compatibility.</p>
<h2 id="ease-of-use">Ease Of Use</h2>
<p>In Motor's current version, 0.1.2, you have to use an awkward style to do async operations in a coroutine:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(collection<span style="color: #666666">.</span>find_one, {<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>In the next release, <code>motor.Op</code> will be deprecated and you'll call Motor functions directly, the same as in PyMongo. The <code>yield</code> keyword is the only difference that remains:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>The new syntax matches the latest style of other Tornado libraries, and it's the style used in Python's new asyncio library.</p>
<p>The other awkward thing in Motor is <code>open_sync()</code>. Since there's no way to do async I/O before starting Tornado's event loop, you have to do this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">client <span style="color: #666666">=</span> MotorClient()
<span style="background-color: #ffffcc">client<span style="color: #666666">.</span>open_sync()
</span>
<span style="color: #408080; font-style: italic"># ...additional application setup....</span>

IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>start()
</pre></div>


<p>In the next release, <code>open_sync</code> will be unnecessary. In fact I'm removing it entirely. I've added features to PyMongo itself (in <strong>its</strong> next release, version 2.7) that Motor can use to connect to the server on demand, when you first attempt an async operation.</p>
<h2 id="features">Features</h2>
<p>Motor 0.1.2 wraps PyMongo 2.5.0, which was released in March, so it lacks a number of features introduced in more recent PyMongos: exhaust cursors, streaming inserts, a more robust BSON decoder, several options for finer control of the connection pool, and more authentication mechanisms for enterprise environments. <a href="http://api.mongodb.org/python/current/changelog.html">You can see all the features introduced since 2.5.0 in PyMongo's changelog.</a> By wrapping PyMongo 2.7 instead of 2.5, the next Motor will get all these features, too.</p>
<p>Motor has implemented SSL encryption since the first release, but didn't supported client or server certificate validation, much less X509 authentication. The next release will do it all; Motor will have the same comprehensive SSL support as PyMongo.</p>
<h2 id="server-compatibility">Server Compatibility</h2>
<p>There's a lot of new features in the next release of the MongoDB server itself. MongoDB 2.6 will come out with <a href="http://docs.mongodb.org/master/release-notes/2.6/#aggregation-operations-now-return-cursors">aggregation cursors</a>, <a href="http://docs.mongodb.org/master/release-notes/2.6/#new-write-commands">bulk write operations</a>, <a href="http://docs.mongodb.org/master/release-notes/2.6/#user-defined-roles">a new role-management system</a>, <a href="http://docs.mongodb.org/master/reference/method/cursor.maxTimeMS/#cursor.maxTimeMS">operation time limits</a>, and more. All of these features require changes to PyMongo. Since Motor 0.2 will wrap the latest PyMongo, Motor will also support the latest MongoDB features.</p>
<h2 id="current-status">Current Status</h2>
<p>By the time I go on vacation next week, <a href="https://github.com/mongodb/motor/">Motor's code on master</a> will be ready for the 0.2 release. But there will be a brief lull: we have to wait for the MongoDB 2.6 release candidate, and then we have to release PyMongo 2.7. Then Motor can correctly list PyMongo 2.7 in its requirements, and I'll put it on PyPI.</p>
<p>Meanwhile, please don't install Motor from GitHub. Use Motor 0.1.2 from PyPI, with PyMongo 2.5.0. The documentation for that version of Motor is <a href="http://motor.readthedocs.org/en/stable/">the "stable" version on ReadTheDocs</a> until the next Motor release. There's been some confusion among new Motor users about installing the correct versions of Motor and PyMongo. Stick to these recommendations for now, and I'll find ways to ease the installation troubles in the next release.</p>
    