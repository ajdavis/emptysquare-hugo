+++
type = "post"
title = "Tornado Unittesting: Eventually Correct"
date = "2011-12-16T13:52:55"
description = "Photo: Tim Green I'm a fan of Tornado, one of the major async web frameworks for Python, but unittesting async code is a total pain. I'm going to review what the problem is, look at some klutzy solutions, and propose a better way. If you don't [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "sundial.jpg"
draft = false
disqus_identifier = "276 http://emptysquare.net/blog/?p=276"
disqus_url = "https://emptysqua.re/blog/276 http://emptysquare.net/blog/?p=276/"
+++

<p><img src="sundial.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Time was, time is"/></p>
<p><a href="http://www.flickr.com/photos/atoach/3945656686/">Photo: Tim Green</a></p>
<p>I'm a fan of <a href="http://www.tornadoweb.org/">Tornado</a>, one of the major
async web frameworks for Python, but unittesting async code is a total
pain. I'm going to review what the problem is, look at some klutzy
solutions, and propose a better way. If you don't care what I have to
say and you just want to steal my code, <a href="https://github.com/ajdavis/tornado-test">get it on
GitHub</a>.</p>
<h1 id="the-problem">The problem</h1>
<p>Let's say you're working on some profoundly complex library that
performs a time-consuming calculation, and you want to test its output:</p>

{{<highlight python3>}}
# test_sync.py
import time
import unittest

def calculate():
    # Do something profoundly complex
    time.sleep(1)
    return 42

class SyncTest(unittest.TestCase):
    def test_find(self):
        result = calculate()
        self.assertEqual(42, result)

if __name__ == '__main__':
    unittest.main()
{{< / highlight >}}

<p>See? You do an operation, then you check that you got the expected
result. No sweat.</p>
<p>But what about testing an asynchronous calculation? You're going to have
some troubles. Let's write an asynchronous calculator and test it:</p>

{{<highlight python3>}}
# test_async.py
import time
import unittest
from tornado import ioloop

def async_calculate(callback):
    """
    @param callback:    A function taking params (result, error)
    """
    # Do something profoundly complex requiring non-blocking I/O, which
    # will complete in one second
    ioloop.IOLoop.instance().add_timeout(
        time.time() + 1,
        lambda: callback(42, None)
    )

class AsyncTest(unittest.TestCase):
    def test_find(self):
        def callback(result, error):
            print 'Got result', result
            self.assertEqual(42, result)

        async_calculate(callback)
        ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    unittest.main()
{{< / highlight >}}

<p>Huh. If you run <code>python test_async.py</code>, you see the expected result is
printed to the console:</p>

{{<highlight plain>}}
Got result 42
{{< / highlight >}}

<p>... and then the program hangs forever. The problem is that
<code>ioloop.IOLoop.instance().start()</code> starts an infinite loop. You have to
stop it explicitly before the call to <code>start()</code> will return.</p>
<h1 id="a-klutzy-solution">A Klutzy Solution</h1>
<p>Let's stop the loop in the callback:</p>

{{<highlight python3>}}
def callback(result, error):
    ioloop.IOLoop.instance().stop()
    print 'Got result', result
    self.assertEqual(42, result)
{{< / highlight >}}

<p>Now if you run <code>python test_async.py</code> everything's copacetic:</p>

{{<highlight plain>}}
$ python test_async.py 
Got result 42
.
{{< / highlight >}}

<hr/>

{{<highlight plain>}}
Ran 1 test in 1.001s

OK
{{< / highlight >}}

<p>Let's see if our test will actually catch a bug. Change the
<code>async_calculate()</code> function to produce the number 17 instead of 42:</p>

{{<highlight python3>}}
def async_calculate(callback):
    """
    @param callback:    A function taking params (result, error)
    """
    # Do something profoundly complex requiring non-blocking I/O, which
    # will complete in one second
    ioloop.IOLoop.instance().add_timeout(
        time.time() + 1,
        lambda: callback(17, None)
    )
{{< / highlight >}}

<p>And run the test:</p>

