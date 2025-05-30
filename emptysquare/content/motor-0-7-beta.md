+++
type = "post"
title = "Motor 0.7 Beta With Pymongo 2.9 And A Threaded Core"
date = "2016-10-03T08:28:36"
description = "Switches from greenlets to a thread pool, and updates from PyMongo 2.8 to 2.9."
category = ["Programming", "MongoDB", "Python", "Motor"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
+++

<p><img alt="Motor logo by Musho Rodney Alan Greenblat" border="0" src="motor-musho.png" style="display:block; margin-left:auto; margin-right:auto;" title="motor-musho.png"/></p>
<p>Please try the beta release of Motor 0.7 and let me know how it works for you:</p>

{{<highlight plain>}}
python -m pip install motor==0.7b0
{{< / highlight >}}

<p>Documentation:</p>
<ul>
<li><a href="https://motor.readthedocs.io/en/latest/">Motor beta documentation</a></li>
<li><a href="https://motor.readthedocs.io/en/latest/changelog.html">Motor 0.7 changelog</a></li>
</ul>
<p>In two ways, Motor 0.7 paves the way for Motor 1.0: first, its PyMongo dependency is upgraded from PyMongo 2.8 to 2.9. Second, I have abandoned my greenlet-based core in favor of a faster, simpler core built on a thread pool. Let's talk about threads first.</p>
<h1 id="threaded-core">Threaded Core</h1>
<p>From the beginning, Motor has used greenlets and an event loop to make PyMongo async. Whenever you begin a Motor method, like this:</p>

{{<highlight python3>}}
@gen.coroutine
def func():
    result = yield collection.find_one()
{{< / highlight >}}

<p>...Motor spawns a greenlet, which begins to run the corresponding PyMongo method. As soon as PyMongo wants to do I/O, Motor pauses its greenlet and schedules the I/O on Tornado's or asyncio's event loop. When the I/O completes, Motor resumes the greenlet, and so on until the PyMongo method completes. Then Motor injects the greenlet's return value into your coroutine at the "yield" site. This is as complex as it sounds, and difficult to maintain, and a little slow.</p>
<p>For asynchronous I/O, Motor now uses a thread pool. It no longer needs the
<code>greenlet</code> package, and it now requires the <code>futures</code> backport package on
Python 2.</p>
<p><a href="/response-to-asynchronous-python-and-databases/">As I wrote last year</a>, my thinking about async Python and databases has changed. I now distinguish between two features of an async database driver:</p>
<ul>
<li>Present an async API for your coroutines with <code>yield</code> or <code>await</code></li>
<li>Talk to the database with non-blocking sockets and the event loop</li>
</ul>
<p>I still think the first feature is important, but I changed my mind about the second.</p>
<p>Why isn't the event loop best for database communications? It's because database operations should be quick. Since their durations are short, the connection pool doesn't grow past a few dozen sockets. Therefore, the driver should optimize for latency on a few connections, rather than optimizing for RAM on a huge number of connections. Threading takes more RAM than evented I/O, but it's faster in Python, so I've switched to threads. <a href="https://jira.mongodb.org/browse/MOTOR-112?focusedCommentId=1376428&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-1376428">On one of my benchmarks, the new core is 35% faster</a>.</p>
<p>Motor still presents the same async API for your coroutines. You can wait for results like this with Tornado and Python 2:</p>

{{<highlight python3>}}
@gen.coroutine
def func():
    result = yield collection.find_one()
{{< / highlight >}}

<p>Or like this with Tornado or asyncio on Python 3:</p>

{{<highlight python3>}}
async def func():
    result = await collection.find_one()
{{< / highlight >}}

<h1 id="pymongo-29x">PyMongo 2.9.x</h1>
<p>The new core is not only faster, it's also simpler, which makes it easier to port to newer PyMongo versions. I upgraded the PyMongo dependency from 2.8.0 to 2.9.x, and wrapped PyMongo 2.9's new APIs.</p>
<p>PyMongo 2.9 is a bridge version that implements both the old PyMongo 2 interface and the new PyMongo 3 interface. For you, this means you can still use old PyMongo APIs with Motor 0.7, but all the new PyMongo 3 APIs are available for you to port to.</p>
<p>For example, you can still mutate a read preference:</p>

{{<highlight python3>}}
client = MotorClient()
db = client.test_database
db.read_preference = ReadPreference.SECONDARY
{{< / highlight >}}

<p>But since <a href="http://api.mongodb.com/python/current/migrate-to-pymongo3.html#the-read-preference-attribute-is-immutable">mutating read preferences is prohibited in PyMongo 3</a>, it'll be prohibited in Motor 1.0 as well. Take this opportunity to update your code for the new style:</p>

{{<highlight python3>}}
client = MotorClient()
db = client.get_database(read_preference=ReadPreference.SECONDARY)
{{< / highlight >}}

<p>Most of Motor 1.0's API is now implemented in Motor 0.7, and APIs that will be removed in
Motor 1.0 are deprecated and raise warnings. See the
<a href="https://motor.readthedocs.io/en/stable/changelog.html#motor-1-0">Motor Migration Guide</a> to prepare your code for Motor 1.0.</p>
<h1 id="roadmap">Roadmap</h1>
<p>I intend to release Motor 1.0 by the end of this quarter. It will be the first API-stable release—that means I promise no more backwards-breaking changes until some distant future. The latest Motor will wrap the latest PyMongo, and support the latest MongoDB server features.</p>
<p>But I can't do all this without you! We need to validate Motor 0.7 first.  So try the beta and <a href="https://twitter.com/jessejiryudavis">let me know</a>—if it has bugs, I need to hear about it from you, and if it works, I need to hear that also.</p>
