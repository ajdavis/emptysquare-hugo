+++
type = "post"
title = "Video, Slides, and Code About Async Python and MongoDB"
date = "2012-03-27T12:22:53"
description = "Video is now online from my webinar last week about Tornado and MongoDB. Alas, I didn't make the text on my screen big enough to be easily readable in the low-res video we recorded, so it'll be a little fuzzy for you. (Live and learn.) No [ ... ]"
categories = ["Programming", "Python", "Mongo"]
tags = ["tornado"]
enable_lightbox = false
draft = false
+++

<p><a href="http://www.10gen.com/presentations/webinar/Asynchronous-MongoDB-with-Python-and-Tornado">Video is now
online</a>
from my webinar last week about Tornado and MongoDB. Alas, I didn't make
the text on my screen big enough to be easily readable in the low-res
video we recorded, so it'll be a little fuzzy for you. (Live and learn.)
No worries, <a href="http://speakerdeck.com/u/mongodb/p/asynchronous-mongodb-with-python-and-tornado-a-jesse-jiryu-davis-python-evangelist">the slides are here in full-res
glory</a>
and <a href="https://github.com/ajdavis/chirp">the example code is on GitHub</a>.
It's a trivial Twitter clone called "chirp" which demonstrates using a
MongoDB capped collection as a sort of queue. The demo uses Tornado, a
MongoDB tailable cursor, and <a href="http://socket.io/">socket.io</a> to stream
new "chirps" from the capped collection to clients. I've implemented the
same demo app three times:</p>
<ul>
<li>Once with AsyncMongo, <a href="https://github.com/bitly/asyncmongo/pull/39">using features I've added in my AsyncMongo
    fork</a> to support
    tailable cursors.</li>
<li>Once with AsyncMongo and <a href="http://www.tornadoweb.org/en/latest/gen.html">Tornado's generator
    interface</a>.</li>
<li>And finally, using the <a href="https://github.com/mongodb/mongo-python-driver/">official
    PyMongo</a>, which
    reveals the tragic consequences of long-running MongoDB queries
    blocking Tornado's IOLoop.</li>
</ul>
    