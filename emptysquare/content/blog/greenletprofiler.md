+++
type = "post"
title = "GreenletProfiler, A Fast Python Profiler For Gevent"
date = "2014-01-27T12:11:20"
description = "A new profiler that can accurately analyze Gevent applications."
"blog/category" = ["Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "cProfile-bar-vs-foo@240.png"
draft = false
+++

<p>If you use Gevent, you know it's great for concurrency, but alas, none of the Python performance profilers work on Gevent applications. So I'm taking matters into my own hands. I'll show you how both cProfile and Yappi stumble on programs that use greenlets, and I'll demonstrate GreenletProfiler, my solution.</p>
<h1 id="cprofile-gets-confused-by-greenlets">cProfile Gets Confused by Greenlets</h1>
<p>I'll write a script that spawns two greenlets, then I'll profile the script to look for the functions that cost the most. In my script, the <code>foo</code> greenlet spins 20 million times. Every million iterations, it yields to Gevent's scheduler (the "hub"). The <code>bar</code> greenlet does the same, but it spins only half as many times.</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">cProfile</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">gevent</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">lsprofcalltree</span>

MILLION <span style="color: #666666">=</span> <span style="color: #666666">1000</span> <span style="color: #666666">*</span> <span style="color: #666666">1000</span>

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">foo</span>():
<span style="background-color: #ffffcc">    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">20</span> <span style="color: #666666">*</span> MILLION):
</span>        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> i <span style="color: #666666">%</span> MILLION:
            <span style="color: #408080; font-style: italic"># Yield to the Gevent hub.</span>
            gevent<span style="color: #666666">.</span>sleep(<span style="color: #666666">0</span>)

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">bar</span>():
<span style="background-color: #ffffcc">    <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10</span> <span style="color: #666666">*</span> MILLION):
</span>        <span style="color: #008000; font-weight: bold">if</span> <span style="color: #AA22FF; font-weight: bold">not</span> i <span style="color: #666666">%</span> MILLION:
            gevent<span style="color: #666666">.</span>sleep(<span style="color: #666666">0</span>)

profile <span style="color: #666666">=</span> cProfile<span style="color: #666666">.</span>Profile()
profile<span style="color: #666666">.</span>enable()

foo_greenlet <span style="color: #666666">=</span> gevent<span style="color: #666666">.</span>spawn(foo)
bar_greenlet <span style="color: #666666">=</span> gevent<span style="color: #666666">.</span>spawn(bar)
foo_greenlet<span style="color: #666666">.</span>join()
bar_greenlet<span style="color: #666666">.</span>join()

