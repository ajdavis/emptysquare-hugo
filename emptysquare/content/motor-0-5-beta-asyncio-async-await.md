+++
type = "post"
title = "Motor 0.5 Beta: asyncio, async and await, simple aggregation"
date = "2015-11-10T23:52:06"
description = "My async driver for MongoDB now supports asyncio, and allows \"async\" and \"await\" in Python 3.5. Collection.aggregate() is more concise."
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "563e6aa153937409903cc55d"
disqus_url = "https://emptysqua.re/blog/563e6aa153937409903cc55d/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today is a good day: I've published a beta of <a href="http://motor.readthedocs.org/en/stable/">Motor</a>, my async Python driver for MongoDB. This version is the biggest upgrade yet. Help me beta-test it! Install with:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">python -m pip install --pre motor==0.5b0
</pre></div>


<p>Motor 0.5 still depends on PyMongo 2.8.0 exactly. That PyMongo version is outdated, I know, but I've decided not to tackle that issue right now.</p>
<p>You'll forgive me, because this Motor release is huge:</p>
<div class="toc">
<ul>
<li><a href="#asyncio">asyncio</a></li>
<li><a href="#aggregate">aggregate</a></li>
<li><a href="#python-35">Python 3.5</a></li>
<li><a href="#async-and-await">async and await</a></li>
</ul>
</div>
<h1 id="asyncio">asyncio</h1>
<p>Motor can now integrate with asyncio, as an alternative to Tornado. My gratitude
to R&eacute;mi Jolin, Andrew Svetlov, and Nikolay Novik for their huge contributions to
Motor's asyncio integration.</p>
<p>The Tornado and asyncio APIs are kindred. Here is Motor with Tornado:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Tornado API</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> gen, ioloop
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">motor.motor_tornado</span> <span style="color: #008000; font-weight: bold">import</span> MotorClient

<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
    <span style="color: #008000; font-weight: bold">print</span>(result)

client <span style="color: #666666">=</span> MotorClient()
ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>run_sync(f)
</pre></div>


<p>And here's the new asyncio integration:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">asyncio</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">motor.motor_asyncio</span> <span style="color: #008000; font-weight: bold">import</span> AsyncIOMotorClient

<span style="color: #AA22FF">@asyncio</span><span style="color: #666666">.</span>coroutine
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield from</span> client<span style="color: #666666">.</span>db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
    <span style="color: #008000">print</span>(result)

client <span style="color: #666666">=</span> AsyncIOMotorClient()
asyncio<span style="color: #666666">.</span>get_event_loop()<span style="color: #666666">.</span>run_until_complete(f())
</pre></div>


<p>Unlike Tornado, asyncio does not include an HTTP implementation, much less a web framework. For those features, use Andrew Svetlov's aiohttp package. I wrote you <a href="http://motor.readthedocs.org/en/latest/tutorial-asyncio.html#a-web-application-with-aiohttp">a tiny example web application with Motor and aiohttp</a>.</p>
<h1 id="aggregate"><code>aggregate</code></h1>
<p><a href="http://motor.readthedocs.org/en/latest/api/motor_collection.html#motor.motor_tornado.MotorCollection.aggregate"><code>MotorCollection.aggregate</code></a> now returns a cursor by default, and the cursor
is returned immediately without a <code>yield</code>. The old syntax is no longer
supported:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.4 and older, no longer supported.</span>
cursor <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>aggregate(pipeline, cursor<span style="color: #666666">=</span>{})
<span style="color: #008000; font-weight: bold">while</span> (<span style="color: #008000; font-weight: bold">yield</span> cursor<span style="color: #666666">.</span>fetch_next):
    doc <span style="color: #666666">=</span> cursor<span style="color: #666666">.</span>next_object()
    <span style="color: #008000">print</span>(doc)
</pre></div>


<p>In Motor 0.5, simply do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5: no &quot;cursor={}&quot;, no &quot;yield&quot;.</span>
cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>aggregate(pipeline)
<span style="color: #008000; font-weight: bold">while</span> (<span style="color: #008000; font-weight: bold">yield</span> cursor<span style="color: #666666">.</span>fetch_next):
    doc <span style="color: #666666">=</span> cursor<span style="color: #666666">.</span>next_object()
    <span style="color: #008000">print</span>(doc)
</pre></div>


<p>In asyncio this uses <code>yield from</code> instead:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5 with asyncio.</span>
cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>aggregate(pipeline)
<span style="color: #008000; font-weight: bold">while</span> (<span style="color: #008000; font-weight: bold">yield from</span> cursor<span style="color: #666666">.</span>fetch_next):
    doc <span style="color: #666666">=</span> cursor<span style="color: #666666">.</span>next_object()
    <span style="color: #008000">print</span>(doc)
</pre></div>


