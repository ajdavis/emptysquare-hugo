+++
type = "post"
title = "Toro: synchronization primitives for Tornado coroutines"
date = "2012-11-18T15:17:49"
description = "I took a break from Motor to make a new package \"Toro\": queues, semaphores, locks, and so on for Tornado coroutines. (The name \"Toro\" is from \"Tornado\" and \"Coro\".) Why would you need something like this, especially since Tornado apps are [ ... ]"
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "toro.png"
draft = false
+++

<p><img alt="Toro" border="0" src="toro.png" style="display:block; margin-left:auto; margin-right:auto;" title="toro.png"/></p>
<p>I took a break from <a href=https://motor.readthedocs.io/>Motor</a> to make a new package "Toro": queues, semaphores, locks, and so on for Tornado coroutines. (The name "Toro" is from "Tornado" and "Coro".)</p>
<p>Why would you need something like this, especially since Tornado apps are usually single-threaded? Well, with Tornado's <a href="http://www.tornadoweb.org/en/latest/gen.html">gen</a> module you can turn Python generators into full-featured coroutines, but coordination among these coroutines is difficult. If one coroutine wants exclusive access to a resource, how can it notify other coroutines to proceed once it's finished? How do you allow N coroutines, but no more than N, access a resource at once? How do you start a set of coroutines and end your program when the last completes?</p>
<p>Each of these problems can be solved individually, but Toro's classes generalize the solutions. Toro provides to Tornado coroutines a set of locking primitives and queues analogous to those that Gevent provides to Greenlets, or that the standard library provides to threads.</p>
<p>Here's a producer-consumer example with a <code>toro.Queue</code>:</p>

{{<highlight python3>}}
from tornado import ioloop, gen
import toro

q = toro.JoinableQueue(maxsize=3)

@gen.engine
def consumer():
    while True:
        item = yield gen.Task(q.get)
        try:
            print 'Doing work on', item
        finally:
            q.task_done()

@gen.engine
def producer():
    for item in range(10):
        yield gen.Task(q.put, item)

if __name__ == '__main__':
    producer()
    consumer()
    loop = ioloop.IOLoop.instance()
    q.join(callback=loop.stop) # block until all tasks are done
    loop.start()
{{< / highlight >}}

<p>More <a href="http://toro.readthedocs.org/en/latest/examples/index.html">examples are in the docs</a>: graceful shutdown using Toro's <code>Lock</code>, a caching proxy server with <code>Event</code>, and a web spider with <code>Queue</code>. Further reading:</p>
<p><a href="http://toro.readthedocs.org/">Toro on Read the Docs</a></p>
<p><a href="https://github.com/ajdavis/toro">Toro on Github</a></p>
<p><a href="http://pypi.python.org/pypi/toro/">Toro on PyPI</a></p>
<p><em>Toro logo by <a href="http://whimsyload.com/">Musho Rodney Alan Greenblat</a></em></p>
