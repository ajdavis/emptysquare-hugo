+++
category = ['Motor', 'Programming', 'Python', 'MongoDB']
date = '2017-02-04T15:13:45.586344'
description = "Motor 1.0 added a monitoring feature so you can log what it does. Here's how to use the feature."
draft = false
enable_lightbox = false
tag = []
thumbnail = 'monitor-lizard.png'
title = 'Monitoring MongoDB Driver Events In Motor'
type = 'post'
+++

![Image description: line drawing of a monitor lizard](monitor-lizard.png)

Do you want to know every MongoDB query or command your program sends, and the server's reply to each? How about getting a notification whenever the driver detects a primary failover, or when a new secondary joins the replica set? Over the last year, MongoDB drivers have implemented these monitoring features in all our supported programming languages. Here's how to use monitoring in Motor, my Python async driver.

Motor wraps PyMongo, and it shares PyMongo's API for monitoring. To receive notifications about events, you subclass one of PyMongo's four listener classes, ``CommandListener``, ``ServerListener``, ``TopologyListener``, or ``ServerHeartbeatListener``. Let's subclass CommandListener, so we're notified whenever a command starts, succeeds, or fails.

```py3
import logging
from pymongo import monitoring

class MyCommandLogger(monitoring.CommandListener):
    def started(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} started on server "
                     "{0.connection_id}".format(event))

    def succeeded(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "succeeded in {0.duration_micros} "
                     "microseconds".format(event))

    def failed(self, event):
        logging.info("Command {0.command_name} with request id "
                     "{0.request_id} on server {0.connection_id} "
                     "failed in {0.duration_micros} "
                     "microseconds".format(event))
```

Register an instance of ``MyCommandLogger``:

```py3
monitoring.register(MyCommandLogger())
```

You can register any number of listeners, of any of the four listener types.

We only need to use PyMongo's API here, but if you create a ``MotorClient`` its commands are monitored, the same as a PyMongo ``MongoClient``.

```py3
import sys
from tornado import ioloop, options, gen
from motor import MotorClient

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

client = MotorClient()

async def do_insert():
    await client.test.collection.insert({'_id': 1, 'message': 'hi!'})

ioloop.IOLoop.current().run_sync(do_insert)
```

This logs something like:

```text
Command insert with request id 50073 started on server ('localhost', 27017)
Command insert with request id 50073 on server ('localhost', 27017) 
  succeeded in 362 microseconds
```

Watch out: Your listeners' callbacks are executed on various background threads, *not* the main thread. If you want to interact with Tornado or Motor from a listener callback, you must defer to the main thread using [``IOLoop.add_callback``](http://www.tornadoweb.org/en/latest/ioloop.html#tornado.ioloop.IOLoop.add_callback), which is the only thread-safe IOLoop method. Similarly, if you're using asyncio instead of Tornado, get to the main loop with [``call_soon_threadsafe``](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.AbstractEventLoop.call_soon_threadsafe). I can't think of a need for you to do this, though&mdash;it seems like logging is the only reasonable thing to do from a listener, and [the Python logging module is thread-safe](https://docs.python.org/3/library/logging.html#thread-safety).

For more info, see:

* [A complete example with Motor](https://gist.github.com/ajdavis/86e1cb6dfcbf8b29fb44362cf48021cd)
* [PyMongo's monitoring API](http://api.mongodb.com/python/current/api/pymongo/monitoring.html)
* [The Command Monitoring Spec for all MongoDB Drivers](https://github.com/mongodb/specifications/blob/master/source/command-monitoring/command-monitoring.rst)
* [The Topology Monitoring Spec for all MongoDB Drivers](https://github.com/mongodb/specifications/blob/master/source/server-discovery-and-monitoring/server-discovery-and-monitoring-monitoring.rst)

That was simple, so we have time for a picture of a monitor lizard and a log:

![Image Description: color photograph of a monitor lizard basking on a log](varanus-bengalensis.jpg)

***

Images:

* [Monitor lizard, Pearson Scott Foresman](https://commons.wikimedia.org/wiki/File:Monitor_Lizard_(PSF).png)
* [Wild Bengal monitor, Carlos Delgado 2014](https://commons.wikimedia.org/wiki/File:Varanus_bengalensis_-_02.jpg)
