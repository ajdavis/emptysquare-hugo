+++
type = "post"
title = "\"How Do Python Coroutines Work?\" Live-Coding Video From Open Source Bridge 2015"
date = "2015-10-06T23:23:58"
description = "The Open Source Bridge conference recently published this video of me building, in barely 30 minutes, a Python 3 async framework."
categories = ["Programming", "Python"]
tags = ["video"]
enable_lightbox = false
draft = false
+++

<iframe width="640" height="360" src="https://www.youtube.com/embed/GSk0tIjDT10?rel=0" frameborder="0" allowfullscreen></iframe>

<hr />
<p>The Open Source Bridge conference recently published this video of me building, in barely 30 minutes, a Python 3 async framework with non-blocking I/O and coroutines. <strong><a href="https://github.com/ajdavis/osbridge-2015">Here's the code I demonstrated.</a></strong></p>
<p>Python 3's new "asyncio" module is an efficient async framework similar to Node. But unlike Node, it emphasizes a modern idiom called "coroutines", rather than callbacks. Coroutines promise the best of two worlds: the efficiency of callbacks, but with a natural and robust coding style similar to synchronous programming.</p>
<p>In barely 30 minutes I live-code a Python 3 async framework. First, I show how an async framework uses non-blocking sockets, callbacks, and an event loop. This version of the framework is very efficient, but callbacks make a mess of the code. Therefore, I implement coroutines using Python generators and two classes called Future and Task, and update my little framework to use coroutines instead of callbacks.</p>
<p>The live-coding demo isn't just a magic trick: watch to see how simply a coroutine-based async framework can be implemented, and gain a deep understanding of this miraculous new programming idiom in the Python 3 standard library.</p>
<p>Although this video is the same material as <a href="/blog/i-live-coded-an-async-coroutine-framework-in-32-5-minutes/">my recent talk at PyGotham</a>, I think my delivery in this video from Open Source Bridge is superior to my PyGotham performance.</p>
<p>If you want to know coroutines deeply, however, a hurried video isn't the way to do it. I have <a href="/blog/links-for-how-python-coroutines-work/">a page full of links for further study on Python coroutines</a>, but my main advice is this: Spend an evening with <a href="/blog/500-lines-web-crawler-asyncio-coroutines/">the chapter Guido van Rossum and I wrote on the subject</a>; you'll be fast friends by the end.</p>
    