<h1 id="python-35">Python 3.5</h1>
<p>Motor is now compatible with Python 3.5, which required some effort.
It was hard because Motor doesn't just work with your coroutines, it uses coroutines internally to implement
some of its own features, like <a href="http://motor.readthedocs.org/en/latest/api/motor_client.html#motor.motor_tornado.MotorClient.open"><code>MotorClient.open</code></a> and <a href="http://motor.readthedocs.org/en/latest/api/gridfs.html#motor.motor_tornado.MotorGridFS.put"><code>MotorGridFS.put</code></a>. I had a method for writing coroutines that worked in Python 2.6 through 3.4, but 3.5 finally broke it. There is no single way to return a value from a Python 3.5 native coroutine
or a Python 2 generator-based coroutine, so all Motor internal coroutines that
return values were rewritten with callbacks. (See <a href="https://github.com/mongodb/motor/commit/dc19418c">commit message dc19418c</a> for an explanation.)</p>
<h1 id="async-and-await"><code>async</code> and <code>await</code></h1>
<p>This is the payoff for my Python 3.5 effort. Motor works with native coroutines, written with the <code>async</code> and
<code>await</code> syntax:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">async <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    await collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</pre></div>


<p>Cursors from <a href="http://motor.readthedocs.org/en/latest/api/motor_collection.html#motor.motor_tornado.MotorCollection.find"><code>MotorCollection.find</code></a>, <a href="http://motor.readthedocs.org/en/latest/api/motor_collection.html#motor.motor_tornado.MotorCollection.aggregate"><code>MotorCollection.aggregate</code></a>, or
<a href="http://motor.readthedocs.org/en/latest/api/gridfs.html#motor.motor_tornado.MotorGridFS.find"><code>MotorGridFS.find</code></a> can be iterated elegantly and very efficiently in native
coroutines with <code>async for</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">async <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    async <span style="color: #008000; font-weight: bold">for</span> doc <span style="color: #AA22FF; font-weight: bold">in</span> collection<span style="color: #666666">.</span>find():
        <span style="color: #008000">print</span>(doc)
</pre></div>


<p>How efficient is this? For a collection with 10,000 documents, this old-style code takes 0.14 seconds on my system:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5 with Tornado.</span>
<span style="color: #AA22FF">@gen</span><span style="color: #666666">.</span>coroutine
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    <span style="color: #008000; font-weight: bold">while</span> (<span style="color: #008000; font-weight: bold">yield</span> cursor<span style="color: #666666">.</span>fetch_next):
        doc <span style="color: #666666">=</span> cursor<span style="color: #666666">.</span>next_object()
        <span style="color: #008000">print</span>(doc)
</pre></div>


<p>The following code, which simply replaces <code>gen.coroutine</code> and <code>yield</code> with <code>async</code> and <code>await</code>, performs about the same:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5 with Tornado, using async and await.</span>
async <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    <span style="color: #008000; font-weight: bold">while</span> (await cursor<span style="color: #666666">.</span>fetch_next):
        doc <span style="color: #666666">=</span> cursor<span style="color: #666666">.</span>next_object()
        <span style="color: #008000">print</span>(doc)
</pre></div>


<p>But with <code>async for</code> it takes 0.04 seconds, three times faster!</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5 with Tornado, using async for.</span>
async <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    async <span style="color: #008000; font-weight: bold">for</span> doc <span style="color: #AA22FF; font-weight: bold">in</span> cursor:
        <span style="color: #008000">print</span>(doc)
</pre></div>


<p>However, MotorCursor's <a href="http://motor.readthedocs.org/en/latest/api/motor_cursor.html#motor.motor_tornado.MotorCursor.to_list"><code>to_list</code></a> still reigns:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># Motor 0.5 with Tornado, using to_list.</span>
async <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()
    docs <span style="color: #666666">=</span> await cursor<span style="color: #666666">.</span>to_list(length<span style="color: #666666">=100</span>)
    <span style="color: #008000; font-weight: bold">while</span> docs:
        <span style="color: #008000; font-weight: bold">for</span> doc <span style="color: #AA22FF; font-weight: bold">in</span> docs:
            <span style="color: #008000">print</span>(doc)
        docs <span style="color: #666666">=</span> await cursor<span style="color: #666666">.</span>to_list(length<span style="color: #666666">=100</span>)
</pre></div>


<p>The function with <code>to_list</code> is twice as fast as <code>async for</code>, but it's ungraceful and requires you to choose a chunk size. I think that <code>async for</code> is stylish, and fast enough for most uses.</p>
<hr />
<p><strong>Try Me!</strong></p>
<p>I haven't always published betas before Motor releases, but this time is different. The asyncio integration is brand new. And since it required pervasive refactoring of Motor's core, the existing Tornado integration is rewritten as well. Python 3.5 support required yet another internal overhaul. I'm anxious to get early reports of all my new code in the wild.</p>
<p>Additionally, the change to <code>aggregate</code> is an API break. (There are also <a href="http://motor.readthedocs.org/en/latest/changelog.html">two subtler changes, see the changelog</a>.) So I'm giving you a chance to opt in explicitly with <code>pip install --pre</code> before I make Motor 0.5 official.</p>
<p>So please: try it out! Install the beta:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">python -m pip install --pre motor==0.5b0
</pre></div>


<p>Test your application with the new code. <a href="https://jira.mongodb.org/browse/MOTOR/">If you find issues, file a bug and I'll respond promptly.</a> And if the beta goes smoothly, don't be silent!&mdash;tweet at me <a href="https://twitter.com/jessejiryudavis">@jessejiryudavis</a> and tell me! It's the only way I'll know the beta is working for you.</p>
