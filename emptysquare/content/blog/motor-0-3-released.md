+++
type = "post"
title = "Motor 0.3 Released"
date = "2014-06-16T22:05:29"
description = "No new features. Now supports Python 2 and 3 single-source."
categories = ["Mongo", "Motor", "Programming", "Python"]
tags = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today I released Motor 0.3. This version has no new features compared to Motor 0.2.1. Here's what I changed:</p>
<ul>
<li>I updated the PyMongo dependency from 2.7 to 2.7.1, therefore inheriting <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/13823">PyMongo 2.7.1&rsquo;s bug fixes</a>.</li>
<li>Motor continues to support Python 2.6, 2.7, 3.3, and 3.4, but now with single-source. <code>2to3</code> no longer runs during installation with Python 3.</li>
<li><code>nosetests</code> is no longer required for regular Motor tests.</li>
<li>I <a href="https://jira.mongodb.org/browse/MOTOR-34">fixed a mistake</a> in the docs for <code>aggregate()</code>.</li>
</ul>
<p>Rewriting Motor to support Python 2 and 3 in the same source code makes life sane for me, and it reflects the current consensus about the best way to write portable Python. It wasn't terribly difficult either.</p>
<p>Now that I've simplified Motor's Python 3 support, I'm ready to tackle the next big challenge: I want to see if Motor can support Twisted and asyncio, in addition to Tornado. Wish me luck.</p>
    