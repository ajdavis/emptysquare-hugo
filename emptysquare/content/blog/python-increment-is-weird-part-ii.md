+++
type = "post"
title = "Python's += Is Weird, Part II"
date = "2013-01-02T12:28:14"
description = "I wrote the other day about two things I think are weird about Python's += operator. In the comments, famed Twisted hacker Jean-Paul Calderone showed me something far, far weirder. This post is a record of me playing around and trying to [ ... ]"
"blog/category" = ["Programming", "Python"]
"blog/tag" = []
enable_lightbox = false
draft = false
legacyid = "50e46ccb53937451d2fe28b2"
+++

<p>I wrote the other day about two things I think are weird about Python's <code>+=</code> operator. <a href="/blog/python-increment-is-weird/#comment-752873234">In the comments</a>, famed Twisted hacker Jean-Paul Calderone showed me something far, far weirder. This post is a record of me playing around and trying to understand it.</p>
<p>To begin let's review what we know. Tuples are immutable in Python, so you can't increment a member of a tuple:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x <span style="color: #666666">=</span> (<span style="color: #666666">0</span>,)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x
<span style="color: #888888">(0,)</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x[<span style="color: #666666">0</span>] <span style="color: #666666">+=</span> <span style="color: #666666">1</span>
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">1</span>, in &lt;module&gt;
<span style="color: #FF0000">TypeError</span>: &#39;tuple&#39; object does not support item assignment
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x
<span style="color: #888888">(0,)</span>
</pre></div>


<p>That's fine. But here's the bizarre behavior Jean-Paul showed me: if you put a list in a tuple and use the <code>+=</code> operator to extend the list, the increment succeeds <strong>and</strong> you get a <code>TypeError</code>!:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x <span style="color: #666666">=</span> ([],)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x
<span style="color: #888888">([],)</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x[<span style="color: #666666">0</span>] <span style="color: #666666">+=</span> [<span style="color: #666666">1</span>]
<span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;&lt;stdin&gt;&quot;</span>, line <span style="color: #666666">1</span>, in &lt;module&gt;
<span style="color: #FF0000">TypeError</span>: &#39;tuple&#39; object does not support item assignment
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x
<span style="color: #888888">([1],)</span>
</pre></div>


<p>The equivalent statement using <code>extend</code> succeeds without the <code>TypeError</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x <span style="color: #666666">=</span> ([],)
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x[<span style="color: #666666">0</span>]<span style="color: #666666">.</span>extend([<span style="color: #666666">1</span>])
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>x
<span style="color: #888888">([1],)</span>
</pre></div>


<p>So what's going on with <code>+=</code>? As always, looking at the bytecode is a good step toward understanding. I'll compile and disassemble the statement <code>x[0] += [1]</code>, and add some annotations:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">dis</span>
<span style="color: #000080; font-weight: bold">&gt;&gt;&gt; </span>dis<span style="color: #666666">.</span>dis(<span style="color: #008000">compile</span>(<span style="color: #BA2121">&#39;x[0] += [1]&#39;</span>, <span style="color: #BA2121">&#39;&lt;string&gt;&#39;</span>, <span style="color: #BA2121">&#39;exec&#39;</span>))
<span style="color: #888888">  1           0 LOAD_NAME                0 (x)</span>
<span style="color: #888888">              3 LOAD_CONST               0 (0)</span>
<span style="color: #888888">              6 DUP_TOPX                 2</span>
<span style="background-color: #ffffcc"><span style="color: #888888">              -- put x[0] on the stack --</span>
</span><span style="background-color: #ffffcc"><span style="color: #888888">              9 BINARY_SUBSCR            </span>
</span><span style="color: #888888">             10 LOAD_CONST               1 (1)</span>
<span style="color: #888888">             13 BUILD_LIST               1</span>
<span style="background-color: #ffffcc"><span style="color: #888888">              -- do the &quot;+=&quot; --</span>
</span><span style="background-color: #ffffcc"><span style="color: #888888">             16 INPLACE_ADD</span>
</span><span style="color: #888888">             17 ROT_THREE           </span>
<span style="background-color: #ffffcc"><span style="color: #888888">              -- store new value in x[0] --</span>
</span><span style="background-color: #ffffcc"><span style="color: #888888">             18 STORE_SUBSCR</span>
</span><span style="color: #888888">             19 LOAD_CONST               2 (None)</span>
<span style="color: #888888">             22 RETURN_VALUE     </span>
</pre></div>


<p>(See Dan Crosta's <a href="http://late.am/post/2012/03/26/exploring-python-code-objects">Exploring Python Code Objects</a> for more on this technique).</p>
<p>Looks like the statement puts a reference to <code>x[0]</code> on the stack, makes the list <code>[1]</code> and uses it to successfully extend the list in <code>x[0]</code>. But then the statement executes <code>STORE_SUBSCR</code>, which calls the C function <code>PyObject_SetItem</code>, which checks if the object supports item assignment. In our case the object is a tuple, so <code>PyObject_SetItem</code> throws the <code>TypeError</code>. Mystery solved.</p>
<p>Is this a Python bug or just very surprising?</p>
    