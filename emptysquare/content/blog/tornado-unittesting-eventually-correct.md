+++
type = "post"
title = "Tornado Unittesting: Eventually Correct"
date = "2011-12-16T13:52:55"
description = "Photo: Tim Green I'm a fan of Tornado, one of the major async web frameworks for Python, but unittesting async code is a total pain. I'm going to review what the problem is, look at some klutzy solutions, and propose a better way. If you don't [ ... ]"
categories = ["Programming", "Python"]
tags = []
enable_lightbox = false
thumbnail = "sundial.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="sundial.jpg" title="Time was, time is" /></p>
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
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># test_sync.py</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">time</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">unittest</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">calculate</span>():
    <span style="color: #408080; font-style: italic"># Do something profoundly complex</span>
    time<span style="color: #666666">.</span>sleep(<span style="color: #666666">1</span>)
    <span style="color: #008000; font-weight: bold">return</span> <span style="color: #666666">42</span>

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">SyncTest</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_find</span>(<span style="color: #008000">self</span>):
        result <span style="color: #666666">=</span> calculate()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(<span style="color: #666666">42</span>, result)

<span style="color: #008000; font-weight: bold">if</span> __name__ <span style="color: #666666">==</span> <span style="color: #BA2121">&#39;__main__&#39;</span>:
    unittest<span style="color: #666666">.</span>main()
</pre></div>


<p>See? You do an operation, then you check that you got the expected
result. No sweat.</p>
<p>But what about testing an asynchronous calculation? You're going to have
some troubles. Let's write an asynchronous calculator and test it:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># test_async.py</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">time</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">unittest</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> ioloop

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">async_calculate</span>(callback):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;</span>
<span style="color: #BA2121; font-style: italic">    @param callback:    A function taking params (result, error)</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #408080; font-style: italic"># Do something profoundly complex requiring non-blocking I/O, which</span>
    <span style="color: #408080; font-style: italic"># will complete in one second</span>
    ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>add_timeout(
        time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> <span style="color: #666666">1</span>,
        <span style="color: #008000; font-weight: bold">lambda</span>: callback(<span style="color: #666666">42</span>, <span style="color: #008000">None</span>)
    )

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">AsyncTest</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_find</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>(result, error):
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Got result&#39;</span>, result
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(<span style="color: #666666">42</span>, result)

        async_calculate(callback)
        ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()

<span style="color: #008000; font-weight: bold">if</span> __name__ <span style="color: #666666">==</span> <span style="color: #BA2121">&#39;__main__&#39;</span>:
    unittest<span style="color: #666666">.</span>main()
</pre></div>


<p>Huh. If you run <code>python test_async.py</code>, you see the expected result is
printed to the console:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Got result 42
</pre></div>


<p>... and then the program hangs forever. The problem is that
<code>ioloop.IOLoop.instance().start()</code> starts an infinite loop. You have to
stop it explicitly before the call to <code>start()</code> will return.</p>
<h1 id="a-klutzy-solution">A Klutzy Solution</h1>
<p>Let's stop the loop in the callback:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>(result, error):
<span style="background-color: #ffffcc">            ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>stop()
</span>            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Got result&#39;</span>, result
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(<span style="color: #666666">42</span>, result)
</pre></div>


<p>Now if you run <code>python test_async.py</code> everything's copacetic:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>python test_async.py 
Got result 42
.
</pre></div>


<hr />
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 1.001s

OK
</pre></div>


<p>Let's see if our test will actually catch a bug. Change the
<code>async_calculate()</code> function to produce the number 17 instead of 42:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">async_calculate</span>(callback):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;</span>
<span style="color: #BA2121; font-style: italic">    @param callback:    A function taking params (result, error)</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #408080; font-style: italic"># Do something profoundly complex requiring non-blocking I/O, which</span>
    <span style="color: #408080; font-style: italic"># will complete in one second</span>
    ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>add_timeout(
        time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> <span style="color: #666666">1</span>,
<span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">lambda</span>: callback(<span style="color: #666666">17</span>, <span style="color: #008000">None</span>)
</span>    )
</pre></div>


<p>And run the test:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>python foo.py 
Got result 17
ERROR:root:Exception in callback &lt;tornado.stack_context._StackContextWrapper object at 0x102420158&gt;
Traceback <span style="color: #666666">(</span>most recent call last<span style="color: #666666">)</span>:
  File <span style="color: #BA2121">&quot;/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py&quot;</span>, line 396, in _run_callback
    callback<span style="color: #666666">()</span>
  File <span style="color: #BA2121">&quot;foo.py&quot;</span>, line 14, in &lt;lambda&gt;
    lambda: callback<span style="color: #666666">(</span>17, None<span style="color: #666666">)</span>
  File <span style="color: #BA2121">&quot;foo.py&quot;</span>, line 22, in callback
    self.assertEqual<span style="color: #666666">(</span>42, result<span style="color: #666666">)</span>
  File <span style="color: #BA2121">&quot;/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/unittest/case.py&quot;</span>, line 494, in assertEqual
    assertion_func<span style="color: #666666">(</span>first, second, <span style="color: #19177C">msg</span><span style="color: #666666">=</span>msg<span style="color: #666666">)</span>
  File <span style="color: #BA2121">&quot;/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/unittest/case.py&quot;</span>, line 487, in _baseAssertEqual
    raise self.failureException<span style="color: #666666">(</span>msg<span style="color: #666666">)</span>
