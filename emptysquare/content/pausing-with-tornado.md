+++
type = "post"
title = "Pausing with Tornado"
date = "2012-04-20T21:26:41"
description = "Throwing this in my blog so I don't forget again. The way to sleep for a certain period of time using tornado.gen is: import tornado.web from tornado.ioloop import IOLoop from tornado import gen class [ ... ]"
category = ["Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
draft = false
legacyid = "430 http://emptysquare.net/blog/?p=430"
+++

<p>Throwing this in my blog so I don't forget again. The way to sleep for a
certain period of time using tornado.gen is:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">tornado.web</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.ioloop</span> <span style="color: #008000; font-weight: bold">import</span> IOLoop
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado</span> <span style="color: #008000; font-weight: bold">import</span> gen

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">MyHandler</span>(tornado<span style="color: #666666">.</span>web<span style="color: #666666">.</span>RequestHandler):
    <span style="color: #AA22FF">@tornado.web.asynchronous</span>
    <span style="color: #AA22FF">@gen.engine</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">get</span>(<span style="color: #008000">self</span>):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&quot;sleeping .... &quot;</span>)
        <span style="color: #408080; font-style: italic"># Do nothing for 5 sec</span>
        loop <span style="color: #666666">=</span> IOLoop<span style="color: #666666">.</span>instance()
        <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Task(loop<span style="color: #666666">.</span>add_timeout, time<span style="color: #666666">.</span>time() <span style="color: #666666">+</span> <span style="color: #666666">5</span>)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>write(<span style="color: #BA2121">&quot;I&#39;m awake!&quot;</span>)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>finish()
</pre></div>


<p>Simple once you see it, but for some reason this has been the hardest
for me to get used to.</p>
