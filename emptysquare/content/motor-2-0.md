+++
category = ['Mongo', 'Motor', 'Programming', 'Python']
date = '2018-07-11T04:11:37.130529'
description = 'Add multi-document transactions, delete a bunch of old methods and drop MongoDB 2.6'
draft = false
enable_lightbox = false
tag = []
thumbnail = 'motor-musho.png'
title = 'Motor 2.0'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" border="0" /></p>

To support multi-document transactions, I had to make breaking changes to Motor's session API and release a major version bump, Motor 2.0. Since this is a major release I also deleted many helper methods and APIs that had been deprecated over time since Motor 1.0, most notably the old CRUD methods ``insert``, ``update``, ``remove``, and ``save``, and the original callback-based API. Read the [Motor 2.0 Migration Guide](http://motor.readthedocs.io/en/stable/migrate-to-motor-2.html) carefully to upgrade your existing Motor application. Motor 2.0 also includes a Python 3.7 compatibility fix in the [MotorChangeStream](http://motor.readthedocs.io/en/stable/api-tornado/motor_change_stream.html) class returned by [MotorCollection.watch](http://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.watch).

Motor 2.0's changes have a big impact for some applications, so I created a bridge release that raises DeprecationWarning for all the APIs that are deleted in Motor 2.0, especially the callback API, which hasn't been deprecated before. Those DeprecationWarnings plus the Python 3.7 compatibility fix constitute Motor 1.3.0.

For applications that only need Python 3.7 compatibility, I've created Motor 1.2.4, which includes the Python 3.7 fix and no other changes.

Detailed release notes follow.

Motor 2.0
---------

Motor 2.0 drops support for MongoDB 2.6 and adds supports MongoDB 4.0 features, including multi-document transactions, and change stream notifications on entire databases or entire MongoDB servers. This version of Motor requires PyMongo 3.7 or later.

Added support for [aiohttp](https://aiohttp.readthedocs.io/) 3.0 and later, and dropped older aiohttp versions. The aiohttp integration now requires Python 3.5+.

This is a major release that removes previously deprecated APIs.

The MotorDatabase.add_user and MotorDatabase.remove_user methods are deleted. Manage user accounts with four database commands: [createUser](https://docs.mongodb.com/manual/reference/command/createUser/), [usersInfo](https://docs.mongodb.com/manual/reference/command/usersInfo/), [updateUser](https://docs.mongodb.com/manual/reference/command/updateUser/), and [dropUser](https://docs.mongodb.com/manual/reference/command/createUser/). You can run any database command with the [MotorDatabase.command()](http://motor.readthedocs.io/en/stable/api-tornado/motor_database.html#motor.motor_tornado.MotorDatabase.command "motor.motor_tornado.MotorDatabase.command") method.

The deprecated GridFS classes MotorGridFS and AsyncIOMotorGridFS are deleted in favor of [MotorGridFSBucket](http://motor.readthedocs.io/en/stable/api-tornado/gridfs.html#motor.motor_tornado.MotorGridFSBucket "motor.motor_tornado.MotorGridFSBucket") and [AsyncIOMotorGridFSBucket](http://motor.readthedocs.io/en/stable/api-asyncio/asyncio_gridfs.html#motor.motor_asyncio.AsyncIOMotorGridFSBucket "motor.motor_asyncio.AsyncIOMotorGridFSBucket"), which conform to driver specs for GridFS.

Additional changes:

-   New methods for retrieving batches of raw BSON:
    -   [MotorCollection.find_raw_batches()](http://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.find_raw_batches "motor.motor_tornado.MotorCollection.find_raw_batches")
    -   [MotorCollection.aggregate_raw_batches()](http://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.aggregate_raw_batches "motor.motor_tornado.MotorCollection.aggregate_raw_batches")
-   Motor adds its name, version, and Tornado's version (if appropriate) to the client data logged by the MongoDB server when Motor connects, in addition to the data added by PyMongo.
-   Calling batch_size() on a cursor returned from [aggregate()](http://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.aggregate "motor.motor_tornado.MotorCollection.aggregate") no longer raises AttributeError.

Motor 1.3.0
-----------

Deprecate Motor's old callback-based async API in preparation for removing it in Motor 2.0. Raise DeprecationWarning whenever a callback is passed.

Motor 1.2.4
-----------

Fix a Python 3.7 compatibility bug in the [MotorChangeStream](http://motor.readthedocs.io/en/stable/api-tornado/motor_change_stream.html#motor.motor_tornado.MotorChangeStream "motor.motor_tornado.MotorChangeStream") class returned by [MotorCollection.watch()](http://motor.readthedocs.io/en/stable/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.watch "motor.motor_tornado.MotorCollection.watch"). It is now possible to use change streams in async for loops in Python 3.7.

***

<a href="https://jira.mongodb.org/browse/MOTOR/">If you find issues, file a bug and I'll respond promptly.</a> But if it works for you, don't be silent!&mdash;<a href="https://twitter.com/jessejiryudavis">tweet at me</a> and tell me.