profile<span style="color: #666666">.</span>disable()
stats <span style="color: #666666">=</span> lsprofcalltree<span style="color: #666666">.</span>KCacheGrind(profile)
stats<span style="color: #666666">.</span>output(<span style="color: #008000">open</span>(<span style="color: #BA2121">&#39;cProfile.callgrind&#39;</span>, <span style="color: #BA2121">&#39;w&#39;</span>))
</pre></div>


<p>Let's pretend I'm a total idiot and I don't know why this program is slow. I profile it with cProfile, and convert its output with <a href="https://pypi.python.org/pypi/lsprofcalltree">lsprofcalltree</a> so I can view the profile in KCacheGrind. cProfile is evidently confused: it thinks <code>bar</code> took twice as long as <code>foo</code>, although the opposite is true:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="cProfile-bar-vs-foo.png" alt="CProfile bar vs foo" title="CProfile bar vs foo" /></p>
<p>cProfile also fails to count the calls to <code>sleep</code>. I'm not sure why cProfile's befuddlement manifests this particular way. If you understand it, please explain it to me in the comments. But it's not surprising that cProfile doesn't understand my script: cProfile is built to trace a single thread, so it assumes that if one function is called, and then a second function is called, that the first must have called the second. Greenlets defeat this assumption because the call stack can change entirely between one function call and the next.</p>
<h1 id="yappi-stumbles-over-greenlets">Yappi Stumbles Over Greenlets</h1>
<p>Next let's try <a href="https://code.google.com/p/yappi/">Yappi</a>, the excellent profiling package by Sumer Cip. Yappi has two big advantages over cProfile: it's built to trace multithreaded programs, and it can measure CPU time instead of wall-clock time. So maybe Yappi will do better than cProfile on my script? I run Yappi like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">yappi<span style="color: #666666">.</span>set_clock_type(<span style="color: #BA2121">&#39;cpu&#39;</span>)
yappi<span style="color: #666666">.</span>start(builtins<span style="color: #666666">=</span><span style="color: #008000">True</span>)

foo_greenlet <span style="color: #666666">=</span> gevent<span style="color: #666666">.</span>spawn(foo)
bar_greenlet <span style="color: #666666">=</span> gevent<span style="color: #666666">.</span>spawn(bar)
foo_greenlet<span style="color: #666666">.</span>join()
bar_greenlet<span style="color: #666666">.</span>join()

yappi<span style="color: #666666">.</span>stop()
stats <span style="color: #666666">=</span> yappi<span style="color: #666666">.</span>get_func_stats()
stats<span style="color: #666666">.</span>save(<span style="color: #BA2121">&#39;yappi.callgrind&#39;</span>, <span style="color: #008000">type</span><span style="color: #666666">=</span><span style="color: #BA2121">&#39;callgrind&#39;</span>)
</pre></div>


<p>Yappi thinks that when <code>foo</code> and <code>bar</code> call <code>gevent.sleep</code>, they indirectly call <code>Greenlet.run</code>, and eventually call themselves:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="yappi-call-graph.jpg" alt="Yappi call graph" title="Yappi call graph" /></p>
<p>This is true in some philosophical sense. When my greenlets sleep, they indirectly cause each other to be scheduled by the Gevent hub. But it's wrong to say they actually call themselves recursively, and it confuses Yappi's cost measurements: Yappi attributes most of the CPU cost of the program to Gevent's internal <code>Waiter.get</code> function. Yappi also, for some reason, thinks that <code>sleep</code> is called only once each by <code>foo</code> and <code>bar</code>, though it knows it was called 30 times in total.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="yappi-costs.png" alt="Yappi costs" title="Yappi costs" /></p>
<h1 id="greenletprofiler-groks-greenlets">GreenletProfiler Groks Greenlets</h1>
<p>Since Yappi is so great for multithreaded programs, I used it as my starting point for GreenletProfiler. Yappi's core tracing code is in C, for speed. The C code has a notion of a "context" which is associated with each thread. I added a hook to Yappi that lets me associate contexts with greenlets instead of threads. And voil&agrave;, the profiler understands my script! <code>foo</code> and <code>bar</code> are correctly measured as two-thirds and one-third of the script's total cost:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="GreenletProfiler-costs.png" alt="GreenletProfiler costs" title="GreenletProfiler costs" /></p>
<p>Unlike Yappi, GreenletProfiler also knows that <code>foo</code> calls <code>sleep</code> 20 times and <code>bar</code> calls <code>sleep</code> 10 times:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="GreenletProfiler-call-graph.png" alt="GreenletProfiler call graph" title="GreenletProfiler call graph" /></p>
<p>Finally, I know which functions to optimize because I have an accurate view of how my script executes.</p>
<h1 id="conclusion">Conclusion</h1>
<p>I can't take much credit for GreenletProfiler, because I stand on the shoulders of giants. Specifically I am standing on the shoulders of Sumer Cip, Yappi's author. But I hope it's useful to you. Install it with <code>pip install GreenletProfiler</code>, profile your greenletted program, and let me know how GreenletProfiler works for you.</p>
<ul>
<li><a href="http://greenletprofiler.readthedocs.org/en/stable/">GreenletProfiler documentation.</a></li>
<li><a href="https://pypi.python.org/pypi/GreenletProfiler">GreenletProfiler on PyPI.</a></li>
</ul>
    