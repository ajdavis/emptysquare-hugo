+++
type = "post"
title = "PyMongo 2.6 Released"
date = "2013-08-19T19:11:53"
description = "Exciting new features, and a breaking change to watch out for, in the new Python driver for MongoDB."
category = ["MongoDB", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "justin-patrin.jpg"
draft = false
+++

<p>It's my pleasure to announce that Bernie Hackett and I have released <a href="https://pypi.python.org/pypi/pymongo/">PyMongo 2.6</a>, the successor to PyMongo 2.5.2, with new features and bugfixes.</p>
<h1 id="connection-pooling">Connection Pooling</h1>
<p>The big news in PyMongo 2.6 is that the <code>max_pool_size</code> option actually means what it says now.</p>
<p>PyMongo opens sockets as needed, to support the number of concurrent operations demanded by a multithreaded application. In versions before 2.6, the default <code>max_pool_size</code> was 10, and it did not
actually bound the number of open connections; it only determined the number
of connections that would be kept open when no longer in use. Consider this code:</p>

{{<highlight python3>}}
client = MongoClient(max_pool_size=5)
{{< / highlight >}}

<p>PyMongo's old connection pool would open as many sockets as you need, without bound, during a load spike, but once the spike is over it will close all but five of them.</p>
<p>In PyMongo 2.6, max means max. The connection pool will open at most <code>max_pool_size</code> sockets to meet demand. So if your <code>max_pool_size</code> is 5, and five threads currently have MongoDB operations in progress, a sixth thread will block waiting for a socket to be returned to the pool by one of the prior threads. Obviously, this can slow down your app, so we've increased the default <code>max_pool_size</code> from 10 to 100.</p>
<p>If you haven't been specifying <code>max_pool_size</code> when you create a <code>MongoClient</code> or <code>MongoReplicaSetClient</code>, then you'll get the new default when you upgrade and you have nothing to worry about. But if you <strong>have</strong> been overriding the default, you should ensure your <code>max_pool_size</code> is large enough to match your highest expected number of concurrent operations. Sockets are only opened when needed, so there's no cost to having a <code>max_pool_size</code> larger than necessary. Err towards a larger value.</p>
<p>In addition we've added two more options: <code>waitQueueMultiple</code> caps the number of threads that can wait for sockets before PyMongo starts throwing exceptions. E.g., to keep the number of waiters less than or equal to 500:</p>

{{<highlight python3>}}
client = MongoClient(max_pool_size=50, waitQueueMultiple=10)
{{< / highlight >}}

<p>When 500 threads are waiting for a socket, additional waiters throw exceptions. Use this option to
bound the amount of queueing in your application during a load spike, at the
cost of additional exceptions.</p>
<p>Once the pool reaches its max size, additional threads are allowed to wait indefinitely for connections to become available, unless you set <code>waitQueueTimeoutMS</code>:</p>

{{<highlight python3>}}
client = MongoClient(waitQueueTimeoutMS=100)
{{< / highlight >}}

<p>A thread that waits more than 100ms (in this example) for a connection throws an exception. Use this option if it is more
important to bound the duration of operations during a load spike than it is to complete every operation.</p>
<p>All this intricate work on the connection pool was generously contributed by <a href="https://twitter.com/papercrane">Justin Patrin</a>, a developer at Idle Games.</p>
<p><img alt="Justin Patrin" src="justin-patrin.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Justin Patrin"/></p>
<p>With extraordinary patience Justin worked with us for a month to deal with our critiques and all the edge cases. Adding a feature to PyMongo's connection pool is maximally difficult. We support Python 2.4 through 3.3, PyPy, and Jython, plus Gevent, and each has very different behavior regarding concurrency, I/O, object lifetimes, and threadlocals. Our pool needs special code for each of them. Justin pounded through the bugs and made one of the best contributions PyMongo's received from an outside programmer.</p>
<h1 id="batched-inserts">Batched Inserts</h1>
<p>PyMongo's maintainer Bernie Hackett added a great new feature: if you pass <code>insert()</code> a huge list of documents, <a href="https://jira.mongodb.org/browse/PYTHON-414">PyMongo automatically splits it into 48MB chunks</a> and passes each chunk to MongoDB. In the past it was up to you to determine the largest message size MongoDB would accept and ensure your batch inserts didn't exceed it, otherwise PyMongo threw an exception. Now, you can stream an arbitrary number of documents to the server in a single method call.</p>
<h1 id="aggregation-cursors">Aggregation Cursors</h1>
<p>Starting with MongoDB 2.5.1, you can stream results from the aggregation framework instead of getting them in one batch. This finally lifts the infamous 16MB limit on aggregation results and brings the aggregation framework closer to the standard <code>find</code> operation. In PyMongo 2.6 we added support for this server feature.</p>
<p>The old style gets all the documents at once:</p>

{{<highlight python3>}}
>>> collection.aggregate(pipeline)
{
    'ok': 1.0,
    'result': [
        {'key': 'value1'},
        {'key': 'value2'}
    ]
}
{{< / highlight >}}

<p>But now you can iterate through the results and there's no limit on the number of them:</p>

{{<highlight python3>}}
>>> for doc in collection.aggregate(pipeline, cursor={}):
...     print doc
{'key': 'value1'}
{'key': 'value2'}
{{< / highlight >}}

<h1 id="exhaust-cursors">Exhaust Cursors</h1>
<p>On the subject of cursors, MongoDB has long had "exhaust cursors": instead of waiting for the client to ask for each batch of results from a query, an exhaust cursor streams batches to the client as fast as possible. This supercharged cursor is used internally for replication and database dumps. Bernie <a href="https://jira.mongodb.org/browse/PYTHON-265">added support for exhaust cursors in PyMongo</a> so you can now take advantage of them, too, for Python tools that need to pull huge data sets from MongoDB over a high-latency network.</p>
<h1 id="get_default_database"><code>get_default_database</code></h1>
<p>A single MongoDB server can have multiple databases, but there's no standard way to use a config file to tell your app which database to use. You can put the database's name in a MongoDB URI like 'mongodb://host:port/my_database', but when you pass the URI to <code>MongoClient</code> you just get a connection to the whole server. There's been no way to say, "Give me a connection to only the database I specified in the URI." I added <code>get_default_database</code> method, so now you can do:</p>

{{<highlight python3>}}
uri = 'mongodb://host/my_database'
client = MongoClient(uri)
db = client.get_default_database()
{{< / highlight >}}

<p><code>db</code> is a reference the database you specified in the URI. This makes your application more customizable with the URI alone, which should make life easier for developers and operations folk.</p>
<h1 id="other">Other</h1>
<p>You can see all <a href="https://jira.mongodb.org/secure/IssueNavigator.jspa?requestId=13849">22 issues resolved in this release</a> in our bug tracker. There was also a very interesting <a href="https://github.com/mongodb/mongo-python-driver/pull/188">bugfix from a GitHub contributor to our Gevent compatibility</a>. Upgrade, check your <code>max_pool_size</code>, and enjoy!</p>
