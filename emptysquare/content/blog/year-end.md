+++
type = "post"
title = "Year End"
date = "2013-12-25T21:51:24"
description = "The year in review: Motor, Toro, and asyncio."
categories = ["Mongo", "Programming", "Python", "Zen"]
tags = []
enable_lightbox = false
thumbnail = "hands.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="hands.jpg" alt="Hands" title="Hands" /></p>
<p>As we usually do, my girlfriend and I spent last week in Chicago with her family for Christmas, and leave tomorrow morning for <a href="http://villagezendo.org/2013-year-end/">the Village Zendo's year end meditation retreat</a>, which lasts until January 1st.</p>
<p>I've stretched myself as an open source contributor this year. In March I released the first version of <a href="http://motor.readthedocs.org/en/stable/">Motor</a>, the most complex open source project I've created. I also rewrote <a href="http://toro.readthedocs.org/">Toro</a>, a library of locks and queues for Tornado coroutines: the 0.5 release of Toro was a big leap forward. Much more significantly, I contributed my ideas from Toro to asyncio, a.k.a. Tulip. I'm so proud that <a href="http://hg.python.org/cpython/file/default/Lib/asyncio/queues.py">my queue code is in Python 3.4's standard library</a>.</p>
<p>Early next year I look forward to <a href="/blog/motor-progress-report-the-road-to-0-2/">releasing Motor 0.2</a>. After that, Bernie Hackett and I are embarking upon a partial rewrite of PyMongo. We're going to make a PyMongo that's extensible, maintainable, and fast, and we'll jettison a ton of cruft that's accumulated since the the beginning of the PyMongo project. My hope is to include in PyMongo 3.0 all the hooks needed to support a Motor 1.0 that can be maintained more easily than the current crop of Motor releases. The same hooks should make PyMongo play more nicely with Gevent, asyncio, and whatever new concurrency framework you throw at it.</p>
<p>After that? Who knows. I'm getting a little tired of Python, actually. I'm looking to branch out into C, C++, or even Go. Luckily I work for MongoDB, where there's opportunities to play with almost any programming language.</p>
<p>But starting tomorrow, everything is on hold. Zen Master Dogen said that during meditation we "put aside all involvements and suspend all affairs." I know I can't help thinking about everything I want to achieve next year, and that's fine. For now, the work is done.</p>
    