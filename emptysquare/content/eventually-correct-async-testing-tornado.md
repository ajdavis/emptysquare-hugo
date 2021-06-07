+++
type = "post"
title = "Eventually Correct: Async Testing With Tornado"
date = "2015-04-10T22:03:32"
description = "Event-loop management, error handling, and coroutines as unittests."
category = ["Motor", "Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "toad-vs-birdo.jpg"
draft = false
disqus_identifier = "5526a9645393741c70651f95"
disqus_url = "https://emptysqua.re/blog/5526a9645393741c70651f95/"
+++

<p><img alt="Toad vs Birdo" src="toad-vs-birdo.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Toad vs Birdo"/></p>
<p>Async frameworks like Tornado scramble our usual unittest strategies: how can you validate the outcome when you do not know when to expect it? Tornado ships with a <code>tornado.testing</code> module that provides two solutions: the <code>wait</code> / <code>stop</code> pattern, and <code>gen_test</code>.</p>
<div class="toc">
<ul>
<li><a href="#wait-stop">Wait / Stop</a></li>
<li><a href="#gen_test">gen_test</a></li>
<li><a href="#further-study">Further Study</a></li>
</ul>
</div>
<h1 id="wait-stop">Wait / Stop</h1>
<p>To begin, let us say we are writing an async application with feature like Gmail's <a href="https://support.google.com/mail/answer/1284885?hl=en">undo send</a>: when I click "send", Gmail delays a few seconds before actually sending the email. It is a funny phenomenon, that during the seconds after clicking "sending" I experience a special clarity about my email. It was too angry, or I forgot an attachment, most often both. If I click the "undo" button in time, the email reverts to a draft and I can tone it down, add the attachment, and send it again.</p>
<p>To write an application with this feature, we will need an asynchronous "delay" function, and we must test it. If we were testing a normal blocking delay function we could use <code>unittest.TestCase</code> from the standard library:</p>

{{<highlight python3>}}
import time
import unittest

from my_application import delay


class MyTestCase(unittest.TestCase):
    def test_delay(self):
        start = time.time()
        delay(1)
        duration = time.time() - start
        self.assertAlmostEqual(duration, 1, places=2)
{{< / highlight >}}

<p>When we run this, it prints:</p>

{{<highlight plain>}}
Ran 1 test in 1.000s
OK
{{< / highlight >}}

<p>And if we replace <code>delay(1)</code> with <code>delay(2)</code> it fails as expected:</p>

{{<highlight plain>}}
=======================================================
FAIL: test_delay (delay0.MyTestCase)
------------------------------------------------------
Traceback (most recent call last):
File "delay0.py", line 12, in test_delay
    self.assertAlmostEqual(duration, 1, places=2)
AssertionError: 2.000854969024658 != 1 within 2 places

------------------------------------------------------
Ran 1 test in 2.002s
FAILED (failures=1)
{{< / highlight >}}

<p>Great! What about testing a <code>delay_async(seconds, callback)</code> function?</p>

{{<highlight python3>}}
def test_delay(self):
    start = time.time()
    delay_async(1, callback=)  # What goes here?
    duration = time.time() - start
    self.assertAlmostEqual(duration, 1, places=2)
{{< / highlight >}}

<p>An asynchronous "delay" function can't block the caller, so it must take a callback and execute it once the delay is over. (In fact we are just reimplementing Tornado's <a href="http://tornado.readthedocs.org/en/latest/ioloop.html#tornado.ioloop.IOLoop.call_later"><code>call_later</code></a>, but please pretend for pedagogy's sake this is a new function that we must test.) To test our <code>delay_async</code>, we will try a series of testing techniques until we have effectively built Tornado's test framework from scratch—you will see why we need special test tools for async code and how Tornado's tools work.</p>
<p>So, we define a function <code>done</code> to measure the delay, and pass it as the callback to <code>delay_async</code>:</p>

{{<highlight python3>}}
def test_delay(self):
    start = time.time()

    def done():
        duration = time.time() - start
        self.assertAlmostEqual(duration, 1, places=2)

    delay_async(1, done)
{{< / highlight >}}

<p>If we run this:</p>

{{<highlight plain>}}
Ran 1 test in 0.001s
OK
{{< / highlight >}}

<p>Success! ...right? But why does it only take a millisecond? And what happens if we delay by two seconds instead?</p>

{{<highlight python3>}}
def test_delay(self):
    start = time.time()

    def done():
        duration = time.time() - start
        self.assertAlmostEqual(duration, 1, places=2)

    delay_async(2, done)
{{< / highlight >}}

<p>Run it again:</p>

{{<highlight plain>}}
Ran 1 test in 0.001s
OK
{{< / highlight >}}

<p>Something is very wrong here. The test appears to pass instantly, regardless of the argument to <code>delay_async</code>, because we neither start the event loop nor wait for it to complete. We have to actually pause the test until the callback has executed:</p>

{{<highlight python3>}}
def test_delay(self):
    start = time.time()
    io_loop = IOLoop.instance()

    def done():
        duration = time.time() - start
        self.assertAlmostEqual(duration, 1, places=2)
        io_loop.stop()

    delay_async(1, done)
    io_loop.start()
{{< / highlight >}}

<p>Now if we run the test with a delay of one second:</p>

{{<highlight plain>}}
Ran 1 test in 1.002s
OK
{{< / highlight >}}

<p>That looks better. And if we delay for two seconds?</p>

{{<highlight plain>}}
ERROR:tornado.application:Exception in callback
Traceback (most recent call last):
  File "site-packages/tornado/ioloop.py", line 568, in _run_callback
    ret = callback()
  File "site-packages/tornado/stack_context.py", line 275, in null_wrapper
    return fn(*args, **kwargs)
  File "delay3.py", line 16, in done
    self.assertAlmostEqual(duration, 1, places=2)
  File "unittest/case.py", line 845, in assertAlmostEqual
    raise self.failureException(msg)
AssertionError: 2.001540184020996 != 1 within 2 places
{{< / highlight >}}

<p>The test appears to fail, as expected, but there are a few problems. First, notice that it is not the unittest that prints the traceback: it is Tornado's application logger. We do not get the unittest's characteristic output. Second, the process is now hung and remains so until I type Control-C. Why?</p>
<p>The bug is here:</p>

{{<highlight python3>}}
def done():
    duration = time.time() - start
    self.assertAlmostEqual(duration, 1, places=2)
    io_loop.stop()
{{< / highlight >}}

<p>Since the failed assertion raises an exception, we never reach the call to <code>io_loop.stop()</code>, so the loop continues running and the process does not exit. We need to register an exception handler. Exception handling with callbacks is convoluted; we have to use a <a href="http://www.tornadoweb.org/en/branch2.3/stack_context.html">stack context</a> to install a handler with Tornado:</p>

{{<highlight python3>}}
from tornado.stack_context import ExceptionStackContext

class MyTestCase(unittest.TestCase):
    def test_delay(self):
        start = time.time()
        io_loop = IOLoop.instance()

        def done():
            duration = time.time() - start
            self.assertAlmostEqual(duration, 1, places=2)
            io_loop.stop()

        self.failure = None

        def handle_exception(typ, value, tb):
            io_loop.stop()
            self.failure = value
            return True  # Stop propagation.

        with ExceptionStackContext(handle_exception):
            delay_async(2, callback=done)

        io_loop.start()
        if self.failure:
            raise self.failure
{{< / highlight >}}

<p>The loop can now be stopped two ways: if the test passes, then <code>done</code> stops the loop as before. If it fails, <code>handle_exception</code> stores the error and stops the loop. At the end, if an error was stored we re-raise it to make the test fail:</p>

{{<highlight plain>}}
=======================================================
FAIL: test_delay (delay4.MyTestCase)
------------------------------------------------------
Traceback (most recent call last):
  File "delay4.py", line 31, in test_delay
    raise self.failure
  File "tornado/ioloop.py", line 568, in _run_callback
    ret = callback()
  File "tornado/stack_context.py", line 343, in wrapped
    raise_exc_info(exc)
  File "<string>", line 3, in raise_exc_info
  File "tornado/stack_context.py", line 314, in wrapped
    ret = fn(*args, **kwargs)
  File "delay4.py", line 17, in done
    self.assertAlmostEqual(duration, 1, places=2)
AssertionError: 2.0015950202941895 != 1 within 2 places
------------------------------------------------------
Ran 1 test in 2.004s
FAILED (failures=1)
{{< / highlight >}}

<p>Now the test ends promptly, whether it succeeds or fails, with unittest's typical output.</p>
<p>This is a lot of tricky code to write just to test a trivial delay function, and it seems hard to get right each time. What does Tornado provide for us? Its <a href="http://www.tornadoweb.org/en/branch2.3/testing.html">AsyncTestCase</a> gives us <code>start</code> and <code>stop</code> methods to control the event loop. If we then move the duration-testing outside the callback we radically simplify our test:</p>

{{<highlight python3>}}
from tornado import testing

class MyTestCase(testing.AsyncTestCase):
    def test_delay(self):
        start = time.time()
        delay_async(1, callback=self.stop)
        self.wait()
        duration = time.time() - start
        self.assertAlmostEqual(duration, 1, places=2)
{{< / highlight >}}

<h1 id="gen_test"><code>gen_test</code></h1>
<p>But modern async code is not primarily written with callbacks: these days we use <a href="http://tornado.readthedocs.org/en/latest/guide/coroutines.html">coroutines</a>. Let us begin a new example test, one that uses <a href="https://motor.readthedocs.org/">Motor, my asynchronous MongoDB driver for Tornado</a>. Although Motor supports the old callback style, it encourages you to use coroutines and "yield" statements, so we can write some Motor code to demonstrate Tornado coroutines and unittesting.</p>
<p>To begin, say we want to execute <a href="http://motor.readthedocs.org/en/stable/api-tornado/motor_collection.html#motor.MotorCollection.find_one"><code>find_one</code></a> and test its return value:</p>

{{<highlight python3>}}
from motor import MotorClient
from tornado import testing

class MyTestCase(testing.AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.client = MotorClient()

    def test_find_one(self):
        collection = self.client.test.collection
        document = yield collection.find_one({'_id': 1})
        self.assertEqual({'_id': 1, 'key': 'value'}, document)
{{< / highlight >}}

<p>Notice the "yield" statement: whenever you call a Motor method that does I/O, you must use "yield" to pause the current function and wait for the returned Future object to be resolved to a value. Including a yield statement makes this function a generator. But now there is a problem:</p>

{{<highlight plain>}}
TypeError: Generator test methods should be decorated with tornado.testing.gen_test
{{< / highlight >}}

<p>Tornado smartly warns us that our test method is merely a generator—we must decorate it with <a href="http://tornado.readthedocs.org/en/latest/testing.html#tornado.testing.gen_test">gen_test</a>. Otherwise the test method simply stops at the first yield, and never reaches the assert. It needs a coroutine <em>driver</em> to run it to completion:</p>

{{<highlight python3>}}
from tornado.testing import gen_test

class MyTestCase(testing.AsyncTestCase):
    # ... same setup ...
    @gen_test
    def test_find_one(self):
        collection = self.client.test.collection
        document = yield collection.find_one({'_id': 1})
        self.assertEqual({'_id': 1, 'key': 'value'}, document)
{{< / highlight >}}

<p>But now when I run the test, it fails:</p>

{{<highlight plain>}}
AssertionError: {'key': 'value', '_id': 1} != None
{{< / highlight >}}

<p>We need to insert some data in <code>setUp</code> so that <code>find_one</code> can find it! Since Motor is asynchronous, we cannot call its <code>insert</code> method directly from <code>setUp</code>, we must run the insertion in a coroutine as well:</p>

{{<highlight python3>}}
from tornado import gen, testing

class MyTestCase(testing.AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.client = MotorClient()
        self.setup_coro()

    @gen.coroutine
    def setup_coro(self):
        collection = self.client.test.collection

        # Clean up from prior runs:
        yield collection.remove()

        yield collection.insert({'_id': 0})
        yield collection.insert({'_id': 1, 'key': 'value'})
        yield collection.insert({'_id': 2})
{{< / highlight >}}

<p>Now when I run the test:</p>

{{<highlight plain>}}
AssertionError: {'key': 'value', '_id': 1} != None
{{< / highlight >}}

<p>It still fails! When I check in the mongo shell whether my data was inserted, only two of the three expected documents are there:</p>

{{<highlight plain>}}
> db.collection.find()
{ "_id" : 0 }
{ "_id" : 1, "key" : "value" }
{{< / highlight >}}

<p>Why is it incomplete? Furthermore, since the document I actually query <em>is</em> there, why did the test fail?</p>
<p>When I called <code>self.setup_coro()</code> in <code>setUp</code>, I launched it as a <em>concurrent</em> coroutine. It began running, but I did not wait for it to complete before beginning the test, so the test may reach its <code>find_one</code> statement before the second document is inserted. Furthermore, <code>test_find_one</code> can fail quickly enough that <code>setup_coro</code> does not insert its third document before the whole test suite finishes, stopping the event loop and preventing the final document from ever being inserted.</p>
<p>Clearly I must wait for the setup coroutine to complete before beginning the test. Tornado's <code>run_sync</code> method is designed for uses like this:</p>

{{<highlight python3>}}
class MyTestCase(testing.AsyncTestCase):
    def setUp(self):
        super().setUp()
        self.client = MotorClient()
        self.io_loop.run_sync(self.setup_coro)
{{< / highlight >}}

<p>With my setup coroutine correctly executed, now <code>test_find_one</code> passes.</p>
<h1 id="further-study">Further Study</h1>
<p>Now we have seen two techniques that make async testing with Tornado as convenient and reliable as standard unittests. To learn more, see my page of <a href="/eventually-correct-links/">links related to this article</a>.</p>
<p>Plus, stay tuned for the next book in the <a href="http://aosabook.org/">Architecture of Open Source Applications</a> series. It will be called "500 Lines or Less", and my chapter is devoted to the implementation of coroutines in asyncio and Python 3.</p>
