+++
type = "post"
title = "Announcing PyMongo 3.0.3"
date = "2015-07-01T10:06:58"
description = "A minor bugfix release."
category = ["Mongo", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "tree-python@240.jpg"
draft = false
disqus_identifier = "5593f3a95393741c65d32a70"
disqus_url = "https://emptysqua.re/blog/5593f3a95393741c65d32a70/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tree-python.jpg" alt="Tree python" title="Tree python" /></p>
<p>Bernie Hackett, Luke Lovett, Anna Herlihy, and I are pleased to announce <a href="https://pypi.python.org/pypi/pymongo/3.0.3">PyMongo 3.0.3</a>. This release fixes bugs reported since PyMongo 3.0.2&mdash;most importantly, <a href="https://jira.mongodb.org/browse/PYTHON-932">a bug that broke Kerberos authentication</a>. We also fixed a <a href="https://jira.mongodb.org/browse/PYTHON-934">TypeError if you try to turn off SSL hostname validation using an option in the MongoDB connection string</a>, and <a href="https://jira.mongodb.org/browse/PYTHON-951">an infinite loop reading certain kinds of corrupt GridFS files</a>.</p>
<p>For the full list of bugs fixed in PyMongo 3.0.3, please <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/15528">see the release in Jira</a>.</p>
<ul>
<li><a href="http://pypi.python.org/pypi/pymongo/3.0.3">Downloads</a></li>
<li><a href="http://api.mongodb.org/python/3.0.3/changelog.html">Change Log</a> </li>
<li><a href="http://api.mongodb.org/python/3.0.3/index.html">Documentation</a></li>
</ul>
<p>If you use PyMongo 3.0.x, upgrade.</p>
<p>If you are on PyMongo 2.8.x, you should probably wait to upgrade: we are about to make it easier for you. PyMongo 2.9, which will be released shortly, provides a smooth bridge for you to upgrade from the old API to the new one.</p>
<p>Let us know if you have any problems by <a href="https://jira.mongodb.org/browse/PYTHON">opening a ticket in Jira</a>, in the PYTHON project.</p>
<hr />
<p><a href="https://www.flickr.com/photos/nasmac/531138641">Image: Ian C. on Flickr.</a></p>
