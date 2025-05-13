+++
type = "post"
title = "PyMongo 2.6.1 Released With Refleak Fix"
date = "2013-09-04T14:56:49"
description = "Yesterday we released PyMongo 2.6.1, which fixes a memory leak in insert()."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "leak.jpg"
draft = false
+++

<p><a href="http://www.flickr.com/photos/usnavy/7684409578/"><img alt="Leak" src="leak.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Leak"/></a></p>
<p>Bernie Hackett and I released <a href="https://pypi.python.org/pypi/pymongo/2.6.1">PyMongo 2.6.1</a> yesterday. This version fixes a bug in PyMongo 2.6, <a href="https://jira.mongodb.org/browse/PYTHON-564">a reference-count leak</a> in <code>insert()</code> that caused memory to grow slowly without bound. Please upgrade immediately.</p>
<p>Sorry about the bug. We introduced it into PyMongo's C code while implementing <a href="https://jira.mongodb.org/browse/PYTHON-414">auto-splitting for very large batch inserts</a>, but it affects all calls to <code>insert</code> regardless of size. If you use PyMongo without building its C extensions, for example if you're on PyPy or Jython, the bug does not affect you.</p>
<p>The new auto-splitting code serializes a sequence of documents as BSON until its buffer reaches 48MB, at which point it calls, from C, the Python method <code>_send_message</code> to fire off the batch to the server. Unfortunately, the C code didn't dereference the server response from <code>_send_message</code>. The response is small, something like this:</p>

{{<highlight python3>}}
{'ok': 1.0, 'err': None, 'n': 0, 'connectionId': 123}
{{< / highlight >}}

<p>Each response was leaked, and the memory added up fast if you called <code>insert</code> in a tight loop. The fix is <a href="https://github.com/mongodb/mongo-python-driver/commit/d8faa7af0005538522372df8ebefdb255cd96c23">simply to decref the response</a>.</p>
