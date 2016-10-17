+++
type = "post"
title = "Eventually Correct: Async Testing With Tornado"
date = "2015-04-10T22:03:32"
description = "Event-loop management, error handling, and coroutines as unittests."
"blog/category" = ["Motor", "Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "toad-vs-birdo@240.jpg"
draft = false
legacyid = "5526a9645393741c70651f95"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="toad-vs-birdo.jpg" alt="Toad vs Birdo" title="Toad vs Birdo" /></p>
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
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">time</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">unittest</span>

<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">my_application</span> <span style="color: #008000; font-weight: bold">import</span> delay


<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
        delay(<span style="color: #666666">1</span>)
        duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
</pre></div>


<p>When we run this, it prints:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 1.000s
OK
</pre></div>


<p>And if we replace <code>delay(1)</code> with <code>delay(2)</code> it fails as expected:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">=======================================================
FAIL: test_delay (delay0.MyTestCase)
------------------------------------------------------
Traceback (most recent call last):
File &quot;delay0.py&quot;, line 12, in test_delay
    self.assertAlmostEqual(duration, 1, places=2)
AssertionError: 2.000854969024658 != 1 within 2 places

------------------------------------------------------
Ran 1 test in 2.002s
FAILED (failures=1)
</pre></div>


<p>Great! What about testing a <code>delay_async(seconds, callback)</code> function?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
<span style="background-color: #ffffcc">        delay_async(<span style="color: #666666">1</span>, callback<span style="color: #666666">=</span>)  <span style="color: #408080; font-style: italic"># What goes here?</span>
</span>        duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
</pre></div>


<p>An asynchronous "delay" function can't block the caller, so it must take a callback and execute it once the delay is over. (In fact we are just reimplementing Tornado's <a href="http://tornado.readthedocs.org/en/latest/ioloop.html#tornado.ioloop.IOLoop.call_later"><code>call_later</code></a>, but please pretend for pedagogy's sake this is a new function that we must test.) To test our <code>delay_async</code>, we will try a series of testing techniques until we have effectively built Tornado's test framework from scratch&mdash;you will see why we need special test tools for async code and how Tornado's tools work.</p>
<p>So, we define a function <code>done</code> to measure the delay, and pass it as the callback to <code>delay_async</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done</span>():
            duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)

        delay_async(<span style="color: #666666">1</span>, done)
</pre></div>


<p>If we run this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 0.001s
OK
</pre></div>


<p>Success! ...right? But why does it only take a millisecond? And what happens if we delay by two seconds instead?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done</span>():
            duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)

<span style="background-color: #ffffcc">        delay_async(<span style="color: #666666">2</span>, done)
</span></pre></div>


<p>Run it again:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 0.001s
OK
</pre></div>


<p>Something is very wrong here. The test appears to pass instantly, regardless of the argument to <code>delay_async</code>, because we neither start the event loop nor wait for it to complete. We have to actually pause the test until the callback has executed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
<span style="background-color: #ffffcc">        io_loop <span style="color: #666666">=</span> IOLoop<span style="color: #666666">.</span>instance()
</span>
        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done</span>():
            duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
<span style="background-color: #ffffcc">            io_loop<span style="color: #666666">.</span>stop()
</span>
        delay_async(<span style="color: #666666">1</span>, done)
<span style="background-color: #ffffcc">        io_loop<span style="color: #666666">.</span>start()
</span></pre></div>


<p>Now if we run the test with a delay of one second:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 1.002s
OK
</pre></div>


<p>That looks better. And if we delay for two seconds?</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">ERROR:tornado.application:Exception in callback
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;site-packages/tornado/ioloop.py&quot;</span>, line <span style="color: #666666">568</span>, in _run_callback
    ret <span style="color: #666666">=</span> callback()
  File <span style="color: #008000">&quot;site-packages/tornado/stack_context.py&quot;</span>, line <span style="color: #666666">275</span>, in null_wrapper
    <span style="color: #008000; font-weight: bold">return</span> fn(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)
  File <span style="color: #008000">&quot;delay3.py&quot;</span>, line <span style="color: #666666">16</span>, in done
    <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
  File <span style="color: #008000">&quot;unittest/case.py&quot;</span>, line <span style="color: #666666">845</span>, in assertAlmostEqual
    <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>failureException(msg)
<span style="color: #FF0000">AssertionError</span>: 2.001540184020996 != 1 within 2 places
</pre></div>


<p>The test appears to fail, as expected, but there are a few problems. First, notice that it is not the unittest that prints the traceback: it is Tornado's application logger. We do not get the unittest's characteristic output. Second, the process is now hung and remains so until I type Control-C. Why?</p>
<p>The bug is here:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done</span>():
            duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
<span style="background-color: #ffffcc">            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
</span>            io_loop<span style="color: #666666">.</span>stop()
</pre></div>


