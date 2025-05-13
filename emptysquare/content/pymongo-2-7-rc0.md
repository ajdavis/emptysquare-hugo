+++
type = "post"
title = "Announcing PyMongo 2.7 release candidate"
date = "2014-02-15T15:20:14"
description = "Try it out: \"pip install https://github.com/mongodb/mongo-python-driver/archive/2.7rc0.tar.gz\""
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "Green_leaf_leaves.jpg"
draft = false
+++

<p><a href="http://commons.wikimedia.org/wiki/File:Green_leaf_leaves.jpg"><img alt="Leaf" src="Green_leaf_leaves.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Leaf"/></a></p>
<p>Yesterday afternoon Bernie Hackett and I shipped a release candidate for PyMongo 2.7, with substantial contributions from Amalia Hawkins and Kyle Erf. This version supports new features in the upcoming MongoDB 2.6, and includes major internal improvements in the driver code. We rarely make RCs before releases, but given the scope of changes it seems wise.</p>
<p>Install the RC like:</p>

{{<highlight plain>}}
pip install \
  https://github.com/mongodb/mongo-python-driver/archive/2.7rc0.tar.gz
{{< / highlight >}}

<p>Please <a href="https://jira.mongodb.org/browse/PYTHON">tell us if you find bugs</a>.</p>
<h1 id="mongodb-26-support">MongoDB 2.6 support</h1>
<p>For the first time in years, the MongoDB wire protocol is changing. Bernie Hackett updated PyMongo to support the new protocol, while maintaining backwards compatibility with old servers. He also added support for MongoDB's new <code>parallelCollectionScan</code> command, which <a href="https://pymongo.readthedocs.io/en/stable/api/pymongo/collection.html#pymongo.collection.Collection.parallel_scan">scans a whole collection with multiple cursors in parallel</a>.</p>
<p>Amalia Hawkins wrote a feature for <a href="https://pymongo.readthedocs.io/en/stable/api/pymongo/cursor.html#pymongo.cursor.Cursor.max_time_ms">setting a server-side timeout for long-running operations</a> with the <code>max_time_ms</code> method:</p>

{{<highlight python3>}}
try:
    for doc in collection.find().max_time_ms(1000):
        pass
except ExecutionTimeout:
    print "Aborted after one second."
{{< / highlight >}}

<p>She also added support for the new aggregation operator, <code>$out</code>, which <a href="http://docs.mongodb.org/master/reference/operator/aggregation/out/">creates a collection directly from an aggregation pipeline</a>. While she was at it, she made PyMongo log a warning whenever your read preference is "secondary" but a command has to run on the primary:</p>

{{<highlight python3>}}
>>> client = MongoReplicaSetClient(
...     'localhost',
...     replicaSet='repl0',
...     read_preference=ReadPreference.SECONDARY)
>>> client.db.command({'reIndex': 'collection'})
UserWarning: reindex does not support SECONDARY read preference
and will be routed to the primary instead.
{'ok': 1}
{{< / highlight >}}

<h1 id="bulk-write-api">Bulk write API</h1>
<p>Bernie added a <a href="https://pymongo.readthedocs.io/en/stable/examples/bulk.html">bulk write API</a>. It's now possible to specify a series of inserts, updates, upserts, replaces, and removes, then execute them all at once:</p>

{{<highlight python3>}}
bulk = db.collection.initialize_ordered_bulk_op()
bulk.insert({'_id': 1})
bulk.insert({'_id': 2})
bulk.find({'_id': 1}).update({'$set': {'foo': 'bar'}})
bulk.find({'_id': 3}).remove()
result = bulk.execute()
{{< / highlight >}}

<p>PyMongo collects the operations into a minimal set of messages to the server. Compared to the old style, bulk operations have lower network costs. You can use PyMongo's bulk API with any version of MongoDB, but you only get the network advantage when talking to MongoDB 2.6.</p>
<h1 id="improved-c-code">Improved C code</h1>
<p>After great effort, I understand why our C extensions didn't like running in <code>mod_wsgi</code>. I <a href="/python-c-extensions-and-mod-wsgi">wrote an explanation</a> that's more detailed than you want to read. But even better, Bernie fixed our C code so <code>mod_wsgi</code> no longer slows it down or makes it log weird warnings. Finally, I put <a href="https://pymongo.readthedocs.io/en/stable/examples/mod_wsgi.html">clear configuration instructions</a> in the PyMongo docs.</p>
<p>Bernie fixed all remaining platform-specific C code. Now you can run PyMongo with its C extensions on ARM, for example if you talk to MongoDB from a Raspberry Pi.</p>
<h1 id="thundering-herd">Thundering herd</h1>
<p>I overhauled <code>MongoClient</code> so its concurrency control is closer to <a href="/wasps-nest-read-copy-update-python/">what I did for <code>MongoReplicaSetClient</code> in the last release</a>. With the new MongoClient, a heavily multithreaded Python application will be much more robust in the face of network hiccups or downed MongoDB servers. You can read details in the <a href="https://jira.mongodb.org/browse/PYTHON-487">bug report</a>.</p>
<h1 id="gridfs-cursor">GridFS cursor</h1>
<p>We had several feature requests for querying <a href="http://docs.mongodb.org/manual/reference/glossary/#term-gridfs">GridFS</a> with PyMongo, so Kyle Erf implemented a GridFS cursor:</p>

{{<highlight python3>}}
>>> fs = gridfs.GridFS(client.db)
>>> # Find large files:
...
>>> fs.find({'length': {'$gt': 1024}}).count()
42
>>> # Find files whose names start with "Kyle":
...
>>> pattern = bson.Regex('kyle.*', 'i')
>>> cursor = fs.find({'filename': pattern})
>>> for grid_out_file in cursor:
...     print grid_out_file.filename
...
Kyle
Kyle1
Kyle Erf
{{< / highlight >}}

<p>You can <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/12892">browse all 53 new features and fixes</a> in our tracker.</p>
<p>Enjoy!</p>
