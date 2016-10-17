+++
type = "post"
title = "Python's += Is Weird"
date = "2013-01-01T12:04:40"
description = "Image: William Warby on Flickr Here's a Python gotcha I've hit often enough to merit a blog post: x += 1 is weird in Python. It's compiled roughly like x = x + 1, with two surprising consequences. One is this familiar pitfall: &gt;&gt;&gt; x = 0 [ ... ]"
"blog/category" = ["Programming", "Python"]
"blog/tag" = ["threading"]
enable_lightbox = false
thumbnail = "python@240.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="python.png" alt="Python" title="python.png" border="0"   /></p>
<p><a style="color: gray; font-style: italic" href="http://www.flickr.com/photos/wwarby/3279021508/">Image: William Warby on Flickr</a></p>
<p>Here's a Python gotcha I've hit often enough to merit a blog post: <code>x += 1</code> is weird in Python. It's compiled roughly like <code>x = x + 1</code>, with two surprising consequences. One is this familiar pitfall:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x <span style="color: #666666">=</span> <span style="color: #666666">0</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="color: #000080; font-weight: bold">... </span>    x <span style="color: #666666">+=</span> <span style="color: #666666">1</span>
<span style="color: #000080; font-weight: bold">... </span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>f()
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">1</span>, in &lt;module&gt;
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">2</span>, in f
<span style="color: #FF0000">UnboundLocalError</span>: local variable &#39;x&#39; referenced before assignment
</pre></div>


<p>The compiler thinks of <code>x += 1</code> similarly to <code>x = x + 1</code>, so it considers <code>x</code> to be a local variable bound in the scope of <code>f</code>. But <code>x</code> is referenced before it's assigned to. Let's look at the bytecode:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>dis<span style="color: #666666">.</span>dis(f)
<span style="color: #888888">  2           0 LOAD_FAST                0 (x)</span>
<span style="color: #888888">              3 LOAD_CONST               1 (1)</span>
<span style="color: #888888">              6 INPLACE_ADD         </span>
<span style="color: #888888">              7 STORE_FAST               0 (x)</span>
<span style="color: #888888">             10 LOAD_CONST               0 (None)</span>
<span style="color: #888888">             13 RETURN_VALUE   </span>
</pre></div>


<p>The first opcode, <code>LOAD_FAST</code>, fails to load <code>x</code> because it's not in scope. Obviously, we need to declare <code>global x</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">global</span> x
<span style="color: #000080; font-weight: bold">... </span>    x <span style="color: #666666">+=</span> <span style="color: #666666">1</span>
<span style="color: #000080; font-weight: bold">... </span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>dis<span style="color: #666666">.</span>dis(f)
<span style="color: #888888">  3           0 LOAD_GLOBAL              0 (x)</span>
<span style="color: #888888">              3 LOAD_CONST               1 (1)</span>
<span style="color: #888888">              6 INPLACE_ADD         </span>
<span style="color: #888888">              7 STORE_GLOBAL             0 (x)</span>
<span style="color: #888888">             10 LOAD_CONST               0 (None)</span>
<span style="color: #888888">             13 RETURN_VALUE    </span>
</pre></div>


<p>Now <code>LOAD_FAST</code> is replaced with <code>LOAD_GLOBAL</code>, which correctly locates <code>x</code>.</p>
<p>The second pitfall of <code>+=</code> is lost updates. If we run <code>f</code> ten thousand times in parallel, sometimes <code>x</code> is incremented less than ten thousand times:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">go</span>():
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">global</span> x
<span style="color: #000080; font-weight: bold">... </span>    x <span style="color: #666666">=</span> <span style="color: #666666">0</span>
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">f</span>():
<span style="color: #000080; font-weight: bold">... </span>        <span style="color: #008000; font-weight: bold">global</span> x
<span style="color: #000080; font-weight: bold">... </span>        x <span style="color: #666666">+=</span> <span style="color: #666666">1</span>
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">... </span>    ts <span style="color: #666666">=</span> [threading<span style="color: #666666">.</span>Thread(target<span style="color: #666666">=</span>f)
<span style="color: #000080; font-weight: bold">... </span>        <span style="color: #008000; font-weight: bold">for</span> _ <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">range</span>(<span style="color: #666666">10000</span>)]
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">for</span> t <span style="color: #AA22FF; font-weight: bold">in</span> ts:
<span style="color: #000080; font-weight: bold">... </span>        t<span style="color: #666666">.</span>start()
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">for</span> t <span style="color: #AA22FF; font-weight: bold">in</span> ts:
<span style="color: #000080; font-weight: bold">... </span>        t<span style="color: #666666">.</span>join()
<span style="color: #000080; font-weight: bold">...</span>
<span style="color: #000080; font-weight: bold">... </span>    <span style="color: #008000; font-weight: bold">print</span> x
<span style="color: #000080; font-weight: bold">... </span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>go()
<span style="color: #888888">10000</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>go()
<span style="color: #888888">10000</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>go()
<span style="color: #888888">9998</span>
</pre></div>


<p>Again, the problem is clear if we look at the bytecode. <code>f</code> is compiled as a series of opcodes that load the global integer referenced by <code>x</code> onto the stack, add 1 to it, and store the new integer back into <code>x</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>dis<span style="color: #666666">.</span>dis(f)
<span style="color: #888888">  3           0 LOAD_GLOBAL              0 (x)</span>
<span style="color: #888888">              3 LOAD_CONST               1 (1)</span>
<span style="color: #888888">              6 INPLACE_ADD         </span>
<span style="color: #888888">              7 STORE_GLOBAL             0 (x)</span>
<span style="color: #888888">             10 LOAD_CONST               0 (None)</span>
<span style="color: #888888">             13 RETURN_VALUE</span>
</pre></div>


<p>The interpreter can switch threads anywhere between <code>LOAD_FAST</code>, which loads the global value of <code>x</code> onto this thread's stack frame, and <code>STORE_FAST</code>, which saves it back to the global <code>x</code>.</p>
<p>Say <code>x</code> is 17 and two threads execute <code>f</code>. Thread A loads the integer 17 onto its stack, adds one to it, and gets interrupted. Now Thread B also loads 17 onto its stack and adds one. No matter the order the threads now complete, the final value of <code>x</code> will be 18, although we expect 19.</p>
<p>The solution is to protect <code>+=</code> statements with a <code>Lock</code>.</p>
    