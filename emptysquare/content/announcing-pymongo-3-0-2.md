+++
type = "post"
title = "Announcing PyMongo 3.0.2"
date = "2015-05-12T19:04:36"
description = "Fixes bugs discovered in PyMongo 3.0.1."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "leaf.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="leaf.jpg" alt="Hepatica leaf" title="Hepatica leaf" /></p>
<p>Bernie Hackett and I are pleased to announce <a href="https://pypi.python.org/pypi/pymongo/3.0.2">PyMongo 3.0.2</a>. This release fixes bugs reported since PyMongo 3.0.1&mdash;most importantly, a bug that could route operations to replica set members that are not in primary or secondary state when using read preference <code>PrimaryPreferred</code> or <code>Nearest</code>.</p>
<p>For the full list of bugs fixed in PyMongo 3.0.2, please <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/15430">see the release in Jira</a>.</p>
<p>If you use PyMongo 3.0.x, upgrade.</p>
<p>If you are on PyMongo 2.8.0, upgrade to <a href="/announcing-pymongo-2-8-1/">yesterday's bugfix release PyMongo 2.8.1 instead</a>. <a href="https://pymongo.readthedocs.io/en/stable/changelog.html">Read the changelog for major API changes in PyMongo 3</a>, and test your application carefully with PyMongo 3.0.x before deploying.</p>
