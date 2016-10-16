+++
type = "post"
title = "Waiting For Multiple Events With Tornado"
date = "2014-03-11T09:16:42"
description = "How do you start multiple I/O operations with Tornado, and process results in the order they complete?"
categories = ["Programming", "Python"]
tags = ["tornado"]
enable_lightbox = false
draft = false
+++

<p>Recently I saw a question on Stack Overflow about waiting for multiple events with a Tornado coroutine, until <em>one</em> of the events completes. The inquirer wanted to do something like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any([future1, future2, future3])
</pre></div>


<p>If the middle future has resolved and the other two are still pending, the result should be like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">[<span style="color: #008000">None</span>, <span style="color: #BA2121">&quot;&lt;some result&gt;&quot;</span>, <span style="color: #008000">None</span>]
</pre></div>


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
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Any</span>(Future):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, futures):
        <span style="color: #008000">super</span>(Any, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>__init__()
        <span style="color: #008000">self</span><span style="color: #666666">.</span>futures <span style="color: #666666">=</span> futures
        <span style="color: #008000; font-weight: bold">for</span> future <span style="color: #AA22FF; font-weight: bold">in</span> futures:
            <span style="color: #408080; font-style: italic"># done_callback is defined just below.</span>
            future<span style="color: #666666">.</span>add_done_callback(<span style="color: #008000">self</span><span style="color: #666666">.</span>done_callback)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done_callback</span>(<span style="color: #008000">self</span>, future):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Called when any future resolves.&quot;&quot;&quot;</span>
        <span style="color: #008000; font-weight: bold">try</span>:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>set_result(<span style="color: #008000">self</span><span style="color: #666666">.</span>make_result())
        <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">Exception</span> <span style="color: #008000; font-weight: bold">as</span> e:
            <span style="color: #008000">self</span><span style="color: #666666">.</span>set_exception(e)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">make_result</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;A list of results.</span>

<span style="color: #BA2121; font-style: italic">        Includes None for each pending future, and a result for each</span>
<span style="color: #BA2121; font-style: italic">        resolved future. Raises an exception for the first future</span>
<span style="color: #BA2121; font-style: italic">        that has an exception.</span>
<span style="color: #BA2121; font-style: italic">        &quot;&quot;&quot;</span>
        <span style="color: #008000; font-weight: bold">return</span> [f<span style="color: #666666">.</span>result() <span style="color: #008000; font-weight: bold">if</span> f<span style="color: #666666">.</span>done() <span style="color: #008000; font-weight: bold">else</span> <span style="color: #008000">None</span>
                <span style="color: #008000; font-weight: bold">for</span> f <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>futures]

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">clear</span>(<span style="color: #008000">self</span>):
        <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Break reference cycle with any pending futures.&quot;&quot;&quot;</span>
        <span style="color: #008000">self</span><span style="color: #666666">.</span>futures <span style="color: #666666">=</span> <span style="color: #008000">None</span>
</pre></div>


<p>Here's an example use of Any:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">delayed_msg</span>(seconds, msg):
    <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>add_timeout,
                   time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> seconds)
    <span style="color: #008000; font-weight: bold">raise</span> gen<span style="color: #666666">.</span>Return(msg)


<span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
    future1 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">2</span>, <span style="color: #BA2121">&#39;2&#39;</span>)
    future2 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">3</span>, <span style="color: #BA2121">&#39;3&#39;</span>)
    future3 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;1&#39;</span>)

    <span style="color: #408080; font-style: italic"># future3 will resolve first.</span>
<span style="background-color: #ffffcc">    results <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any([future1, future2, future3])
</span>    end <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;finished in </span><span style="color: #BB6688; font-weight: bold">%.1f</span><span style="color: #BA2121"> sec: </span><span style="color: #BB6688; font-weight: bold">%r</span><span style="color: #BA2121">&quot;</span> <span style="color: #666666">%</span> (end <span style="color: #666666">-</span> start, results)

    <span style="color: #408080; font-style: italic"># Wait for any of the remaining futures.</span>
<span style="background-color: #ffffcc">    results <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any([future1, future2])
</span>    end <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
    <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;finished in </span><span style="color: #BB6688; font-weight: bold">%.1f</span><span style="color: #BA2121"> sec: </span><span style="color: #BB6688; font-weight: bold">%r</span><span style="color: #BA2121">&quot;</span> <span style="color: #666666">%</span> (end <span style="color: #666666">-</span> start, results)

IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>run_sync(f)
</pre></div>


