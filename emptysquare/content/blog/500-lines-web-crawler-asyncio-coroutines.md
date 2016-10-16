+++
type = "post"
title = "Book Chapter: \"A Web Crawler With asyncio Coroutines\""
date = "2015-09-15T10:31:41"
description = "The chapter I wrote with Guido van Rossum about Python async coroutines is available now, as an early access release before publication."
categories = ["Programming", "Python"]
tags = []
enable_lightbox = false
thumbnail = "habitat-montreal.jpg"
draft = false
+++

<p><a href="https://www.flickr.com/photos/emptysquare/2645433948/in/photolist-52Lxm9-52LtHb-52FF5c-52KSB5-wKtf8"><img style="display:block; margin-left:auto; margin-right:auto;" src="habitat-montreal.jpg" alt="Habitat Montr&eacute;al" title="Habitat Montr&eacute;al" /></a></p>
<p><a href="http://aosabook.org/en/500L/a-web-crawler-with-asyncio-coroutines.html">The chapter I wrote with Guido van Rossum about Python async coroutines is available now</a>, as an early access release before publication.</p>
<p>The chapter is part of "500 Lines or Less," the latest book in the eminent <a href="http://aosabook.org/blog/pages/about.html">Architecture of Open Source Applications</a> series. Once published the book will be available for free download, and for purchase&mdash;proceeds benefit <a href="https://www.amnesty.org/">Amnesty International</a>.</p>
<p>Our chapter is titled "A Web Crawler With asyncio Coroutines". In less than 500 lines of Python, we demonstrate the bones of an async framework similar to asyncio, the framework in Python 3's standard library.</p>
<p>To start, we explain what "async" means and what sort of applications it optimizes. Since a web crawler&mdash;a program that fetches all the pages on a site&mdash;is ideal for async, we build a web crawler together as our example program.</p>
<p>The chapter proceeds in three stages. First, we show an async event loop and sketch a crawler that uses the event loop with callbacks: it is very efficient, but extending it to more complex problems would lead to unmanageable spaghetti code. Second, therefore, we show that Python coroutines are an efficient and extensible alternative to callbacks. We implement simple coroutines in Python using generator functions. In the third stage, we use the full-featured coroutines already available in Python's standard "asyncio" library, and show how to coordinate coroutines using an async queue.</p>
<p>I'm honored to work with Guido and bring to completion this project he began last year. My gratitude goes to the editor Michael DiBernardo for inviting me to co-author this chapter, to Ben Darnell and Pete Soderling for their insightful editing, to Andrew Svetlov for his timely technical contributions, and Brett Cannon for meticulously reviewing and patching the early access release.</p>
    