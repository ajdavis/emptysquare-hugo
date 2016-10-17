+++
type = "post"
title = "Announcing Motor 0.4.1"
date = "2015-05-09T12:07:05"
description = "One critical bugfix."
"blog/category" = ["Mongo", "Motor", "Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
legacyid = "554e0d3f5393741c64c21709"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>I received an <a href="https://jira.mongodb.org/browse/MOTOR-66">extraordinarily helpful bug report</a> yesterday from Brent Miller, who showed me that Motor's replica set client hangs if it tries two operations at once, <em>while</em> it is setting up its initial connection. He sent a script that not only reproduces the hang, but diagnoses it, too, by regularly dumping all threads' stacks to a file.</p>
<p>A report this generous made my work easy. I found that I'd caused this bug while fixing another one. In the previous bug, if Motor's replica set client was under load while reconnecting to your servers, it could start multiple greenlets to monitor your replica set, instead of just one. (Eventually, Motor will be <em>designed</em> to start multiple greenlets and <a href="/blog/announcing-pymongo-3/#replica-set-discovery-and-monitoring">monitor all servers in parallel, the same as PyMongo 3</a>, but for now, starting multiple monitor greenlets is a bug.)</p>
<p>I fixed that bug overzealously: now if you start multiple operations on a replica set client as it connects, it does not start the monitor greenlet at all, and deadlocks. Motor 0.4.1 gets it right. It starts one and only one monitor greenlet as it connects to your replica set. Get it from PyPI:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install motor==0.4.1
</pre></div>
    