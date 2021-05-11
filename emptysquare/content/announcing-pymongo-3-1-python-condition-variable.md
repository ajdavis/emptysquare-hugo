+++
type = "post"
title = "PyMongo 3.1 Works Around A Funny Performance Flaw In Python 2"
date = "2015-11-02T18:14:46"
description = "PyMongo 3.1 implements performance monitoring, a new GridFS API, and I worked around a flaw that consumes your idle CPU."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "leaf.jpg"
draft = false
disqus_identifier = "5636490b539374098f4a0197"
disqus_url = "https://emptysqua.re/blog/5636490b539374098f4a0197/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="leaf.jpg" alt="Leaf" title="Leaf" /></p>
<p>Bernie Hackett, Anna Herlihy, Luke Lovett, and I are pleased to announce the release of PyMongo 3.1. It adds features that conform to two new cross-language driver specs: it implements the <a href="https://github.com/mongodb/specifications/blob/master/source/command-monitoring/command-monitoring.rst">Command Monitoring Spec</a> to help you measure performance, and it adds a <a href="http://api.mongodb.org/python/3.1/api/gridfs/index.html#gridfs.GridFSBucket">GridFSBucket class</a> to match our new <a href="https://github.com/mongodb/specifications/blob/master/source/gridfs/gridfs-spec.rst">GridFS Spec</a>.</p>
<p>A few of our users reported that PyMongo 3 used five or ten percent of their CPU while idle, and recorded a couple hundred context switches per second. I investigated and found a slapstick performance flaw in Python 2's condition variable that was interacting badly with my concurrency design in PyMongo 3.</p>
<h1 id="a-reasonable-tradeoff">A Reasonable Tradeoff?</h1>
<p>PyMongo 3 has new server discovery and monitoring logic which requires one background thread to monitor each server the driver is connected to. These monitors wake every 10 seconds or, when PyMongo is actively searching for a server, every half-second. This architecture has big performance advantages over PyMongo 2's&mdash;it's faster at discovering servers, and more performant and responsive if you have a large replica set, or if your replica set's topology changes, or if some members are down or slow to respond. (<a href="/announcing-pymongo-3/#responsiveness">More info here.</a>)</p>
<p>So, I expected PyMongo 3 to cost a bit of idle CPU, because its threads wake every 10 seconds to check the servers; this is intended to cost a tiny bit of memory and load in exchange for big wins in performance and reliability. But our users reported, and I confirmed, that the cost was much more than I'd guessed.</p>
<p>It is a requirement of our Server Discovery And Monitoring Spec that <a href="https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.rst#requesting-an-immediate-check">a sleeping monitor can be awakened early</a> if the driver detects a server failure. My monitors implement this using the Python standard library's <a href="https://docs.python.org/2/library/threading.html#threading.Condition.wait">Condition.wait</a> with a timeout.</p>
<p>Aside from infrequent wakeups to do their appointed chores, and occasional interruptions, monitors also wake frequently to check if they should terminate. The reason for this odd design is to avoid a deadlock in the garbage collector: a PyMongo client's destructor can't take a lock, so it can't signal the monitor's condition variable. (See <a href="/pypy-garbage-collection-and-a-deadlock/">What To Expect When You're Expiring</a>, or <a href="https://jira.mongodb.org/browse/PYTHON-863">PYTHON-863</a>.) Therefore, the only way for a dying client to terminate its background threads is to set their "stopped" flags, and let the threads see the flag the next time they wake. I erred on the side of prompt cleanup and set this frequent check interval at 100ms.</p>
<p>I figured that checking a flag and going back to sleep 10 times a second was cheap on modern machines. I was incorrect. Where did I go wrong?</p>
<h1 id="idling-hot">Idling Hot</h1>
<p>Starting in Python 3.2, the builtin C implementation of <a href="https://docs.python.org/3/library/_thread.html#_thread.lock.acquire">lock.acquire takes a timeout</a>, so condition variables wait simply by calling lock.acquire; they're <a href="https://hg.python.org/cpython/file/v3.5.0/Lib/threading.py#l261">implemented as efficiently as I expected</a>. In Python 3 on my system, an idle PyMongo client takes only 0.15% CPU.</p>
<p>But in Python 2, lock.acquire has no timeout. To wait with a timeout in Python 2, a condition variable <a href="https://hg.python.org/cpython/file/v2.7.10/Lib/threading.py#l309">sleeps a millisecond, tries to acquire the lock, sleeps twice as long, and tries again</a>. This exponential backoff reaches a maximum sleep time of 50ms.</p>
<p>The author of this algorithm, Tim Peters, commented:</p>
<blockquote>
<p>Balancing act:  We can't afford a pure busy loop, so we
have to sleep; but if we sleep the whole timeout time,
we'll be unresponsive.  The scheme here sleeps very
little at first, longer as time goes on, but never longer
than 20 times per second.</p>
</blockquote>
<p>If the whole timeout is long, this is completely reasonable. But PyMongo calls the condition variable's "wait" method in a loop with a timeout of only 100ms, so the exponential backoff is restarted 10 times a second. Each time the exponential backoff restarts, it sets its wait time back to one millisecond. Overall, the condition variable is not waking 10 times a second, but many hundreds of times.</p>
<p>In Python 2.7.10 on my system, one idle PyMongo client takes a couple percent CPU to monitor one MongoDB server. On a production server with many Python processes, each monitoring a large replica set of MongoDB servers, the overhead could be significant. It would leave less headroom for traffic spikes or require bigger hardware.</p>
<h1 id="the-simplest-solution-the-could-possibly-work">The Simplest Solution The Could Possibly Work</h1>
<p>I surprised myself with how simple the solution was: <a href="https://github.com/mongodb/mongo-python-driver/commit/b9228a3eb00fed4b1db558bc133142e6a62194e5">I ditched the condition variable</a>. In the new code, Monitor threads simply sleep half a second between checks; every half second they wake, look to see if they should ping the MongoDB server, or if they should terminate, then go back to sleep. The early wake-up feature is gone now, but since the <a href="https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring.rst#minheartbeatfrequencyms">Server Discovery And Monitoring Spec</a> prohibits monitors from checking servers more often than every half-second anyway, this is no real loss.</p>
<p>Even better, I deleted 100 lines of Python and added only 20.</p>
<p>The original bug-reporter Daniel Brandt wrote "results are looking very good." Nicola Iarocci, a MongoDB Master, chimed in: "Hello just wanted to confirm that I was also witnessing huge performance issues when running the <a href="http://python-eve.org">Eve</a> test suite under Python 2. With PyMongo 3.1rc0 however, everything is back to normal. Cheers!"</p>
<hr />
<p>Links to more info about the PyMongo 3.1 release:</p>
<ul>
<li><a href="http://api.mongodb.org/python/3.1/changelog.html">PyMongo 3.1 changelog.</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%203.1%20AND%20project%20%3D%20PYTHON">List of all issues resolved in 3.1.</a></li>
</ul>
<p><a href="https://www.flickr.com/photos/41369090@N02/3813650335"><span style="color:gray">Image: Macpedia.</span></a></p>
