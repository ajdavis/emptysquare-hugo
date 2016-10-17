+++
type = "post"
title = "YieldPoints: simple extensions to tornado.gen"
date = "2012-12-07T18:42:19"
description = "I affectionately introduce YieldPoints, my littlest project yet. It's just some simple extensions to Tornado's gen module. The cutest example of what you can do with YieldPoints is the WaitAny class, which lets you begin multiple [ ... ]"
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["tornado"]
enable_lightbox = false
thumbnail = "yield@240.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="yield.png" alt="YieldPoints" title="yield.png" border="0"   /></p>
<p>I affectionately introduce YieldPoints, my littlest project yet. It's just some simple extensions to <a href="http://www.tornadoweb.org/en/latest/gen.html">Tornado's gen module</a>.</p>
<p>The cutest example of what you can do with YieldPoints is the WaitAny class, which lets you begin multiple asynchronous tasks and handle their results in the order they complete:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #AA22FF">@gen.engine</span>
<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
    callback0 <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Callback(<span style="color: #666666">0</span>)
    callback1 <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> gen<span style="color: #666666">.</span>Callback(<span style="color: #666666">1</span>)

    <span style="color: #408080; font-style: italic"># Fire callback1 soon, callback0 later</span>
    IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>add_timeout(
        timedelta(seconds<span style="color: #666666">=0.1</span>), partial(callback1, <span style="color: #BA2121">&#39;foo&#39;</span>))

    IOLoop<span style="color: #666666">.</span>instance()<span style="color: #666666">.</span>add_timeout(
        timedelta(seconds<span style="color: #666666">=0.2</span>), partial(callback0, <span style="color: #BA2121">&#39;bar&#39;</span>))

    keys <span style="color: #666666">=</span> <span style="color: #008000">set</span>([<span style="color: #666666">0</span>, <span style="color: #666666">1</span>])
    <span style="color: #008000; font-weight: bold">while</span> keys:
        key, result <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> yieldpoints<span style="color: #666666">.</span>WaitAny(keys)
        <span style="color: #008000; font-weight: bold">print</span> <span style="color: #BA2121">&#39;key:&#39;</span>, key, <span style="color: #BA2121">&#39;, result:&#39;</span>, result
        keys<span style="color: #666666">.</span>remove(key)
</pre></div>


<p>More <a href="http://yieldpoints.readthedocs.org/">examples are in the docs</a>: you can use WithTimeout to wrap any callback in a timeout, and use Cancel or CancelAll to decline to wait for a callback you registered earlier. There's an adorable <a href="https://yieldpoints.readthedocs.org/en/latest/examples/index.html">extended example</a> that uses my library to start downloading multiple URLs at once, and process the results in the order received.</p>
<p>Further reading:</p>
<p><a href="http://yieldpoints.readthedocs.org/">YieldPoints on Read the Docs</a></p>
<p><a href="https://github.com/ajdavis/yieldpoints">YieldPoints on Github</a></p>
<p><a href="http://pypi.python.org/pypi/yieldpoints/">YieldPoints on PyPI</a></p>
    