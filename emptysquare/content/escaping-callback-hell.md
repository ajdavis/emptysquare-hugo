+++
type = "post"
title = "Escaping Callback Hell"
date = "2014-02-03T14:19:06"
description = "MongoDB's asynchronous interface will require no callbacks in the next release."
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = ["tornado"]
enable_lightbox = false
thumbnail = "orpheus.jpg"
draft = false
disqus_identifier = "52efeb405393747fe3c1cada"
disqus_url = "https://emptysqua.re/blog/52efeb405393747fe3c1cada/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="orpheus.jpg" alt="Orpheus, Antonio Canova" title="Orpheus, Antonio Canova" /></p>
<p>Even though he was the most charming singer in the world, Orpheus couldn't rescue Eurydice from hell. As he was leading her out of Hades he turned to call back to her, and lost her forever.</p>
<p>But you can rescue your Python programs from callback hell! In the coming month I plan to release <a href="https://motor.readthedocs.org/en/latest/">Motor</a> 0.2 with full support for Tornado coroutines. You'll get an asynchronous interface to MongoDB that uses coroutines and Futures, and there won't be a callback in sight. (Unless you want them.)</p>
<p><a href="http://joshaust.in/2014/02/it-requires-super-human-discipline-to-write-readable-code-in-callbacks/">Josh Austin at MaaSive.net is using a development version of Motor in production for the sake of its cleaner API</a>. I wouldn't recommend using unreleased code, but Josh has written a superb article justifying his choice. He details the evolution of Motor's asynchronous API and shows how the latest style is simpler and less error-prone.</p>
<p>Go read his article, and escape Orpheus's tragic fate.</p>
