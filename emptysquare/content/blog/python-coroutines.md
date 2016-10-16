+++
type = "post"
title = "Python Coroutines"
date = "2011-10-26T16:52:26"
description = "David Beazley's Curious Course on Coroutines and Concurrency in Python is the best coroutine tutorial I've seen. It makes an essential distinction between generators, from which you pull data, like this: def squares(): for i in [ ... ]"
categories = ["Programming", "Python"]
tags = []
enable_lightbox = false
draft = false
+++

<p>David Beazley's <a href="http://www.dabeaz.com/coroutines/index.html">Curious Course on Coroutines and
Concurrency</a> in Python is
the best coroutine tutorial I've seen.</p>
<p>It makes an essential distinction between <strong>generators</strong>, from which you <strong>pull</strong> data, like this:</p>

<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">squares</span>():
  <span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10</span>):
    <span style="color: #008000; font-weight: bold">yield</span> i <span style="color: #666666">*</span> i <span style="color: #408080; font-style: italic"># send data</span>

<span style="color: #008000; font-weight: bold">for</span> j <span style="color: #AA22FF; font-weight: bold">in</span> squares():
  <span style="color: #008000; font-weight: bold">print</span> j
</pre></div>


<p>... and <strong>coroutines</strong>, through which you <strong>push</strong> data, like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">line_printer</span>():
  buf <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;&#39;</span>
  <span style="color: #008000; font-weight: bold">try</span>:
    <span style="color: #008000; font-weight: bold">while</span> <span style="color: #008000">True</span>:
      buf <span style="color: #666666">+=</span> (<span style="color: #008000; font-weight: bold">yield</span>) <span style="color: #408080; font-style: italic"># receive data</span>
      parts <span style="color: #666666">=</span> buf<span style="color: #666666">.</span>split(<span style="color: #BA2121">&#39;</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&#39;</span>)
      <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">len</span>(parts) <span style="color: #666666">&gt;</span> <span style="color: #666666">1</span>:
        <span style="color: #408080; font-style: italic"># We&#39;ve received 1 or more new lines, print them</span>
        <span style="color: #008000; font-weight: bold">for</span> part <span style="color: #AA22FF; font-weight: bold">in</span> parts[:<span style="color: #666666">-1</span>]: <span style="color: #008000; font-weight: bold">print</span> part
        buf <span style="color: #666666">=</span> parts[<span style="color: #666666">-1</span>]
  <span style="color: #008000; font-weight: bold">except</span> <span style="color: #D2413A; font-weight: bold">GeneratorExit</span>:
    <span style="color: #408080; font-style: italic"># Someone has called close() on this generator, print</span>
    <span style="color: #408080; font-style: italic"># the last of the buffer</span>
    <span style="color: #008000; font-weight: bold">if</span> buf: <span style="color: #008000; font-weight: bold">print</span> buf

<span style="color: #408080; font-style: italic"># push random chars, and sometimes newlines, into the coroutine</span>
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">random</span>
coroutine <span style="color: #666666">=</span> line_printer()
coroutine<span style="color: #666666">.</span>next() <span style="color: #408080; font-style: italic"># start coroutine</span>
<span style="color: #008000; font-weight: bold">for</span> i <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">1000</span>):
  random_char <span style="color: #666666">=</span> <span style="color: #008000">chr</span>(random<span style="color: #666666">.</span>randint(<span style="color: #008000">ord</span>(<span style="color: #BA2121">&#39;a&#39;</span>), <span style="color: #008000">ord</span>(<span style="color: #BA2121">&#39;z&#39;</span>) <span style="color: #666666">+</span> <span style="color: #666666">1</span>))
  <span style="color: #008000; font-weight: bold">if</span> <span style="color: #008000">ord</span>(random_char) <span style="color: #666666">&gt;</span> <span style="color: #008000">ord</span>(<span style="color: #BA2121">&#39;z&#39;</span>):
    random_char <span style="color: #666666">=</span> <span style="color: #BA2121">&#39;</span><span style="color: #BB6622; font-weight: bold">\n</span><span style="color: #BA2121">&#39;</span>
  coroutine<span style="color: #666666">.</span>send(random_char)

coroutine<span style="color: #666666">.</span>close()
</pre></div>


<p>I plan to spend a lot of time with coroutines in the next few months, in particular seeing how they can simplify coding in asynchronous Python web frameworks.</p>
    