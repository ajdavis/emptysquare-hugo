+++
type = "post"
title = "Python's += Is Weird"
date = "2013-01-01T12:04:40"
description = "Image: William Warby on Flickr Here's a Python gotcha I've hit often enough to merit a blog post: x += 1 is weird in Python. It's compiled roughly like x = x + 1, with two surprising consequences. One is this familiar pitfall: &gt;&gt;&gt; x = 0 [ ... ]"
category = ["Programming", "Python"]
tag = ["threading"]
enable_lightbox = false
thumbnail = "python.png"
draft = false
+++

<p><img alt="Python" border="0" src="python.png" style="display:block; margin-left:auto; margin-right:auto;" title="python.png"/></p>
<p><a href="http://www.flickr.com/photos/wwarby/3279021508/" style="color: gray; font-style: italic">Image: William Warby on Flickr</a></p>
<p>Here's a Python gotcha I've hit often enough to merit a blog post: <code>x += 1</code> is weird in Python. It's compiled roughly like <code>x = x + 1</code>, with two surprising consequences. One is this familiar pitfall:</p>

{{<highlight python3>}}
>>> x = 0
>>> def f():
...     x += 1
... 
>>> f()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 2, in f
UnboundLocalError: local variable 'x' referenced before assignment
{{< / highlight >}}

<p>The compiler thinks of <code>x += 1</code> similarly to <code>x = x + 1</code>, so it considers <code>x</code> to be a local variable bound in the scope of <code>f</code>. But <code>x</code> is referenced before it's assigned to. Let's look at the bytecode:</p>

{{<highlight python3>}}
>>> dis.dis(f)
  2           0 LOAD_FAST                0 (x)
              3 LOAD_CONST               1 (1)
              6 INPLACE_ADD         
              7 STORE_FAST               0 (x)
             10 LOAD_CONST               0 (None)
             13 RETURN_VALUE
{{< / highlight >}}

<p>The first opcode, <code>LOAD_FAST</code>, fails to load <code>x</code> because it's not in scope. Obviously, we need to declare <code>global x</code>:</p>

{{<highlight python3>}}
>>> def f():
...     global x
...     x += 1
... 
>>> dis.dis(f)
  3           0 LOAD_GLOBAL              0 (x)
              3 LOAD_CONST               1 (1)
              6 INPLACE_ADD         
              7 STORE_GLOBAL             0 (x)
             10 LOAD_CONST               0 (None)
             13 RETURN_VALUE
{{< / highlight >}}

<p>Now <code>LOAD_FAST</code> is replaced with <code>LOAD_GLOBAL</code>, which correctly locates <code>x</code>.</p>
<p>The second pitfall of <code>+=</code> is lost updates. If we run <code>f</code> ten thousand times in parallel, sometimes <code>x</code> is incremented less than ten thousand times:</p>

{{<highlight python3>}}
>>> def go():
...     global x
...     x = 0
...
...     def f():
...         global x
...         x += 1
...
...     ts = [threading.Thread(target=f)
...         for _ in range(10000)]
...
...     for t in ts:
...         t.start()
...
...     for t in ts:
...         t.join()
...
...     print x
... 
>>> go()
10000
>>> go()
10000
>>> go()
9998
{{< / highlight >}}

<p>Again, the problem is clear if we look at the bytecode. <code>f</code> is compiled as a series of opcodes that load the global integer referenced by <code>x</code> onto the stack, add 1 to it, and store the new integer back into <code>x</code>:</p>

{{<highlight python3>}}
>>> dis.dis(f)
  3           0 LOAD_GLOBAL              0 (x)
              3 LOAD_CONST               1 (1)
              6 INPLACE_ADD         
              7 STORE_GLOBAL             0 (x)
             10 LOAD_CONST               0 (None)
             13 RETURN_VALUE
{{< / highlight >}}

<p>The interpreter can switch threads anywhere between <code>LOAD_GLOBAL</code>, which loads the global value of <code>x</code> onto this thread's stack frame, and <code>STORE_GLOBAL</code>, which saves it back to the global <code>x</code>.</p>
<p>Say <code>x</code> is 17 and two threads execute <code>f</code>. Thread A loads the integer 17 onto its stack, adds one to it, and gets interrupted. Now Thread B also loads 17 onto its stack and adds one. No matter the order the threads now complete, the final value of <code>x</code> will be 18, although we expect 19.</p>
<p>The solution is to protect <code>+=</code> statements with a <code>Lock</code>.</p>