<p>Since the failed assertion raises an exception, we never reach the call to <code>io_loop.stop()</code>, so the loop continues running and the process does not exit. We need to register an exception handler. Exception handling with callbacks is convoluted; we have to use a <a href="http://www.tornadoweb.org/en/branch2.3/stack_context.html">stack context</a> to install a handler with Tornado:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.stack_context</span> <span style="color: #008000; font-weight: bold">import</span> ExceptionStackContext

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
        io_loop <span style="color: #666666">=</span> IOLoop<span style="color: #666666">.</span>instance()

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done</span>():
            duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
            io_loop<span style="color: #666666">.</span>stop()

        <span style="color: #008000">self</span><span style="color: #666666">.</span>failure <span style="color: #666666">=</span> <span style="color: #008000">None</span>

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">handle_exception</span>(typ, value, tb):
            io_loop<span style="color: #666666">.</span>stop()
            <span style="color: #008000">self</span><span style="color: #666666">.</span>failure <span style="color: #666666">=</span> value
            <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">True</span>  <span style="color: #408080; font-style: italic"># Stop propagation.</span>

        <span style="color: #008000; font-weight: bold">with</span> ExceptionStackContext(handle_exception):
            delay_async(<span style="color: #666666">2</span>, callback<span style="color: #666666">=</span>done)

        io_loop<span style="color: #666666">.</span>start()
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>failure:
            <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>failure
</pre></div>


<p>The loop can now be stopped two ways: if the test passes, then <code>done</code> stops the loop as before. If it fails, <code>handle_exception</code> stores the error and stops the loop. At the end, if an error was stored we re-raise it to make the test fail:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">=======================================================
FAIL: test_delay (delay4.MyTestCase)
------------------------------------------------------
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;delay4.py&quot;</span>, line <span style="color: #666666">31</span>, in test_delay
    <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>failure
  File <span style="color: #008000">&quot;tornado/ioloop.py&quot;</span>, line <span style="color: #666666">568</span>, in _run_callback
    ret <span style="color: #666666">=</span> callback()
  File <span style="color: #008000">&quot;tornado/stack_context.py&quot;</span>, line <span style="color: #666666">343</span>, in wrapped
    raise_exc_info(exc)
  File <span style="color: #008000">&quot;&lt;string&gt;&quot;</span>, line <span style="color: #666666">3</span>, in raise_exc_info
  File <span style="color: #008000">&quot;tornado/stack_context.py&quot;</span>, line <span style="color: #666666">314</span>, in wrapped
    ret <span style="color: #666666">=</span> fn(<span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)
  File <span style="color: #008000">&quot;delay4.py&quot;</span>, line <span style="color: #666666">17</span>, in done
    <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
<span style="color: #FF0000">AssertionError</span>: 2.0015950202941895 != 1 within 2 places
------------------------------------------------------
Ran 1 test in 2.004s
FAILED (failures=1)
</pre></div>


<p>Now the test ends promptly, whether it succeeds or fails, with unittest's typical output.</p>
<p>This is a lot of tricky code to write just to test a trivial delay function, and it seems hard to get right each time. What does Tornado provide for us? Its <a href="http://www.tornadoweb.org/en/branch2.3/testing.html">AsyncTestCase</a> gives us <code>start</code> and <code>stop</code> methods to control the event loop. If we then move the duration-testing outside the callback we radically simplify our test:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> testing

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(testing<span style="color: #666666">.</span>AsyncTestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_delay</span>(<span style="color: #008000">self</span>):
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
<span style="background-color: #ffffcc">        delay_async(<span style="color: #666666">1</span>, callback<span style="color: #666666">=</span><span style="color: #008000">self</span><span style="color: #666666">.</span>stop)
</span><span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>wait()
</span>        duration <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertAlmostEqual(duration, <span style="color: #666666">1</span>, places<span style="color: #666666">=2</span>)
</pre></div>


<h1 id="gen_test"><code>gen_test</code></h1>
<p>But modern async code is not primarily written with callbacks: these days we use <a href="http://tornado.readthedocs.org/en/latest/guide/coroutines.html">coroutines</a>. Let us begin a new example test, one that uses <a href="https://motor.readthedocs.org/">Motor, my asynchronous MongoDB driver for Tornado</a>. Although Motor supports the old callback style, it encourages you to use coroutines and "yield" statements, so we can write some Motor code to demonstrate Tornado coroutines and unittesting.</p>
<p>To begin, say we want to execute <a href="http://motor.readthedocs.org/en/latest/api/motor_collection.html#motor.MotorCollection.find_one"><code>find_one</code></a> and test its return value:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">motor</span> <span style="color: #008000; font-weight: bold">import</span> MotorClient
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> testing

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(testing<span style="color: #666666">.</span>AsyncTestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>()<span style="color: #666666">.</span>setUp()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>client <span style="color: #666666">=</span> MotorClient()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_find_one</span>(<span style="color: #008000">self</span>):
        collection <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>client<span style="color: #666666">.</span>test<span style="color: #666666">.</span>collection
<span style="background-color: #ffffcc">        document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
</span><span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;key&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}, document)
</span></pre></div>


