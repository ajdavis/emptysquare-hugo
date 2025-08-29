+++
type = "post"
title = "This Site Is Built With Lektor"
date = "2016-01-10T13:48:20"
description = "I've moved to Armin Ronacher's new static site generator."
category = ["Python", "Programming"]
tag = ["lektor"]
enable_lightbox = false
thumbnail = "magpie.jpg"
draft = false
+++

<p><img alt="" src="magpie.jpg" /></p>
<p>In the last week I've ported this blog and my /photography to Armin Ronacher's new static site generator, <a href="http://getlektor.com">Lektor</a>.</p>
<p>In the beginning, I blogged on WordPress. WordPress is a wonder of the world. It <a href="http://venturebeat.com/2015/11/08/wordpress-now-powers-25-of-the-web/">powers a quarter of the web</a>. The <a href="http://opensourcebridge.org/sessions/1419">WordPress developers have figured out how to auto-update their millions of users</a> (please follow that link, the story is fascinating), and this auto-updating makes it a remarkably secure and robust platform. But I'm somehow not smart enough to make WordPress fast.</p>
<p>For the last few years the site has run my homegrown Python blog platform, <a href="https://github.com/ajdavis/motor-blog">Motor-Blog</a>. In Motor-Blog I painstakingly implemented the features I needed. It was a tremendous investment, but I wouldn't give up what I learned. As I wrote in <a href="../eating-your-own-hamster-food/">Eating Your Own Hamster Food</a>, it was an invaluable experience to write my own blog software on top of MongoDB, Tornado, and my async Python driver.</p>
<p>Motor-Blog is a hotrod: I built it in my garage, it lacks basic features, and it's fast and overpowered and expensive. I ran it on four Tornado processes, connected to a MongoDB instance, load-balanced by NGinx, all running on one big Rackspace box. That's a pricey way to run a simple website. And, continuing the hotrod analogy, I was the only one who knew how it worked. I liked tinkering with it on weekends, but it was an absurd vehicle just to drive to the grocery store.</p>
<p>So when I heard that Armin Ronacher, the craftsman of Flask and Jinja, had announced a new static generator I decided to play around with it. I spent a day over Christmas break seeing how much of my site I could port to Lektor. I intended to also test-drive the more mature generators like Pelican and Octopress, but tinkering with Lektor has been so much fun I decided to commit to it. I'm an incorrigible tinkerer.</p>
<p>I've had the opportunity, as an early adopter, to watch Armin accelerate Lektor's community from zero to sixty in its first weeks. There are already <a href="https://github.com/lektor/lektor/graphs/contributors">16 contributors</a> to the Lektor core, 20 to the Lektor documentation site, and <a href="https://www.getlektor.com/docs/plugins/list/">a half-dozen plugins by people besides Armin</a>. I don't think this is just good luck. Armin has been smart about building Lektor's community from the outset; I plan to ask him some questions and write an article about this in a couple weeks.</p>
<hr />
<p><a href="http://www.oldbookillustrations.com/illustrations/grandville-magpie-writer/">Image: Mrs. Magpie</a></p>
