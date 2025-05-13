+++
type = "post"
title = "Waiting For Multiple Events With Tornado"
date = "2014-03-11T09:16:42"
description = "How do you start multiple I/O operations with Tornado, and process results in the order they complete?"
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
draft = false
+++

<p>Recently I saw a question on Stack Overflow about waiting for multiple events with a Tornado coroutine, until <em>one</em> of the events completes. The inquirer wanted to do something like this:</p>

{{<highlight python3>}}
result = yield Any([future1, future2, future3])
{{< / highlight >}}

<p>If the middle future has resolved and the other two are still pending, the result should be like:</p>

{{<highlight python3>}}
[None, "<some result>", None]
{{< / highlight >}}

<p>Tornado doesn't provide a class like Any. How would you implement one?</p>
<p><strong>Contents:</strong></p>
<div class="toc">
<ul>
<li><a href="#a-bad-beginning">A Bad Beginning</a></li>
<li><a href="#a-better-way">A Better Way</a></li>
<li><a href="#exceptions">Exceptions</a></li>
<li><a href="#conclusion">Conclusion</a></li>
</ul>
</div>
<h1 id="a-bad-beginning">A Bad Beginning</h1>
<p>You could make a class that inherits from Future, and wraps a list of futures. The class waits until one of its futures resolves, then gives you the list of results:</p>

{{<highlight python3>}}
class Any(Future):
    def __init__(self, futures):
        super(Any, self).__init__()
        self.futures = futures
        for future in futures:
            # done_callback is defined just below.
            future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        """Called when any future resolves."""
        try:
            self.set_result(self.make_result())
        except Exception as e:
            self.set_exception(e)

    def make_result(self):
        """A list of results.

        Includes None for each pending future, and a result for each
        resolved future. Raises an exception for the first future
        that has an exception.
        """
        return [f.result() if f.done() else None
                for f in self.futures]

    def clear(self):
        """Break reference cycle with any pending futures."""
        self.futures = None
{{< / highlight >}}

<p>Here's an example use of Any:</p>

{{<highlight python3>}}
@gen.coroutine
def delayed_msg(seconds, msg):
    yield gen.Task(IOLoop.current().add_timeout,
                   time.time() + seconds)
    raise gen.Return(msg)


@gen.coroutine
def f():
    start = time.time()
    future1 = delayed_msg(2, '2')
    future2 = delayed_msg(3, '3')
    future3 = delayed_msg(1, '1')

    # future3 will resolve first.
    results = yield Any([future1, future2, future3])
    end = time.time()
    print "finished in %.1f sec: %r" % (end - start, results)

    # Wait for any of the remaining futures.
    results = yield Any([future1, future2])
    end = time.time()
    print "finished in %.1f sec: %r" % (end - start, results)

IOLoop.current().run_sync(f)
{{< / highlight >}}

<p>As expected, this prints:</p>

{{<highlight plain>}}
finished in 1.0 sec: [None, None, '1']
finished in 2.0 sec: ['2', None]
{{< / highlight >}}

<p>But you can see there are some complications with this approach. For one thing, if you want to wait for the <em>rest</em> of the futures after the first one resolves, it's complicated to construct the list of still-pending futures. I suppose you could do:</p>

{{<highlight python3>}}
futures = [future1, future2, future3]
results = yield Any(f for f in futures
                    if not f.done())
{{< / highlight >}}

<p>Not pretty. And not correct, either! There's a race condition: if a future is resolved in between consecutive executions of this code, you may never receive its result. On the first call, you get the result of some other future that resolves faster, but by the time you're constructing the list to pass to the second Any, your future is now "done" and you omit it from the list.</p>
<p>Another complication is the reference cycle: Any refers to each future, which refers to a callback which refers back to Any. For prompt garbage collection, you should call <code>clear()</code> on Any before it goes out of scope. This is very awkward.</p>
<p>Additionally, you can't distinguish between a pending future, and a future that resolved to None. You'd need a special sentinel value distinct from None to represent a pending future.</p>
<p>The final complication is the worst. If multiple futures are resolved and some of them have exceptions, there's no obvious way for Any to communicate all that information to you. Mixing exceptions and results in a list would be perverse.</p>
<h1 id="a-better-way">A Better Way</h1>
<p>Fortunately, there's a better way. We can make Any return just the first future that resolves, instead of a list of results:</p>

{{<highlight python3>}}
class Any(Future):
    def __init__(self, futures):
        super(Any, self).__init__()
        for future in futures:
            future.add_done_callback(self.done_callback)

    def done_callback(self, future):
        self.set_result(future)
{{< / highlight >}}

<p>The reference cycle is gone, and the exception-handling question is answered: The Any class returns the whole future to you, instead of its result or exception. You can inspect it as you like.</p>
<p>It's also easy to wait for the remaining futures after some are resolved:</p>

{{<highlight python3>}}
@gen.coroutine
def f():
    start = time.time()
    future1 = delayed_msg(2, '2')
    future2 = delayed_msg(3, '3')
    future3 = delayed_msg(1, '1')

    futures = set([future1, future2, future3])
    while futures:
        resolved = yield Any(futures)
        end = time.time()
        print "finished in %.1f sec: %r" % (
            end - start, resolved.result())
        futures.remove(resolved)
{{< / highlight >}}

<p>As desired, this prints:</p>

{{<highlight plain>}}
finished in 1.0 sec: '1'
finished in 2.0 sec: '2'
finished in 3.0 sec: '3'
{{< / highlight >}}

<p>There's no race condition now. You can't miss a result, because you don't remove a future from the list unless you've received its result.</p>
<h1 id="exceptions">Exceptions</h1>
<p>To test the exception-handling behavior, let's make a function that raises an exception after a delay:</p>

{{<highlight python3>}}
@gen.coroutine
def delayed_exception(seconds, msg):
    yield gen.Task(IOLoop.current().add_timeout,
                   time.time() + seconds)
    raise Exception(msg)
{{< / highlight >}}

<p>Now, instead of returning a result, one of our futures will raise an exception:</p>

{{<highlight python3>}}
@gen.coroutine
def f():
    start = time.time()
    future1 = delayed_msg(2, '2')
    # Exception!
    future2 = delayed_exception(3, '3')
    future3 = delayed_msg(1, '1')

    futures = set([future1, future2, future3])
    while futures:
        resolved = yield Any(futures)
        end = time.time()
        try:
            outcome = resolved.result()
        except Exception as e:
            outcome = e

        print "finished in %.1f sec: %r" % (
            end - start, outcome)
        futures.remove(resolved)
{{< / highlight >}}

<p>Now, the script prints:</p>

{{<highlight plain>}}
finished in 1.0 sec: '1'
finished in 2.0 sec: '2'
finished in 3.0 sec: Exception('3',)
{{< / highlight >}}

<h1 id="conclusion">Conclusion</h1>
<p>It took a bit of thinking, but our final Any class is simple. It lets you launch many concurrent operations and process them in the order they complete. Not bad.</p>
