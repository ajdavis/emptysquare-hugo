+++
category = ['MongoDB', 'Motor', 'Python', 'Programming']
date = '2016-11-02T18:23:39.635333'
description = 'Motor 1.0 is the first API-stable release. It wraps PyMongo 3.3+ and supports the latest MongoDB features.'
draft = false
tag = []
thumbnail = 'motor-musho.png'
title = 'Announcing Motor 1.0'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor logo by Musho Rodney Alan Greenblat" title="motor-musho.png" border="0" /></p>

More than four years ago, I was sitting through a particularly distracted period of meditation. It was a Saturday morning and I was sitting on a meditation cushion next to my girlfriend in her Brooklyn apartment, staring at the wall. I suddenly thought of a technique for turning PyMongo into an async driver without rewriting it from scratch, by using greenlets. That weekend I forked PyMongo [and demonstrated a proof of concept](https://github.com/ajdavis/mongo-python-driver/commit/f4cf72300fd84b23a1adf43c4bf226ec987d17b5) to my boss.

Since then, I've spun off my async driver as a distinct project called Motor, named for "Mongo + Tornado". It took me more than a year to release Motor 0.1, amid my other duties at MongoDB. Time passed, life moved on. MongoDB moved from Soho to Times Square, my girlfriend and I moved in together in Stuyvesant Town, and two generations of dwarf hamsters passed through our home. I occasionally released Motor updates. [Version 0.5 added support for asyncio and for Python's new "async" and "await" keywords](/motor-0-5-asyncio-async-await-keywords/). Version 0.7 was the most momentous, because it abandoned the idea I'd had while staring at the wall in Jennifer's apartment: [Motor stopped using greenlets, in favor of a thread pool](/motor-0-7-beta/).

Motor 1.0 arrived today. This version wraps PyMongo 3.3 or newer, so it supports the latest MongoDB features and the latest PyMongo API. The move from PyMongo 2 to 3 brings a bunch of breaking API changes, please read [Motor 1.0 Migration Guide](http://motor.readthedocs.io/en/stable/migrate-to-motor-1.html) and the [PyMongo 3 changelog](http://api.mongodb.com/python/current/changelog.html#changes-in-version-3-0) carefully!

Peace,  
&mdash;A. Jesse Jiryu Davis
