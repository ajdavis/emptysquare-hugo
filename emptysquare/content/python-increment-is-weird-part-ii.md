+++
type = "post"
title = "Python's += Is Weird, Part II"
date = "2013-01-02T12:28:14"
description = "I wrote the other day about two things I think are weird about Python's += operator. In the comments, famed Twisted hacker Jean-Paul Calderone showed me something far, far weirder. This post is a record of me playing around and trying to [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
+++

<p>I wrote the other day about two things I think are weird about Python's <code>+=</code> operator. <a href="/python-increment-is-weird/#comment-752873234">In the comments</a>, famed Twisted hacker Jean-Paul Calderone showed me something far, far weirder. This post is a record of me playing around and trying to understand it.</p>
<p>To begin let's review what we know. Tuples are immutable in Python, so you can't increment a member of a tuple:</p>

{{<highlight python3>}}
>>> x = (0,)
>>> x
(0,)
>>> x[0] += 1
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
>>> x
(0,)
{{< / highlight >}}

<p>That's fine. But here's the bizarre behavior Jean-Paul showed me: if you put a list in a tuple and use the <code>+=</code> operator to extend the list, the increment succeeds <strong>and</strong> you get a <code>TypeError</code>!:</p>

{{<highlight python3>}}
>>> x = ([],)
>>> x
([],)
>>> x[0] += [1]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
>>> x
([1],)
{{< / highlight >}}

<p>The equivalent statement using <code>extend</code> succeeds without the <code>TypeError</code>:</p>

{{<highlight python3>}}
>>> x = ([],)
>>> x[0].extend([1])
>>> x
([1],)
{{< / highlight >}}

<p>So what's going on with <code>+=</code>? As always, looking at the bytecode is a good step toward understanding. I'll compile and disassemble the statement <code>x[0] += [1]</code>, and add some annotations:</p>

{{<highlight python3>}}
>>> import dis
>>> dis.dis(compile('x[0] += [1]', '<string>', 'exec'))
  1           0 LOAD_NAME                0 (x)
              3 LOAD_CONST               0 (0)
              6 DUP_TOPX                 2
              -- put x[0] on the stack --
              9 BINARY_SUBSCR            
             10 LOAD_CONST               1 (1)
             13 BUILD_LIST               1
              -- do the "+=" --
             16 INPLACE_ADD
             17 ROT_THREE           
              -- store new value in x[0] --
             18 STORE_SUBSCR
             19 LOAD_CONST               2 (None)
             22 RETURN_VALUE
{{< / highlight >}}

<p>(See Dan Crosta's <a href="http://late.am/post/2012/03/26/exploring-python-code-objects">Exploring Python Code Objects</a> for more on this technique).</p>
<p>Looks like the statement puts a reference to <code>x[0]</code> on the stack, makes the list <code>[1]</code> and uses it to successfully extend the list in <code>x[0]</code>. But then the statement executes <code>STORE_SUBSCR</code>, which calls the C function <code>PyObject_SetItem</code>, which checks if the object supports item assignment. In our case the object is a tuple, so <code>PyObject_SetItem</code> throws the <code>TypeError</code>. Mystery solved.</p>
<p>Is this a Python bug or just very surprising?</p>