<p>As expected, this prints:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">finished in 1.0 sec: [None, None, &#39;1&#39;]
finished in 2.0 sec: [&#39;2&#39;, None]
</pre></div>


<p>But you can see there are some complications with this approach. For one thing, if you want to wait for the <em>rest</em> of the futures after the first one resolves, it's complicated to construct the list of still-pending futures. I suppose you could do:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">futures <span style="color: #666666">=</span> [future1, future2, future3]
results <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any(f <span style="color: #008000; font-weight: bold">for</span> f <span style="color: #AA22FF; font-weight: bold">in</span> futures
                    <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> f<span style="color: #666666">.</span>done())
</pre></div>


<p>Not pretty. And not correct, either! There's a race condition: if a future is resolved in between consecutive executions of this code, you may never receive its result. On the first call, you get the result of some other future that resolves faster, but by the time you're constructing the list to pass to the second Any, your future is now "done" and you omit it from the list.</p>
<p>Another complication is the reference cycle: Any refers to each future, which refers to a callback which refers back to Any. For prompt garbage collection, you should call <code>clear()</code> on Any before it goes out of scope. This is very awkward.</p>
<p>Additionally, you can't distinguish between a pending future, and a future that resolved to None. You'd need a special sentinel value distinct from None to represent a pending future.</p>
<p>The final complication is the worst. If multiple futures are resolved and some of them have exceptions, there's no obvious way for Any to communicate all that information to you. Mixing exceptions and results in a list would be perverse.</p>
<h1 id="a-better-way">A Better Way</h1>
<p>Fortunately, there's a better way. We can make Any return just the first future that resolves, instead of a list of results:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">Any</span>(Future):
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, futures):
        <span style="color: #008000">super</span>(Any, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>__init__()
        <span style="color: #008000; font-weight: bold">for</span> future <span style="color: #AA22FF; font-weight: bold">in</span> futures:
            future<span style="color: #666666">.</span>add_done_callback(<span style="color: #008000">self</span><span style="color: #666666">.</span>done_callback)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">done_callback</span>(<span style="color: #008000">self</span>, future):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>set_result(future)
</pre></div>


<p>The reference cycle is gone, and the exception-handling question is answered: The Any class returns the whole future to you, instead of its result or exception. You can inspect it as you like.</p>
<p>It's also easy to wait for the remaining futures after some are resolved:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
    future1 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">2</span>, <span style="color: #BA2121">&#39;2&#39;</span>)
    future2 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">3</span>, <span style="color: #BA2121">&#39;3&#39;</span>)
    future3 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;1&#39;</span>)

    futures <span style="color: #666666">=</span> <span style="color: #008000">set</span>([future1, future2, future3])
    <span style="color: #008000; font-weight: bold">while</span> futures:
        resolved <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any(futures)
        end <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;finished in </span><span style="color: #BB6688; font-weight: bold">%.1f</span><span style="color: #BA2121"> sec: </span><span style="color: #BB6688; font-weight: bold">%r</span><span style="color: #BA2121">&quot;</span> <span style="color: #666666">%</span> (
            end <span style="color: #666666">-</span> start, resolved<span style="color: #666666">.</span>result())
        futures<span style="color: #666666">.</span>remove(resolved)
</pre></div>


<p>As desired, this prints:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">finished in 1.0 sec: &#39;1&#39;
finished in 2.0 sec: &#39;2&#39;
finished in 3.0 sec: &#39;3&#39;
</pre></div>


<p>There's no race condition now. You can't miss a result, because you don't remove a future from the list unless you've received its result.</p>
<h1 id="exceptions">Exceptions</h1>
<p>To test the exception-handling behavior, let's make a function that raises an exception after a delay:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">delayed_exception</span>(seconds, msg):
    <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(IOLoop<span style="color: #666666">.</span>current()<span style="color: #666666">.</span>add_timeout,
                   time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> seconds)
    <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #D2413A; font-weight: bold">Exception</span>(msg)
</pre></div>


<p>Now, instead of returning a result, one of our futures will raise an exception:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.coroutine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    start <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
    future1 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">2</span>, <span style="color: #BA2121">&#39;2&#39;</span>)
    <span style="color: #408080; font-style: italic"># Exception!</span>
<span style="background-color: #ffffcc">    future2 <span style="color: #666666">=</span> delayed_exception(<span style="color: #666666">3</span>, <span style="color: #BA2121">&#39;3&#39;</span>)
</span>    future3 <span style="color: #666666">=</span> delayed_msg(<span style="color: #666666">1</span>, <span style="color: #BA2121">&#39;1&#39;</span>)

    futures <span style="color: #666666">=</span> <span style="color: #008000">set</span>([future1, future2, future3])
    <span style="color: #008000; font-weight: bold">while</span> futures:
        resolved <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> Any(futures)
        end <span style="color: #666666">=</span> time<span style="color: #666666">.</span>time()
        <span style="color: #008000; font-weight: bold">try</span>:
            outcome <span style="color: #666666">=</span> resolved<span style="color: #666666">.</span>result()
<span style="background-color: #ffffcc">        <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">Exception</span> <span style="color: #008000; font-weight: bold">as</span> e:
</span><span style="background-color: #ffffcc">            outcome <span style="color: #666666">=</span> e
</span>
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&quot;finished in </span><span style="color: #BB6688; font-weight: bold">%.1f</span><span style="color: #BA2121"> sec: </span><span style="color: #BB6688; font-weight: bold">%r</span><span style="color: #BA2121">&quot;</span> <span style="color: #666666">%</span> (
            end <span style="color: #666666">-</span> start, outcome)
        futures<span style="color: #666666">.</span>remove(resolved)
</pre></div>


<p>Now, the script prints:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">finished in 1.0 sec: &#39;1&#39;
finished in 2.0 sec: &#39;2&#39;
finished in 3.0 sec: Exception(&#39;3&#39;,)
</pre></div>


<h1 id="conclusion">Conclusion</h1>
<p>It took a bit of thinking, but our final Any class is simple. It lets you launch many concurrent operations and process them in the order they complete. Not bad.</p>
    