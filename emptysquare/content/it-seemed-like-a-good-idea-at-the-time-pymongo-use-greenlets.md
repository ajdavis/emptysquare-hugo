+++
type = "post"
title = "It Seemed Like A Good Idea At The Time: PyMongo's \"use_greenlets\""
date = "2014-12-05T10:23:34"
description = "Second in a four-part series about choices we regretted in the design of PyMongo."
category = ["MongoDB", "Programming", "Python"]
tag = ["gevent", "good-idea-at-the-time", "pymongo"]
enable_lightbox = false
thumbnail = "road.jpg"
draft = false
disqus_identifier = "5478deb753937409607d8cc8"
disqus_url = "https://emptysqua.re/blog/5478deb753937409607d8cc8/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="road.jpg" alt="Road" title="Road" /></p>
<p><em>The road to hell is paved with good intentions.</em></p>
<p>This is the second of <a href="/good-idea-at-the-time-pymongo/">a four-part series on regrettable decisions we made when we designed PyMongo</a>. This winter we're preparing PyMongo 3.0, and we have an opportunity to make big changes. I'm putting our regrettable designs to rest, and writing their epitaphs as I go.</p>
<p>Last week <a href="/good-idea-at-the-time-pymongo-start-request/">I wrote about the first regrettable decision, "start_request"</a>. Today I'll tell you the story of the second: PyMongo and Gevent.</p>
<div class="toc">
<ul>
<li><a href="#the-invention-of-use_greenlets">The Invention Of "use_greenlets"</a></li>
<li><a href="#half-a-feature">Half A Feature</a></li>
<li><a href="#youthful-indiscretion">Youthful Indiscretion</a></li>
<li><a href="#the-death-of-use_greenlets">The Death Of "use_greenlets"</a></li>
<li><a href="#post-mortem">Post-Mortem</a></li>
</ul>
</div>
<hr />
<h1 id="the-invention-of-use_greenlets">The Invention Of "use_greenlets"</h1>
<p>As I described in last week's article, I committed my first big changes to connection pooling in PyMongo in March 2012. Once I'd improved PyMongo's connection pool for multi-threaded applications, my boss Bernie asked me to improve PyMongo's compatibility with Gevent. The main problem was, PyMongo wanted to reserve a socket for each thread, but Gevent uses <a href="https://greenlet.readthedocs.org/">greenlets</a> in place of threads. I didn't know Gevent well, but I forged ahead.</p>
<!--

Gevent Release 0.13.0 (Jul 14, 2010)

Release highlights:

Added gevent.local module. Fixed issue #24. Thanks to Ted Suzman.

https://code.google.com/p/gevent/issues/detail?id=24

-->