<p>Notice the "yield" statement: whenever you call a Motor method that does I/O, you must use "yield" to pause the current function and wait for the returned Future object to be resolved to a value. Including a yield statement makes this function a generator. But now there is a problem:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">TypeError<span style="color: #666666">:</span> Generator test methods should be decorated <span style="color: #008000; font-weight: bold">with</span> tornado<span style="color: #666666">.</span><span style="color: #7D9029">testing</span><span style="color: #666666">.</span><span style="color: #7D9029">gen_test</span>
</pre></div>


<p>Tornado smartly warns us that our test method is merely a generator&mdash;we must decorate it with <a href="http://tornado.readthedocs.org/en/latest/testing.html#tornado.testing.gen_test">gen_test</a>. Otherwise the test method simply stops at the first yield, and never reaches the assert. It needs a coroutine <em>driver</em> to run it to completion:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="background-color: #ffffcc"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.testing</span> <span style="color: #008000; font-weight: bold">import</span> gen_test
</span>
<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(testing<span style="color: #666666">.</span>AsyncTestCase):
    <span style="color: #408080; font-style: italic"># ... same setup ...</span>
<span style="background-color: #ffffcc">    <span style="color: #AA22FF">@gen_test</span>
</span>    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_find_one</span>(<span style="color: #008000">self</span>):
        collection <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>client<span style="color: #666666">.</span>test<span style="color: #666666">.</span>collection
        document <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>find_one({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>})
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;key&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>}, document)
</pre></div>


<p>But now when I run the test, it fails:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">AssertionError: {&#39;key&#39;: &#39;value&#39;, &#39;_id&#39;: 1} != None
</pre></div>


<p>We need to insert some data in <code>setUp</code> so that <code>find_one</code> can find it! Since Motor is asynchronous, we cannot call its <code>insert</code> method directly from <code>setUp</code>, we must run the insertion in a coroutine as well:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="background-color: #ffffcc"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> gen, testing
</span>
<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(testing<span style="color: #666666">.</span>AsyncTestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>()<span style="color: #666666">.</span>setUp()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>client <span style="color: #666666">=</span> MotorClient()
<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>setup_coro()
</span>
<span style="background-color: #ffffcc">    <span style="color: #AA22FF">@gen.coroutine</span>
</span>    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setup_coro</span>(<span style="color: #008000">self</span>):
        collection <span style="color: #666666">=</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>client<span style="color: #666666">.</span>test<span style="color: #666666">.</span>collection

        <span style="color: #408080; font-style: italic"># Clean up from prior runs:</span>
        <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>remove()

        <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">0</span>})
        <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;key&#39;</span>: <span style="color: #BA2121">&#39;value&#39;</span>})
        <span style="color: #008000; font-weight: bold">yield</span> collection<span style="color: #666666">.</span>insert({<span style="color: #BA2121">&#39;_id&#39;</span>: <span style="color: #666666">2</span>})
</pre></div>


<p>Now when I run the test:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">AssertionError: {&#39;key&#39;: &#39;value&#39;, &#39;_id&#39;: 1} != None
</pre></div>


<p>It still fails! When I check in the mongo shell whether my data was inserted, only two of the three expected documents are there:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">&gt; db.collection.find()
{ &quot;_id&quot; : 0 }
{ &quot;_id&quot; : 1, &quot;key&quot; : &quot;value&quot; }
</pre></div>


<p>Why is it incomplete? Furthermore, since the document I actually query <em>is</em> there, why did the test fail?</p>
<p>When I called <code>self.setup_coro()</code> in <code>setUp</code>, I launched it as a <em>concurrent</em> coroutine. It began running, but I did not wait for it to complete before beginning the test, so the test may reach its <code>find_one</code> statement before the second document is inserted. Furthermore, <code>test_find_one</code> can fail quickly enough that <code>setup_coro</code> does not insert its third document before the whole test suite finishes, stopping the event loop and preventing the final document from ever being inserted.</p>
<p>Clearly I must wait for the setup coroutine to complete before beginning the test. Tornado's <code>run_sync</code> method is designed for uses like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyTestCase</span>(testing<span style="color: #666666">.</span>AsyncTestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>()<span style="color: #666666">.</span>setUp()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>client <span style="color: #666666">=</span> MotorClient()
<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>io_loop<span style="color: #666666">.</span>run_sync(<span style="color: #008000">self</span><span style="color: #666666">.</span>setup_coro)
</span></pre></div>


<p>With my setup coroutine correctly executed, now <code>test_find_one</code> passes.</p>
<h1 id="further-study">Further Study</h1>
<p>Now we have seen two techniques that make async testing with Tornado as convenient and reliable as standard unittests. To learn more, see my page of <a href="/blog/eventually-correct-links/">links related to this article</a>.</p>
<p>Plus, stay tuned for the next book in the <a href="http://aosabook.org/">Architecture of Open Source Applications</a> series. It will be called "500 Lines or Less", and my chapter is devoted to the implementation of coroutines in asyncio and Python 3.</p>
    