AssertionError: <span style="color: #666666">42</span> !<span style="color: #666666">=</span> 17
.
</pre></div>


<hr />
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 1.002s

OK
</pre></div>


<p>An <code>AssertionError</code> is raised, but the test still <strong>passes</strong>! Alas,
Tornado's IOLoop suppresses all exceptions. The exceptions are printed
to the console, but the unittest framework thinks the test has passed.</p>
<h1 id="a-better-way">A Better Way</h1>
<p>We're going to perform some minor surgery on Tornado to fix this up, by
creating and installing our own IOLoop which re-raises all exceptions in
callbacks. Luckily, Tornado makes this easy. Add <code>import sys</code> to the top
of test_async.py, and paste in the following:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">PuritanicalIOLoop</span>(ioloop<span style="color: #666666">.</span>IOLoop):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;</span>
<span style="color: #BA2121; font-style: italic">    A loop that quits when it encounters an Exception.</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">handle_callback_exception</span>(<span style="color: #008000">self</span>, callback):
        exc_type, exc_value, tb <span style="color: #666666">=</span> sys<span style="color: #666666">.</span>exc_info()
        <span style="color: #008000; font-weight: bold">raise</span> exc_value
</pre></div>


<p>Now add a <code>setUp()</code> method to <code>AsyncTest</code> which will install our
puritanical loop:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>(AsyncTest, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>setUp()

        <span style="color: #408080; font-style: italic"># So any function that calls IOLoop.instance() gets the</span>
        <span style="color: #408080; font-style: italic"># PuritanicalIOLoop instead of the default loop.</span>
        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>initialized():
            loop <span style="color: #666666">=</span> PuritanicalIOLoop()
            loop<span style="color: #666666">.</span>install()
        <span style="color: #008000; font-weight: bold">else</span>:
            loop <span style="color: #666666">=</span> ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()
            <span style="color: #008000">self</span><span style="color: #666666">.</span>assert_(
                <span style="color: #008000">isinstance</span>(loop, PuritanicalIOLoop),
                <span style="color: #BA2121">&quot;Couldn&#39;t install PuritanicalIOLoop&quot;</span>
            )
</pre></div>


<p>This is a bit over-complicated for our simple case—a call to
<code>PuritanicalIOLoop().install()</code> would suffice—but this will all come in
handy later. In our simple test suite, <code>setUp()</code> is only run once, so
the check for <code>IOLoop.initialized()</code> is unnecessary, but you'll need it
if you run multiple tests. The call to <code>super()</code> will be necessary if we
inherit from a <code>TestCase</code> with a <code>setUp()</code> method, which is exactly what
we're going to do below. For now, just run <code>python test_async.py</code> and
observe that we get a proper failure:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>python foo.py 
Got result 17
<span style="color: #19177C">F</span>
<span style="color: #666666">======================================================================</span>
FAIL: test_find <span style="color: #666666">(</span>__main__.SyncTest<span style="color: #666666">)</span>
</pre></div>


<hr />
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Traceback (most recent call last):
  File &quot;foo.py&quot;, line 49, in test_find
    ioloop.IOLoop.instance().start()
  File &quot;/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py&quot;, line 263, in start
    self._run_callback(timeout.callback)
  File &quot;/Users/emptysquare/.virtualenvs/blog/lib/python2.7/site-packages/tornado/ioloop.py&quot;, line 398, in _run_callback
    self.handle_callback_exception(callback)
  File &quot;foo.py&quot;, line 25, in handle_callback_exception
    raise exc_value
AssertionError: 42 != 17
</pre></div>


<hr />
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Ran 1 test in 1.002s

FAILED (failures=1)
</pre></div>


<p>Lovely. Change <code>async_calculate()</code> back to the correct version that
produces 42.</p>
<h1 id="an-even-better-way">An Even Better Way</h1>
<p>So we've verified that our test catches bugs in the calculation. But
what if we have a bug that prevents our callback from ever being called?
Add a return statement at the top of <code>async_calculate()</code> so we don't
execute the callback:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">async_calculate</span>(callback):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;</span>
<span style="color: #BA2121; font-style: italic">    @param callback:    A function taking params (result, error)</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #408080; font-style: italic"># Do something profoundly complex requiring non-blocking I/O, which</span>
    <span style="color: #408080; font-style: italic"># will complete in one second</span>
<span style="background-color: #ffffcc">    <span style="color: #008000; font-weight: bold">return</span>
</span>    ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>add_timeout(
        time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> <span style="color: #666666">1</span>,
        <span style="color: #008000; font-weight: bold">lambda</span>: callback(<span style="color: #666666">42</span>, <span style="color: #008000">None</span>)
    )
</pre></div>


<p>Now if we run the test, it hangs forever, because <code>IOLoop.stop()</code> is
never called. How can we write a test that asserts that the callback is
<strong>eventually</strong> executed? Never fear, I've written some code:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">AssertEventuallyTest</span>(unittest<span style="color: #666666">.</span>TestCase):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">super</span>(AssertEventuallyTest, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>setUp()

        <span style="color: #408080; font-style: italic"># Callbacks registered with assertEventuallyEqual()</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>assert_callbacks <span style="color: #666666">=</span> <span style="color: #008000">set</span>()

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">assertEventuallyEqual</span>(
        <span style="color: #008000">self</span>, expected, fn, msg<span style="color: #666666">=</span><span style="color: #008000">None</span>, timeout_sec<span style="color: #666666">=</span><span style="color: #008000">None</span>
    ):
        <span style="color: #008000; font-weight: bold">if</span> timeout_sec <span style="color: #AA22FF; font-weight: bold">is</span> <span style="color: #008000">None</span>:
            timeout_sec <span style="color: #666666">=</span> <span style="color: #666666">5</span>
        timeout_sec <span style="color: #666666">=</span> <span style="color: #008000">max</span>(timeout_sec, <span style="color: #008000">int</span>(os<span style="color: #666666">.</span>environ<span style="color: #666666">.</span>get(<span style="color: #BA2121">&#39;TIMEOUT_SEC&#39;</span>, <span style="color: #666666">0</span>)))
        start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
        loop <span style="color: #666666">=</span> ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()

        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>():
            <span style="color: #008000; font-weight: bold">try</span>:
                <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEqual(expected, fn(), msg)
                <span style="color: #408080; font-style: italic"># Passed</span>
                <span style="color: #008000">self</span><span style="color: #666666">.</span>assert_callbacks<span style="color: #666666">.</span>remove(callback)
                <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>assert_callbacks:
                    <span style="color: #408080; font-style: italic"># All asserts have passed</span>
                    loop<span style="color: #666666">.</span>stop()
            <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">AssertionError</span>:
                <span style="color: #408080; font-style: italic"># Failed -- keep waiting?</span>
                <span style="color: #008000; font-weight: bold">if</span> time<span style="color: #666666">.</span>time() <span style="color: #666666">-</span> start <span style="color: #666666">&amp;</span>lt; timeout_sec:
                    <span style="color: #408080; font-style: italic"># Try again in about 0.1 seconds</span>
                    loop<span style="color: #666666">.</span>add_timeout(time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> <span style="color: #666666">0.1</span>, callback)
                <span style="color: #008000; font-weight: bold">else</span>:
                    <span style="color: #408080; font-style: italic"># Timeout expired without passing test</span>
                    loop<span style="color: #666666">.</span>stop()
                    <span style="color: #008000; font-weight: bold">raise</span>

        <span style="color: #008000">self</span><span style="color: #666666">.</span>assert_callbacks<span style="color: #666666">.</span>add(callback)

        <span style="color: #408080; font-style: italic"># Run this callback on the next I/O loop iteration</span>
        loop<span style="color: #666666">.</span>add_callback(callback)
</pre></div>


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
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="background-color: #ffffcc"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">AsyncTest</span>(AssertEventuallyTest):
</span>    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">setUp</span>(<span style="color: #008000">self</span>):
        <span style="color: #408080; font-style: italic"># ... snip ...</span>

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">test_find</span>(<span style="color: #008000">self</span>):
        results <span style="color: #666666">=</span> []
        <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">callback</span>(result, error):
            <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;Got result&#39;</span>, result
            results<span style="color: #666666">.</span>append(result)

        async_calculate(callback)

<span style="background-color: #ffffcc">        <span style="color: #008000">self</span><span style="color: #666666">.</span>assertEventuallyEqual(
</span><span style="background-color: #ffffcc">            <span style="color: #666666">42</span>,
</span><span style="background-color: #ffffcc">            <span style="color: #008000; font-weight: bold">lambda</span>: results <span style="color: #AA22FF; font-weight: bold">and</span> results[<span style="color: #666666">0</span>]
</span><span style="background-color: #ffffcc">        )
</span>
        ioloop<span style="color: #666666">.</span>IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>start()
</pre></div>


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
    