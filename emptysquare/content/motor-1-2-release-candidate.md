+++
category = ['MongoDB', 'Motor', 'Programming', 'Python']
date = '2017-12-13T07:01:32.459430'
description = 'Adds change streams, causal consistency, retryable writes, and more. Drops Python 2.6, MongoDB 2.4, and Tornado 3.'
draft = false
enable_lightbox = false
tag = []
thumbnail = 'motor-musho.png'
title = 'Announcing Motor 1.2 Release Candidate, With MongoDB 3.6 Support'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" border="0" /></p>

[MongoDB 3.6 was released December 5](https://groups.google.com/d/msg/mongodb-announce/IDlWs6RTnm8/odRj2_ENAAAJ). Today I've uploaded a release candidate for version 1.2 of Motor, the async Python driver for MongoDB. This will be a big release so I hope you try the release candidate and [tell me if it works for you or if you find bugs](https://twitter.com/jessejiryudavis).

Install the release candidate with pip:

```text
python -m pip install motor==1.2rc0
```

# Compatibility Changes

- MongoDB: drop 2.4, add 3.6
- Python: drop 2.6, continue to support 2.7 and 3.3+
- Tornado: drop 3, continue to support Tornado 4.5+
- [aiohttp](https://aiohttp.readthedocs.io/): support 2.0 and later, drop older version

See the [Compatibility Matrix](http://motor.readthedocs.io/en/latest/requirements.html) for the relationships
among Motor, Python, Tornado, and MongoDB versions.

# MongoDB 3.6 Features

## Change Streams

There's a new method [MotorCollection.watch](http://motor.readthedocs.io/en/latest/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.watch) to acquire a Change Stream on a
collection:

```py3
async for change in collection.watch():
    print(change)
```

I've written you a little sample app that watches a collection for changes and posts each notification over a websocket using the Tornado webserver:

<div style="text-align: center">
<p>
<a href="http://motor.readthedocs.io/en/latest/examples/tornado_change_stream_example.html">Tornado Change Stream Example</a>
</p>
</div>

## Causal Consistency

There's a new Session API to support [causal consistency](https://docs.mongodb.com/manual/core/read-isolation-consistency-recency/#causal-consistency), meaning you can read your writes and perform monotonic reads, even reading from secondaries in a replica set or a sharded cluster. Create a session with [MotorClient.start_session](http://motor.readthedocs.io/en/latest/api-tornado/motor_client.html#motor.motor_tornado.MotorClient.start_session) and use it for a sequence of related operations:

```py3
collection = client.db.collection

with (await client.start_session()) as s:
    doc = {'_id': ObjectId(), 'x': 1}
    await collection.insert_one(doc, session=s)

    secondary = collection.with_options(
        read_preference=ReadPreference.SECONDARY)

    # Sessions are causally consistent by default, we can read the doc
    # we just inserted, even reading from a secondary.
    async for doc in secondary.find(session=s):
        print(doc)
```

## Array Filters

You can now update subdocuments in arrays within documents, and use "array filters" to choose which subdocuments to change. Pass the ``array_filters`` argument to
[MotorCollection.update_one](http://motor.readthedocs.io/en/latest/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.update_one),
[MotorCollection.update_many](http://motor.readthedocs.io/en/latest/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.update_many),
[MotorCollection.find_one_and_update](http://motor.readthedocs.io/en/latest/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.find_one_and_update),
or [MotorCollection.bulk_write](http://motor.readthedocs.io/en/latest/api-tornado/motor_collection.html#motor.motor_tornado.MotorCollection.bulk_write).

For example if your document looks like this:

```javascript
{
    _id: 1,
    points: [
        {x: 0, y: 0},
        {x: 1, y: 0},
        {x: 2, y: 0}
    ]
}
```

You can update all subdocuments where x is greater than zero:

```py3
await collection.update_one(
    {'_id': 1},
    {'$set': {'points.$[i].y': 5}},
    array_filters=[{'i.x': {'$gt': 0}}])
```

## "mongodb+srv://" URIs

This new URI scheme is convenient for short, maintainable URIs that represent large clusters, especially in [Atlas](https://www.mongodb.com/cloud/atlas). See PyMongo's [MongoClient](http://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) for details.

## Retryable Writes

Now, with a MongoDB 3.6 replica set or sharded cluster, Motor will safely retry any write that's interrupted by a network glitch or a primary failover, without any risk of a double write. Just add ``retryWrites`` to the URI:

```text
mongodb://host1,host2,host3/?replicaSet=rs&retryWrites=true
```

See PyMongo's [MongoClient](http://api.mongodb.com/python/current/api/pymongo/mongo_client.html#pymongo.mongo_client.MongoClient) for details about retryable writes.

Thanks to everyone who contributed to this version:

- A. Jesse Jiryu Davis
- Bernie Hackett
- Jakub Wilk
- Karol Horowski

Peace,<br>
A. Jesse Jiryu Davis

***

<a href="https://www.flickr.com/photos/emptysquare/26615253806/"><img src="26615253806_ed4f855c04_k.jpg"></a>
