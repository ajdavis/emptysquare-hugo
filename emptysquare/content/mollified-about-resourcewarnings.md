+++
type = "post"
title = "Mollified About ResourceWarnings"
date = "2012-06-01T09:02:45"
description = "Last month I griped about ResourceWarnings in Python 3, arguing they're a useless irritation in a language that can clean up resources automatically. Python core developer Nick Coghlan responded in the comments and I understand the [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
disqus_identifier = "580 http://emptysquare.net/blog/?p=580"
disqus_url = "https://emptysqua.re/blog/580 http://emptysquare.net/blog/?p=580/"
+++

<p>Last month <a href="/blog/against-resourcewarnings-in-python-3/">I griped about ResourceWarnings in Python
3</a>, arguing they're a
useless irritation in a language that can clean up resources
automatically. Python core developer <a href="http://www.boredomandlaziness.org/">Nick
Coghlan</a> responded in the comments
and I understand the choice now.</p>
<p>Nick explains that ResourceWarnings reveal problems that would make the
Python standard library inefficient running in PyPy. A resource like a
socket can clean itself up promptly in CPython, but now that it issues a
ResourceWarning when it isn't explicitly closed, the socket helps
library authors prepare for PyPy, in which resources are <strong>not</strong>
promptly cleaned up. If I decide that lazy cleanup is ok, I can avoid
ResourceWarnings by using a <a href="http://docs.python.org/library/weakref.html#weakref.ref">weakref
callback</a> to
close the resource before it's deleted, whenever that happens.</p>
<p>Nick also pointed out that ResourceWarnings are off by default in normal
Python programs—I just saw them all the time because I usually run my
code in <code>nosetest</code>.</p>
<p><a href="/blog/against-resourcewarnings-in-python-3/#comment-514722438">Read our full discussion in the
comments</a>.</p>
<p>Props to Nick for taking the time to explain.</p>
