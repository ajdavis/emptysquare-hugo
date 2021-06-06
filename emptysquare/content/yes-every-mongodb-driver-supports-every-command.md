+++
type = "post"
title = "Yes, Every MongoDB Driver Supports Every Command"
date = "2012-12-17T17:29:54"
description = ""
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "50cf9b1c5393745f960f20d0"
disqus_url = "https://emptysqua.re/blog/50cf9b1c5393745f960f20d0/"
+++

<p>This post is in response to a persistent form of question I receive about MongoDB drivers: "Does driver X support feature Y?" The answer is nearly always "yes," but you can't know that unless you understand MongoDB commands.</p>
<p>There are only four kinds of operations a MongoDB driver can perform on the server: insert, update, remove, query, and commands.</p>
<p>Almost two years ago my colleague Kristina wrote about "<a href="http://www.kchodorow.com/blog/2011/01/25/why-command-helpers-suck/">Why Command Helpers Suck</a>," and she is still right: if you only use the convenience methods without understanding the unifying concept of a "command," you're unnecessarily tied to a particular driver's API, and you don't know how MongoDB really works.</p>
<p>So let's do a pop quiz:</p>
<ol>
<li>Which MongoDB drivers support the Aggregation Framework?</li>
<li>Which support the "group" operation?</li>
<li>Which drivers are compatible with MongoDB's mapreduce feature?</li>
<li>Which drivers let you run "count" or "distinct" on a collection?</li>
</ol>
<p>If you answered, "all of them," you're right—every driver supports commands, and all the features I asked about are commands.</p>
<p>Let's consider three MongoDB drivers for Python and show examples of using the <code>distinct</code> command in each.</p>
<h1 id="pymongo">PyMongo</h1>
<p>PyMongo has two convenience methods for <code>distinct</code>. One is on the <code>Collection</code> class, the other on <code>Cursor</code>:</p>

{{<highlight python3>}}
>>> from pymongo import MongoClient
>>> db = MongoClient().test
>>> db.test_collection.distinct('my_key')
[1.0, 2.0, 3.0]
>>> db.test_collection.find().distinct('my_key')
[1.0, 2.0, 3.0]
{{< / highlight >}}

<p>But this all boils down to the same MongoDB command. We can look up its arguments in the <a href="http://docs.mongodb.org/manual/reference/commands/">MongoDB Command Reference</a> and see that <a href="http://docs.mongodb.org/manual/reference/commands/#distinct">distinct</a> takes the form:</p>

{{<highlight plain>}}
{ distinct: collection, key: <field>, query: <query> }
{{< / highlight >}}

<p>So let's use PyMongo's generic <code>command</code> method to run <code>distinct</code> directly. We'll pass the <code>collection</code> and <code>key</code> arguments and omit <code>query</code>. We need to use PyMongo's <code>SON</code> class to ensure we pass the arguments in the right order:</p>

{{<highlight python3>}}
>>> from bson import SON
>>> db.command(SON([('distinct', 'test_collection'), ('key', 'my_key')]))
{u'ok': 1.0,
 u'stats': {u'cursor': u'BasicCursor',
            u'n': 3,
            u'nscanned': 3,
            u'nscannedObjects': 3,
            u'timems': 0},
 u'values': [1.0, 2.0, 3.0]}
{{< / highlight >}}

<p>The answer is in <code>values</code>.</p>
<h1 id="motor">Motor</h1>
<p>My async driver for Tornado and MongoDB, called <a href="/motor/">Motor</a>, supports a similar conveniences for <code>distinct</code>. It has both the <code>MotorCollection.distinct</code> method:</p>

{{<highlight python3>}}
>>> from tornado.ioloop import IOLoop
>>> from tornado import gen
>>> import motor
>>> from motor import MotorConnection
>>> db = MotorConnection().open_sync().test
>>> @gen.engine
... def f():
...     print (yield motor.Op(db.test_collection.distinct, 'my_key'))
...     IOLoop.instance().stop()
... 
>>> f()
>>> IOLoop.instance().start()
[1.0, 2.0, 3.0]
{{< / highlight >}}

<p>... and <code>MotorCursor.distinct</code>:</p>

{{<highlight python3>}}
>>> @gen.engine
... def f():
...     print (yield motor.Op(db.test_collection.find().distinct, 'my_key'))
...     IOLoop.instance().stop()
... 
>>> f()
>>> IOLoop.instance().start()
[1.0, 2.0, 3.0]
{{< / highlight >}}

<p>Again, these are just convenient alternatives to using <code>MotorDatabase.command</code>:</p>

{{<highlight python3>}}
>>> @gen.engine
... def f():
...     print (yield motor.Op(db.command,
...         SON([('distinct', 'test_collection'), ('key', 'my_key')])))
...     IOLoop.instance().stop()
... 
>>> f()
>>> IOLoop.instance().start()
{u'ok': 1.0,
 u'stats': {u'cursor': u'BasicCursor',
            u'n': 3,
            u'nscanned': 3,
            u'nscannedObjects': 3,
            u'timems': 0},
 u'values': [1.0, 2.0, 3.0]}
{{< / highlight >}}

<h1 id="asyncmongo">AsyncMongo</h1>
<p>AsyncMongo is another driver for Tornado and MongoDB. Its interface isn't nearly so rich as Motor's, so I often hear questions like, "Does AsyncMongo support <code>distinct</code>? Does it support <code>aggregate</code>? What about <code>group</code>?" In fact, it's those questions that prompted this post. And of course the answer is yes, AsyncMongo supports all commands:</p>

{{<highlight python3>}}
>>> from tornado.ioloop import IOLoop
>>> import asyncmongo
>>> db = asyncmongo.Client(
...     pool_id='mydb', host='127.0.0.1', port=27017,
...     maxcached=10, maxconnections=50, dbname='test')
>>> @gen.engine
... def f():
...     results = yield gen.Task(db.command,
...         SON([('distinct', 'test_collection'), ('key', 'my_key')]))
...     print results.args[0]
...     IOLoop.instance().stop()
... 
>>> f()
>>> IOLoop.instance().start()
{u'ok': 1.0,
 u'stats': {u'cursor': u'BasicCursor',
            u'n': 3,
            u'nscanned': 3,
            u'nscannedObjects': 3,
            u'timems': 0},
 u'values': [1.0, 2.0, 3.0]}
{{< / highlight >}}

<h1 id="exceptions">Exceptions</h1>
<p>There are some areas where drivers really differ, like <a href="http://docs.mongodb.org/manual/replication/">Replica Set</a> support, or <a href="/reading-from-mongodb-replica-sets-with-pymongo/">Read Preferences</a>. 10gen's drivers are much more consistent than third-party drivers. But if the underlying operation is a command, then all drivers are essentially the same.</p>
<h1 id="so-go-learn-how-to-run-commands">So Go Learn How To Run Commands</h1>
<p>So the next time you're about to ask, "Does driver X support feature Y," first check if Y is a command by looking for it in the <a href="http://docs.mongodb.org/manual/reference/commands/">command reference</a>. Chances are it's there, and if so, you know how to run it.</p>
