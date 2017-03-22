+++
type = "post"
title = "Update on Motor and asyncio"
date = "2015-08-05T09:54:52"
description = "The roadmap for asyncio support, plus \"async\" and \"await\" in Python 3.5."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "55c031ce5393741c65d3ac8b"
disqus_url = "https://emptysqua.re/blog/55c031ce5393741c65d3ac8b/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>I want to update you about <a href="http://motor.readthedocs.org/en/stable/">Motor</a>, my asynchronous Python driver for
MongoDB and Tornado. Motor development has been on hiatus since January while I concentrated on my tasks for <a href="/announcing-pymongo-3/">PyMongo 3</a>. After PyMongo 3, I took over as the lead for <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the MongoDB C Driver, and most of my Python work ceased.</p>
<h1 id="spring-break">Spring Break</h1>
<p>Spring was a good time for me to take a break from Motor. It is actually
possible for Motor to be finished, at least for periods. It does one
thing well: it integrates MongoDB with Tornado, probably the most popular
Python async framework. Motor's limited scope lets it rest peacefully for
months, feature-complete and free of major bugs. While Motor
quiesced like this, I devoted myself to <a href="/server-discovery-and-monitoring-in-pymongo-perl-and-c/">writing the Server Discovery
And Monitoring Spec</a>, then to implementing that spec in PyMongo 3, and
then to relearning C fast enough to keep up with libmongoc's demands.</p>
<p>At the time I set Motor aside, I had begun integrating it
with Python 3.4's new asyncio module, so you could choose between
asyncio and Tornado. I adapted a portion of the Motor-on-Tornado test
suite into a Motor-on-asyncio suite and got it passing, with good
confidence that the rest of the suite would pass once ported. The
remaining tasks to make the asyncio integration production-ready were
certainly tractable. Meanwhile, I had developed substantial features
and bugfixes on the Motor 0.4 release branch, so the next step was to
merge the two branches. But with asyncio not yet widely used, and more
urgent work looming, I put down the asyncio integration. That was
where I expected it to sit until autumn, if not longer.</p>
<h1 id="presents">Presents</h1>
<p>But I recently received two surprise gifts. First, in April, R&eacute;mi Jolin stepped
in and did the hard work of <a href="https://github.com/mongodb/motor/pull/18">merging 97 commits from the Motor 0.4
release branch into the asyncio branch</a>, and fixing up the result: now
Motor's master branch has both the asyncio integration <em>and</em> the fixes and features needed to become Motor
0.5.</p>
<p>My second gift arrived in June when Andrew Svetlov, one of
asyncio's main authors, wrote to say he wants to finish the
integration so he can use asyncio with MongoDB in production. Andrew
and his colleague Nikolay Novik at DataRobot in Ukraine are porting the remainder of Motor's tests to asyncio, and
they'll refactor how Motor uses asyncio's streams to benefit from the
framework's latest features.</p>
<h1 id="async-and-await">"async" and "await"</h1>
<p>So Motor speeds forward, with my hand only lightly on the wheel. I
hope for an asyncio-compatible Motor 0.5 this fall.</p>
<p>While I'm at it, it should be an easy win, and a huge one, to add support for Python 3.5's new "async" and "await" keywords defined in <a href="https://www.python.org/dev/peps/pep-0492/">PEP 492</a>. So I plan to add support for them in Motor 0.5 as well&mdash;the enhancements will make Motor cursors faster and more convenient with asyncio <em>and</em> Tornado!</p>
<h1 id="prospects">Prospects</h1>
<p>The new Motor will
still wrap the outdated PyMongo 2.8, however. So my next priority, after Motor 0.5 is released, is to
port Motor to PyMongo 3 to take advantage of <a href="/announcing-pymongo-3/">PyMongo's new features</a>:
its implementation of the <a href="/server-discovery-and-monitoring-in-pymongo-perl-and-c/">Server Discovery and Monitoring Spec</a>, the
<a href="https://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">Server Selection Spec</a>, and the <a href="https://www.mongodb.com/blog/post/consistent-crud-api-next-generation-mongodb-drivers">new CRUD API</a>. This will make Motor much
more scalable when connected to large replica sets, and makes its API
consistent with our other drivers. That may merit the name Motor 1.0.</p>
<p>And after that? In the next year, Motor will need new features to
fully support MongoDB 3.2.</p>
<p>Farther out, my work on asyncio integration has convinced me that it's
feasible for Motor to someday work with Twisted, too. PyMongo already supports Gevent, so if Motor does Twisted then all major async frameworks
will be supported by official drivers. There will be no more excuse
for async Python applications not to use MongoDB.</p>
