+++
type = "post"
title = "Announcing PyMongo 3.0.1"
date = "2015-04-21T17:10:54"
description = "Fixes a few critical bugs discovered in PyMongo 3.0."
category = ["Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "pymongo-301-leaf@240.jpg"
draft = false
disqus_identifier = "5536bc955393741c76451331"
disqus_url = "https://emptysqua.re/blog/5536bc955393741c76451331/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-301-leaf.jpg" alt="Leaf" title="Leaf" /></p>
<p>It's my pleasure to announce the release of <a href="https://pypi.python.org/pypi/pymongo/">PyMongo 3.0.1</a>, a bugfix release that addresses issues discovered since PyMongo 3.0 was released a couple weeks ago. The main bugs were related to queries and cursors in complex sharding setups, but there was an unintentional change to the return value of <code>save</code>, GridFS file-deletion didn't work properly, passing a hint with a count didn't always work, and there were some obscure bugs and undocumented features.</p>
<p>For the full list of bugs fixed in PyMongo 3.0.1, please <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/15322">see the release in Jira</a>.</p>
<p>If you are using PyMongo 3.0, please upgrade immediately.</p>
<p>If you are on PyMongo 2.8, <a href="http://api.mongodb.org/python/current/changelog.html">read the changelog for major API changes in PyMongo 3</a>, and test your application carefully with PyMongo 3 before deploying.</p>
