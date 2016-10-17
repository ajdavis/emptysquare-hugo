+++
type = "post"
title = "Plop: Python Profiler With Call Graphs"
date = "2013-03-11T15:37:35"
description = "Ben Darnell's Plop project promises a low profiling impact on running systems, and shows pretty call graphs."
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "call-graph@240.png"
draft = false
legacyid = "513e327f53937424471d5661"
+++

<p>Tornado's maintainer Ben Darnell released a <a href="https://pypi.python.org/pypi/plop/">Python Low-Overhead Profiler</a> or "Plop" last year, and I'm just now playing with it. Unlike <a href="http://docs.python.org/2/library/profile.html#module-cProfile">cProfile</a>, which records every function call at great cost to the running process, Plop promises that "profile collection can be turned on and off in a live process with minimal performance impact."</p>
<p>A Plop <code>Collector</code> samples the process's call stack periodically (every 10 milliseconds by default) until you call <code>Collector.stop()</code>. Plop's profile viewer is a web application built on Tornado and d3.js, which uses a fun force-directed layout to display your process's call graph. You can use the demo scripts from Plop's <a href="https://github.com/bdarnell/plop">repo</a> to make an example profile:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="call-graph.png" alt="Call graph" title="call-graph.png" border="0"   /></p>
<p>Functions are shown as circles, sized according to the number of times they were executed and colored according to filename. Edges connect callers to callees. The visualization nearly freezes Firefox but runs well in Chrome.</p>
<p>Plop isn't going to replace cProfile and RunSnakeRun, but that's not its intention. Better to think of it as a lightweight complement to the heavier machinery: Plop is nice for visualizing call graphs (which RunSnakeRun does badly) and for sampling a live process in a performance-critical environment.</p>
    