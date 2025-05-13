+++
type = "post"
title = "Tornado Locks And Queues (The End Of Toro)"
date = "2015-05-28T11:46:28"
description = "I merged Toro, my library for coordinating asynchronous coroutines, into Tornado 4.2."
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "toro.png"
draft = false
+++

<p><img alt="Toro" border="0" src="toro.png" style="display:block; margin-left:auto; margin-right:auto;" title="toro.png"/></p>
<p>On Tuesday, Ben Darnell released Tornado 4.2, with two new modules: <a href="http://www.tornadoweb.org/en/stable/locks.html">tornado.locks</a> and <a href="http://www.tornadoweb.org/en/stable/queues.html">tornado.queues</a>. These new modules help you coordinate Tornado's asynchronous coroutines with patterns familiar from multi-threaded programming.</p>
<p>I originally developed these features in my <a href="https://toro.readthedocs.org/">Toro</a> package, which I began almost three years ago, and I'm honored that Ben has adopted my code into Tornado's core. It's a bit sad, though, because this is the end of the line for Toro, one of the best ideas of my career. Skip to the bottom for my thoughts on Toro's retirement.</p>
<p>The classes Condition and Queue are representative of Tornado's new features. Here's how one coroutine signals another, using a Condition:</p>

{{<highlight python3>}}
condition = locks.Condition()

@gen.coroutine
def waiter():
    print("I'll wait right here")
    yield condition.wait()  # Yield a Future.
    print("I'm done waiting")

@gen.coroutine
def notifier():
    print("About to notify")
    condition.notify()
    print("Done notifying")

@gen.coroutine
def runner():
    # Yield two Futures; wait for waiter() and notifier() to finish.
    yield [waiter(), notifier()]

io_loop.run_sync(runner)
{{< / highlight >}}

<p>This script prints:</p>

{{<highlight plain>}}
I'll wait right here
About to notify
Done notifying
I'm done waiting
{{< / highlight >}}

<p>As you can see, the Condition interface is close to the Python standard library's Condition. But instead of coordinating threads, Tornado's Condition coordinates asynchronous coroutines.</p>
<p>Tornado's Queue is similarly analogous to the standard Queue:</p>

{{<highlight python3>}}
q = queues.Queue(maxsize=2)

@gen.coroutine
def consumer():
    while True:
        item = yield q.get()
        try:
            print('Doing work on %s' % item)
            yield gen.sleep(0.01)
        finally:
            q.task_done()

@gen.coroutine
def producer():
    for item in range(5):
        yield q.put(item)
        print('Put %s' % item)

@gen.coroutine
def main():
    consumer()           # Start consumer.
    yield producer()     # Wait for producer to put all tasks.
    yield q.join()       # Wait for consumer to finish all tasks.
    print('Done')

io_loop.run_sync(main)
{{< / highlight >}}

<p>This will print:</p>

{{<highlight plain>}}
Put 0
Put 1
Put 2
Doing work on 0
Doing work on 1
Put 3
Doing work on 2
Put 4
Doing work on 3
Doing work on 4
Done
{{< / highlight >}}

<p>Tornado's new locks and queues implement the same familiar patterns we've used for decades to coordinate threads. There's no need to invent these techniques anew for coroutines.</p>
<p>I was inspired to write these classes in 2012, when I was deep in the initial implementation of <a href="https://motor.readthedocs.org/">Motor</a>, my MongoDB driver for Tornado. The time I spent learning about coroutines for Motor's sake provoked me to wonder, how far could I push them? How much of the threading API was applicable to coroutines? The outcome was Toro—not necessarily evidence of my genius, but a very good idea that led me far. Toro's scope was straightforward, and I had to make very few decisions. The initial implementation took a week or two. I commissioned the cute bull character from <a href="http://whimsyload.com/">Musho Rodney Alan Greenblat</a>. The cuteness of Musho's art matched the simplicity of Toro's purpose.</p>
<p>When I heard about Guido van Rossum's Tulip project at his PyCon talk in 2013, I thought he could use Toro's locks and queues. It would be an excuse for me to work with Guido. I found that Tulip already had locks, implemented by Nikolay Kim if I remember right, but it didn't have queues yet so I jumped in and contributed mine. It was a chance to be code-reviewed by Guido and other Python core developers. In the long run, when Tulip became the <code>asyncio</code> standard library module, <a href="https://docs.python.org/3.4/library/asyncio-queue.html">my queues</a> became my first big contribution to the Python standard library.</p>
<p>Toro has led me to collaborate with Guido van Rossum and Ben Darnell, two of the coders I admire most. And now Toro's life is over. Its code is split up and merged into much larger and better-known projects. The name "Toro" and the character are relics. When I find the time I'll post the deprecation notice and direct people to use the locks and queues in Tornado core. Toro was the most productive idea of my career. Now I'm waiting for the next one.</p>
