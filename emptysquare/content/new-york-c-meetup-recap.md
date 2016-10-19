+++
type = "post"
title = "New York C++ Meetup recap"
date = "2011-11-29T22:39:56"
description = "My gig, 10gen, sponsored the The New York C++ Developers meetup tonight. Roman Shtylman presented a just-the-facts primer on writing C++ extensions for Node.js. The use cases were: if you need to spawn threads, if you need to interface [ ... ]"
category = ["Programming"]
tag = []
enable_lightbox = false
thumbnail = "nodejs-light@240.png"
draft = false
legacyid = "207 http://emptysquare.net/blog/?p=207"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="nodejs-light.png" title="Node.js" /></p>
<p>My gig, 10gen, sponsored the <a href="http://www.meetup.com/nyccpp/events/16232776/">The New York C++ Developers meetup
tonight</a>. <a href="http://www.shtylman.com/">Roman
Shtylman</a> presented a just-the-facts primer on
writing C++ extensions for Node.js. The use cases were: if you need to
spawn threads, if you need to interface with an existing C or C++
library, or if you need to do CPU-intensive work and can prove that C++
is better at it than Javascript, then you could extend Node with C++.</p>
<p>From what I saw tonight it seems most of the challenge in writing an
extension is interfacing with V8 in general, not Node specifically.
While I have no pressing need to extend Node, <a href="http://shtylman.github.com/node-presentation/">reading Shtylman's
slides</a> from tonight gave
me a feel for how V8's internals work, which is its own reward.</p>
