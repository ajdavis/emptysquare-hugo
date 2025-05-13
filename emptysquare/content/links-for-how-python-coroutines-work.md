+++
type = "page"
title = "Links for \"How Python Coroutines Work\""
date = "2015-08-15T20:58:59"
description = "More information about my live-coding demonstration of a Python 3 async framework."
category = []
tag = []
enable_lightbox = false
thumbnail = "python.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="python.png" alt="Python" title="Python" /></p>
<p>At <a href="http://opensourcebridge.org/sessions/1582">Open Source Bridge</a> and <a href="https://pygotham.org/2015/talks/162/how-do-python-coroutines/">PyGotham</a> in 2015, and <a href="https://www.socallinuxexpo.org/scale/14x/presentations/how-do-python-coroutines-work">at SCALE14x</a>, I demonstrated that you can code a Python 3 async framework in under an hour. I start the demo by writing a callback-based async framework, built on non-blocking sockets and a simple event loop. Then I adapt the framework to use generator-based coroutines, which are cleaner than callbacks but still more efficient than threads for async I/O.</p>
<iframe width="640" height="360" src="https://www.youtube.com/embed/GSk0tIjDT10?rel=0" frameborder="0" allowfullscreen></iframe>

<hr />
<p><strong><a href="https://github.com/ajdavis/coroutines-demo">Here's the code I demonstrated.</a></strong></p>
<p>The material for this demo is adapted from <a href="https://github.com/aosabook/500lines/blob/master/crawler/crawler.markdown">a chapter I wrote with Guido van
Rossum for an upcoming book</a> in the Architecture of Open Source Applications
series.</p>
<p>Ben Darnell wrote a marvelous <a href="http://www.tornadoweb.org/en/stable/guide/coroutines.html">guide to coroutines in Tornado</a>. For advanced coroutine patterns see <a href="/refactoring-tornado-coroutines/">"Refactoring Tornado Coroutines"</a> and my <a href="http://www.tornadoweb.org/en/stable/coroutine.html">locks and queues for Tornado</a>.</p>
<hr />
<p><span style="color:gray"><a href="https://commons.wikimedia.org/wiki/File:PSM_V04_D272_Port_natal_python.jpg">Image: Popular Science, 1837.</a></span></p>
