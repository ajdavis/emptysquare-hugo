+++
category = ['Python', 'Mongo', 'Programming', 'C']
date = '2016-11-17T12:15:26.287885'
description = 'In the MongoDB Engineering Journal I sing the ballad of my quest: making getaddrinfo concurrent on CPython.'
draft = false
tag = ['getaddrinfo']
thumbnail = 'scroll.jpg'
title = 'The Saga of Concurrent DNS: My Article in the MongoDB Engineering Journal'
type = 'post'
enable_lightbox = true
+++

{{< gallery path="mongodb-engineering-journal-getaddrinfo-article" >}}

Earlier this year I updated CPython to allow concurrent DNS resolution on Mac and BSD. My patch was trivial, but it took me weeks of archeological research to prove it was correct. In this article for the MongoDB Engineering Journal, I sing the ballad of my quest:

<div style="text-align:center; font-size: x-large; line-height: 1.1em; font-weight:bold">
<a href="https://engineering.mongodb.com/post/the-saga-of-concurrent-dns-in-python-and-the-defeat-of-the-wicked-mutex-troll/">The Saga of Concurrent DNS in Python,<br>and the Defeat of the Wicked Mutex Troll</a>
<br>
<br>
</div>

If silly fantasy stories are your thing, enjoy! If not, you can just read [the report on bugs.python.org](http://bugs.python.org/issue25924).
***

<span style="color: gray">Illustration by <a href="http://www.terrymarks.net/">Terry Marks</a></span>
