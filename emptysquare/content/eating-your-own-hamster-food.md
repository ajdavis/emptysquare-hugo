+++
type = "post"
title = "Eating Your Own Hamster Food"
date = "2012-10-01T17:04:38"
description = "If you aren't using your own libraries as you build them, you're skipping an essential test: not mainly for correctness or performance but for usability. (Using your software as you develop it is normally called \"eating your own [ ... ]"
category = ["Motor", "Programming", "Python"]
tag = ["dogfood"]
enable_lightbox = false
thumbnail = "hamster-food.jpg"
draft = false
+++

<p><img alt="Hamster Food" border="0" src="hamster-food.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="hamster-food.jpg"/></p>
<p><strong>Update</strong>: I've ported this blog from my own platform to Hugo, but I haven't changed my mind about this article: building my own blog platform with Motor was worth it.</p>
<p>If you aren't using your own libraries as you build them, you're skipping an essential test: not mainly for correctness or performance but for usability.</p>
<p>(Using your software as you develop it is normally called <a href="http://en.wikipedia.org/wiki/Eating_your_own_dog_food">"eating your own dogfood"</a>, but I don't have any dogs. Only hamsters. This is my dwarf hamster Rhoda.)</p>
<p>I develop <a href="http://motor.readthedocs.org/">Motor</a>, my asynchronous driver for Tornado and MongoDB, mainly with test-driven development: I think of an API Motor should implement, I write the test, and I make Motor pass the test. But I also <strong>use</strong> Motor in the <a href="https://github.com/ajdavis/motor-blog">blog platform</a> that runs this site. By using Motor, I discovered a few features that are absolutely essential for building a real application with it, which I never would have thought of otherwise:</p>
<p>• Opening a MotorConnection. My initial API for opening a connection to MongoDB with Motor was asynchronous:</p>

{{<highlight python3>}}
connection = motor.MotorConnection()
connection.open(my_callback)
{{< / highlight >}}

<p>That's fine for unittests. But as soon as I started building my blog it was clear it's a pain in the ass. There's no place in a Tornado application's usual startup sequence to do this step. So I made Motor open connections on demand, when you first use them.</p>
<p><a href="https://motor.readthedocs.io/en/stable/api-tornado/web.html#motor.web.GridFSHandler">GridFSHandler</a>. I recently completed Motor's methods for accessing GridFS, MongoDB's binary blob-storage system. Then I updated my blog to serve images from GridFS. And even though all the functionality I needed was complete, it was horribly inconvenient. So I wrote a <a href="https://motor.readthedocs.io/en/stable/api-tornado/gridfs.html#motor.motor_tornado.MotorGridOut.stream_to_handler"><code>stream_to_handler</code></a> method to pipe a GridFS file into a Tornado RequestHandler. Once I started using it, I figured it was still too low-level, so I reimplemented Tornado's <a href="http://www.tornadoweb.org/en/stable/web.html#tornado.web.StaticFileHandler">StaticFileHandler</a> on top of GridFS. Now serving static files straight from MongoDB is as easy as serving them from the file system.</p>
<p>I've sunk a lot of hours into building this site. I wondered if all the time was worth it. It's not like it has any special features I couldn't get from <a href="http://nikola.ralsina.com.ar/">Nikola</a> or <a href="http://docs.getpelican.com/en/3.0/index.html">Pelican</a>. Building a capable blog platform with code syntax highlighting, drafts, media, Disqus, Google Analytics, and so on took longer than I expected, and I'm still tinkering with it. But the investment pays off marvelously. By using Motor in a real-world application, even a small one, I've discovered serious usability problems my testing wouldn't reveal.</p>