<p>I <a href="https://github.com/mongodb/mongo-python-driver/commit/72d780081252c72be004ba483b1ed16f7ec6a490">added a "use_greenlets" option to PyMongo</a>; if True, PyMongo reserved a socket for each greenlet. I made a separate connection pool class called GreenletPool: it shared most of its code with the standard Pool, but instead of using a threadlocal to associate sockets with threads, it used a simple dict to associate sockets with greenlets. A <a href="https://docs.python.org/2/library/weakref.html#weakref.ref">weakref callback</a> ensured that the greenlet's socket was reclaimed when the greenlet died.</p>
<h1 id="half-a-feature">Half A Feature</h1>
<p>The "use_greenlet" option and the GreenletPool didn't add too much complexity to PyMongo. But my error was this: I only gave Gevent users half a feature. My "improvement" was as practical as adding half a wheel to a bicycle.</p>
<p>At the time, I clearly described my half-feature in PyMongo's documentation:</p>
<blockquote>
<p><strong>Using Gevent Without Threads</strong></p>
<p>Typically when using Gevent, you will run <code>from gevent import monkey; monkey.patch_all()</code> early in your program's execution. From then on, all thread-related Python functions will act on greenlets instead of threads, and PyMongo will treat greenlets as if they were threads transparently. Each greenlet will use a socket exclusively by default.</p>
<p><strong>Using Gevent With Threads</strong></p>
<p>If you need to use standard Python threads in the same process as Gevent and greenlets, you can run only <code>monkey.patch_socket()</code>, and create a Connection instance with <code>use_greenlets=True</code>. The Connection will use a special greenlet-aware connection pool that allocates a socket for each greenlet, ensuring consistent reads in Gevent.</p>
<p>ReplicaSetConnection with <code>use_greenlets=True</code> will also use a greenlet-aware pool. Additionally, it will use a background greenlet instead of a background thread to monitor the state of the replica set.</p>
</blockquote>
<p>Hah! In my commit message, I claimed I'd "improved Gevent compatibility." What exactly did I mean? I meant you could use PyMongo after calling Gevent's <code>patch_socket()</code> without having to call <code>patch_thread()</code>. But who would do that? What conceivable use case had I enabled? After all, once you've called <code>patch_socket()</code>, regular multi-threaded networking code doesn't work. So I had <em>not</em> allowed you to mix Gevent and non-Gevent code in one application.</p>
<p><strong>Update</strong>: Peter Hansen explained to me exactly what I was missing, and <a href="/pymongo-use-greenlets-followup/">I've written a followup article in response</a>.</p>
<p>What was I thinking? Maybe I thought "use_greenlets" worked around <a href="https://code.google.com/p/gevent/issues/detail?id=24">a bug in Gevent's threadlocals</a>, but Gevent fixed that bug two years prior, so that's not the answer.</p>
<p>I suppose "use_greenlets" allowed you to use PyMongo with multiple Gevent loops, one loop per OS thread. Gevent does support this pattern, but I'm uncertain how useful it is since the Global Interpreter Lock prevents OS threads from running Python code concurrently. I'd written some clever code that was probably useless, and I greatly confused Gevent users about how they should use PyMongo.</p>
<h1 id="youthful-indiscretion">Youthful Indiscretion</h1>
<p>It's been three years since I added "use_greenlets". The company was so young then. We were called 10gen, and we were housed on Fifth Avenue in Manhattan, above a nail salon. The office was cramped and every seat was taken. There was no place to talk: my future boss Steve Francia interviewed me walking around Union Square. Eliot Horowitz and I negotiated my salary in the stairwell. The hardwood floors were bent and squeaky. The first day I came to work I wore motorcycle boots, and the racket they made on those bad floors made me so self-conscious I never wore them to work again. When I sat down, my chair rolled downhill from my desk and bumped into Meghan Gill behind me.</p>
<p>The company was young and so was I. When Bernie asked me to improve PyMongo's compatibility with Gevent, I should've thought much harder about what that meant. Instead of the half-feature I wrote, I should have given you either a whole feature or no feature.</p>
<p>The whole feature would have allowed you to use PyMongo with Gevent and no monkey-patching at all, provided that you set "use_greenlets". If "use_greenlets" was set to True, PyMongo would associate sockets with greenlets instead of threads, <em>and</em> it would use Gevent's socket implementation instead of the standard library's. This would allow Gevent to properly suspend the current greenlet while awaiting network I/O, but you could still mix Gevent and non-Gevent code in one application.</p>
<h1 id="the-death-of-use_greenlets">The Death Of "use_greenlets"</h1>
<p>But even better than the whole feature is no feature. So that is what I have implemented for PyMongo 3.0: in the next major release, <a href="https://jira.mongodb.org/browse/PYTHON-512">PyMongo will have no Gevent-specific code at all</a>. PyMongo will work with Gevent's <code>monkey.patch_all()</code> just like any other Python library does, and <code>use_greenlets</code> is gone. In our continuous integration server we'll test Gevent and, if practical, other monkey-patching frameworks like Eventlet and Greenhouse, to make sure they work with PyMongo. But we won't privilege Gevent over the other frameworks, nor distort PyMongo's design for the sake of a half-feature no one can use.</p>
<h1 id="post-mortem">Post-Mortem</h1>
<p>The lesson here is obvious: gather requirements. It's harder for an open source author to gather requirements than it is for a commercial software vendor, but it's far from impossible. Gevent has a mailing list, after all. At the time it didn't occur to me to discuss with Gevent users what they wanted from PyMongo.</p>
<p>Nowadays I'd know better. Especially when I'm not scratching my own itch, when I'm integrating with a library I don't use, I need to define rigorously what need I'm filling. Otherwise I'm meeting you in a foreign country with a ship full of the wrong goods for trade.</p>
<p>The same challenge presents itself to me now with Motor, my async driver for MongoDB. So far Motor has only worked with Tornado, an async framework I've used and know well. But I'm going to start integrating Motor with asyncio and, eventually, Twisted, and I need to be awfully careful about gathering requirements. One technique I'll use is <a href="/eating-your-own-hamster-food/">eating my own hamster food</a>: Before I release the version of Motor that supports asyncio, I'll port Motor-Blog, the software that runs this site, from Tornado to asyncio. That way there will be at least one real-world application that uses Motor and asyncio before I release the new version.</p>
<hr />
<p><em>The next installment in "It Seemed Like A Good Idea At The Time" is <a href="/good-idea-at-the-time-pymongo-copy-database/">PyMongo's "copy_database"</a>.</em></p>