{{<highlight plain>}}
$ python foo.py 
Got result 17
ERROR:root:Exception in callback <tornado.stack_context._StackContextWrapper object at 0x102420158>
Traceback (most recent call last):
  File "/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py", line 396, in _run_callback
    callback()
  File "foo.py", line 14, in <lambda>
    lambda: callback(17, None)
  File "foo.py", line 22, in callback
    self.assertEqual(42, result)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/unittest/case.py", line 494, in assertEqual
    assertion_func(first, second, msg=msg)
  File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/unittest/case.py", line 487, in _baseAssertEqual
    raise self.failureException(msg)
AssertionError: 42 != 17
.
{{< / highlight >}}

<hr/>

{{<highlight plain>}}
Ran 1 test in 1.002s

OK
{{< / highlight >}}

<p>An <code>AssertionError</code> is raised, but the test still <strong>passes</strong>! Alas,
Tornado's IOLoop suppresses all exceptions. The exceptions are printed
to the console, but the unittest framework thinks the test has passed.</p>
<h1 id="a-better-way">A Better Way</h1>
<p>We're going to perform some minor surgery on Tornado to fix this up, by
creating and installing our own IOLoop which re-raises all exceptions in
callbacks. Luckily, Tornado makes this easy. Add <code>import sys</code> to the top
of test_async.py, and paste in the following:</p>

{{<highlight python3>}}
class PuritanicalIOLoop(ioloop.IOLoop):
    """
    A loop that quits when it encounters an Exception.
    """
    def handle_callback_exception(self, callback):
        exc_type, exc_value, tb = sys.exc_info()
        raise exc_value
{{< / highlight >}}

<p>Now add a <code>setUp()</code> method to <code>AsyncTest</code> which will install our
puritanical loop:</p>

{{<highlight python3>}}
def setUp(self):
    super(AsyncTest, self).setUp()

    # So any function that calls IOLoop.instance() gets the
    # PuritanicalIOLoop instead of the default loop.
    if not ioloop.IOLoop.initialized():
        loop = PuritanicalIOLoop()
        loop.install()
    else:
        loop = ioloop.IOLoop.instance()
        self.assert_(
            isinstance(loop, PuritanicalIOLoop),
            "Couldn't install PuritanicalIOLoop"
        )
{{< / highlight >}}

<p>This is a bit over-complicated for our simple case—a call to
<code>PuritanicalIOLoop().install()</code> would suffice—but this will all come in
handy later. In our simple test suite, <code>setUp()</code> is only run once, so
the check for <code>IOLoop.initialized()</code> is unnecessary, but you'll need it
if you run multiple tests. The call to <code>super()</code> will be necessary if we
inherit from a <code>TestCase</code> with a <code>setUp()</code> method, which is exactly what
we're going to do below. For now, just run <code>python test_async.py</code> and
observe that we get a proper failure:</p>

{{<highlight plain>}}
$ python foo.py 
Got result 17
F
======================================================================
FAIL: test_find (__main__.SyncTest)
{{< / highlight >}}

<hr/>

{{<highlight plain>}}
Traceback (most recent call last):
  File "foo.py", line 49, in test_find
    ioloop.IOLoop.instance().start()
  File "/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py", line 263, in start
    self._run_callback(timeout.callback)
  File "/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py", line 398, in _run_callback
    self.handle_callback_exception(callback)
  File "foo.py", line 25, in handle_callback_exception
    raise exc_value
AssertionError: 42 != 17
{{< / highlight >}}

<hr/>

{{<highlight plain>}}
Ran 1 test in 1.002s

FAILED (failures=1)
{{< / highlight >}}

<p>Lovely. Change <code>async_calculate()</code> back to the correct version that
produces 42.</p>
<h1 id="an-even-better-way">An Even Better Way</h1>
<p>So we've verified that our test catches bugs in the calculation. But
what if we have a bug that prevents our callback from ever being called?
Add a return statement at the top of <code>async_calculate()</code> so we don't
execute the callback:</p>

{{<highlight python3>}}
def async_calculate(callback):
    """
    @param callback:    A function taking params (result, error)
    """
    # Do something profoundly complex requiring non-blocking I/O, which
    # will complete in one second
    return
    ioloop.IOLoop.instance().add_timeout(
        time.time() + 1,
        lambda: callback(42, None)
    )
{{< / highlight >}}

