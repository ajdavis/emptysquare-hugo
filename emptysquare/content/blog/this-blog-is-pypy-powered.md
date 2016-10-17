+++
type = "post"
title = "This Blog is PyPy-powered"
date = "2012-08-30T15:25:04"
description = "My async MongoDB driver Motor now passes its test suite running in PyPy 1.9. To celebrate, I've switched my blog from CPython to PyPy! Update: I moved back to CPython 2.7. Although Motor and the rest of my blog's software appears to run [ ... ]"
"blog/category" = ["Mongo", "Motor", "Programming", "Python"]
"blog/tag" = ["pypy"]
enable_lightbox = false
thumbnail = "pypy-logo@240.png"
draft = false
legacyid = "503fbe105393740a96e9f26d"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pypy-logo.png" alt="PyPy Logo" title="pypy-logo.png" border="0"   /></p>
<p>My async MongoDB driver <a href="/motor/">Motor</a> now passes its test suite running in PyPy 1.9. To celebrate, I've switched my blog from CPython to PyPy!</p>
<p><strong>Update:</strong> I moved back to CPython 2.7. Although Motor and the rest of my blog's software appears to run stably on PyPy, it is very very slow. I have some suspicions about why but need to investigate.</p>
<p><strong>Another update:</strong> It has been pointed out to me on the Tornado mailing list that <a href="http://morepypy.blogspot.com/2011/11/pypy-17-widening-sweet-spot.html">greenlets make PyPy programs slow</a>:</p>
<blockquote>
<p>PyPy now comes with stackless features enabled by default. However, any loop using stackless features will interrupt
the JIT for now, so no real performance improvement for stackless-based programs. Contact pypy-dev for info how to 
help on removing this restriction.</p>
</blockquote>
    