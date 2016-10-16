+++
type = "post"
title = "Motor 0.1 Migration Instructions"
date = "2013-03-07T11:42:17"
description = "If you've been using Motor prior to the 0.1 release, here's how to upgrade."
categories = ["Mongo", "Motor", "Programming", "Python"]
tags = []
enable_lightbox = false
draft = false
+++

<p>Motor (which is indeed my non-blocking driver for MongoDB and Tornado) <a href="/blog/motor-officially-released/">had a 0.1 release to PyPI yesterday</a>. It had an odd history prior, so there are various versions of the code that you, dear reader, may have installed on your system. All you need to do is:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>pip uninstall pymongo motor
<span style="color: #19177C">$ </span>pip install motor
</pre></div>


<p>Motor will pull in the official PyMongo, plus Tornado and Greenlet, as dependencies. You should now have Motor 0.1 and PyMongo 2.4.2:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">pymongo</span>
<span style="color: #666666">&gt;&gt;&gt;</span> pymongo<span style="color: #666666">.</span>version
<span style="color: #BA2121">&#39;2.4.2&#39;</span>
<span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">motor</span>
<span style="color: #666666">&gt;&gt;&gt;</span> motor<span style="color: #666666">.</span>version
<span style="color: #BA2121">&#39;0.1&#39;</span>
</pre></div>


<p>(The lore is: I started Motor last year in a branch of my fork of PyMongo, so you could've installed an experimental version of <strong>both</strong> PyMongo and Motor from there. Then we transferred Motor into its own repo within the MongoDB.org organization on January 15. And on February 1st a zealous fan actually grabbed the "Motor" package name on PyPI and uploaded my code to it, then transferred ownership to me, just to make sure I could use the name Motor.)</p>
    