<p>Now if we run the test, it hangs forever, because <code>IOLoop.stop()</code> is
never called. How can we write a test that asserts that the callback is
<strong>eventually</strong> executed? Never fear, I've written some code:</p>

{{<highlight python3>}}
class AssertEventuallyTest(unittest.TestCase):
    def setUp(self):
        super(AssertEventuallyTest, self).setUp()

        # Callbacks registered with assertEventuallyEqual()
        self.assert_callbacks = set()

    def assertEventuallyEqual(
        self, expected, fn, msg=None, timeout_sec=None
    ):
        if timeout_sec is None:
            timeout_sec = 5
        timeout_sec = max(timeout_sec, int(os.environ.get('TIMEOUT_SEC', 0)))
        start = time.time()
        loop = ioloop.IOLoop.instance()

        def callback():
            try:
                self.assertEqual(expected, fn(), msg)
                # Passed
                self.assert_callbacks.remove(callback)
                if not self.assert_callbacks:
                    # All asserts have passed
                    loop.stop()
            except AssertionError:
                # Failed -- keep waiting?
                if time.time() - start &lt; timeout_sec:
                    # Try again in about 0.1 seconds
                    loop.add_timeout(time.time() + 0.1, callback)
                else:
                    # Timeout expired without passing test
                    loop.stop()
                    raise

        self.assert_callbacks.add(callback)

        # Run this callback on the next I/O loop iteration
        loop.add_callback(callback)
{{< / highlight >}}

<p>This class lets us register any number of functions which are called
periodically until they equal their expected values, or time out. The
last function that succeeds or times out stops the IOLoop, so your test
definitely finishes. The timeout is configurable, either as an argument
to <code>assertEventuallyEqual()</code> or as an environment variable
<code>TIMEOUT_SEC</code>. Setting a very large timeout value in your environment is
useful for debugging a misbehaving unittest—set it to a million seconds
so you don't time out while you're stepping through the code.</p>
<p>(My code's inspired by the Scala world's
<a href="http://code.google.com/p/specs/wiki/MatchersGuide#Eventually_matchers">"eventually"</a>
test, which <a href="https://twitter.com/#!/RIT">Brendan W. McAdams</a> showed me.)</p>
<p>Paste <code>AssertEventuallyTest</code> into test_async.py and fix up your test
case to inherit from it:</p>

{{<highlight python3>}}
class AsyncTest(AssertEventuallyTest):
    def setUp(self):
        # ... snip ...

    def test_find(self):
        results = []
        def callback(result, error):
            print 'Got result', result
            results.append(result)

        async_calculate(callback)

        self.assertEventuallyEqual(
            42,
            lambda: results and results[0]
        )

        ioloop.IOLoop.instance().start()
{{< / highlight >}}

<p>The call to <code>IOLoop.stop()</code> is gone from the callback, and we've added a
call to <code>assertEventuallyEqual()</code> just before starting the IOLoop.</p>
<p>There are two details to note about this code:</p>
<p><strong>Detail the First:</strong> <code>assertEventuallyEqual()</code>'s first argument is the
expected value, and its second argument is a <strong>function</strong> that should
eventually equal the expected value. Hence the lambda.</p>
<p><strong>Detail the Second:</strong> <code>callback()</code> needs a place to store its result so
that lambda can find it, but here we run into a nasty peculiarity of
Python. Python functions can assign to variables in their own scope, or
the global scope (with the <code>global</code> keyword), but inner functions can't
assign to values in outer functions' scope. Python 3 introduces a
<code>nonlocal</code> keyword to solve this, but meanwhile we can hack around the
problem by creating a <code>results</code> list in the outer function and
<code>append</code>ing to it in the inner function. This is a common idiom that
you'll use a lot when you write callbacks in asynchronous unittests.</p>
<h1 id="conclusion">Conclusion</h1>
<p>I've packed up <a href="https://github.com/ajdavis/tornado-test"><code>PuritanicalIOLoop</code> and <code>AssertEventuallyTest</code> on
GitHub</a>; go grab the code. Your
test cases can choose to inherit from <code>PuritanicalTornadoTest</code>,
<code>AssertEventuallyTest</code>, or both. Just make sure your <code>setUp</code> methods
call <code>super(MyTestCaseClass, self).setUp()</code>. Go forth and test!</p>
