+++
type = "post"
title = "My Two Talks at Open Source Bridge"
date = "2016-06-08T09:54:04"
description = "I'll speak about testing networked applications, and about mentoring young coders."
categories = ["Programming"]
tags = ["opensourcebridge"]
enable_lightbox = false
thumbnail = "trailway-coffee-shop.jpg"
draft = false
+++

<p><img alt="Description: 1930s postcard, drawing of old-fashioned roadside cafe. The sign says &quot;Trailway Coffee Shop: Fountain Lunches Dinners.&quot; In the background is a forested hill with blue sky." src="trailway-coffee-shop.jpg" /></p>
<p>My two favorite talks at Open Source Bridge this year aren't mine: they're <a href="/blog/my-two-favorite-talks-at-open-source-bridge-2016">my friends talks about accessibility, and about a parallel testing system written in Go</a>.</p>
<p>Nevertheless, I'm excited about the talks I'm going to give. I hope to see you there: <strong><a href="https://www.eventbrite.com/e/open-source-bridge-2016-registration-22759978709">Register for Open Source Bridge, June 21-24.</a></strong></p>
<hr />
<h2 id="black-pipe-testing-or-up-your-app-by-impersonating-a-database"><a href="http://opensourcebridge.org/proposals/1732">Black Pipe Testing, or "@#$! Up Your App by Impersonating a Database"</a></h2>
<p><img alt="Description: A man in tie, sweater, and hardhat is standing in the mouth of a huge pipe. He smiles into the camera, and reaches his arm up so his fingers just touch the top of the pipe, several feet above his head. The pipe is lying on the grass in a construction site. Behind him is a canal." src="pipe.jpg" /></p>
<p>A “black box” test sends input to your program and tests the output. But a networked application has I/O at two ends: the API and the network. A black box test can’t validate it, especially its error-handling. But a “black pipe” test can! Such a test talks to your code over the network at the same time as it tests the API. I’ll present a handy library for Black Pipe tests of MongoDB apps and advise you when to use it. I want you to write a library like it for your favorite DB, so we can all test our programs better!</p>
<h2 id="dodge-disasters-and-march-to-triumph-as-a-mentor"><a href="http://opensourcebridge.org/proposals/1768">Dodge Disasters and March to Triumph as a Mentor</a></h2>
<p><img alt="Description: a young man listens to an older, bearded man with white hair, who gestures as he speaks. Both wear white ancient Greek robes. The drawing is flat and stylized in a manner reminiscent of ancient Greek painting. The image is signed &quot;Fabisch&quot;." src="mentor.jpg" /></p>
<p>You can set yourself up for triumph as a mentor, by getting the prerequisites in place before your apprentice even arrives. You need to be a technical expert in what your apprentice is working on, the guiding visionary must be present, you need small clear goals, and you and your apprentice must be sympatico.</p>
<p>If you're a senior engineer, you must learn to mentor new hires. Besides, great mentors are critical to the careers of women and minorities in tech. The good news is, there's a method you can apply. Learn from me and march to mentorship triumph.</p>
<p><img alt="Description: uncropped version of the &quot;Trailway Coffee Shop&quot; postcard. The top portion of the image is the same as the first image in this article. Below in cursive is written &quot;Central Oregons Most Popular Family Restaurant&quot;, Hiway 20 &amp; Bond, Bend, Oregon. Open 24 Hours a Day. Below that, a colorful landscape: green pines and deciduous trees with golden leaves, on a green river slope. In the background is a wide river, a snow-capped mountain, and blue sky." src="trailway-coffee-shop-full.jpg" /></p>
<hr />
<p>Images:</p>
<ul>
<li>Trailway Coffee Shop, &quot;Central Oregon's most popular family restaurant&quot;, Hiway 20 &amp; Bond, Bend, Oregon. <a href="https://www.flickr.com/photos/boston_public_library/">1930s postcard courtesy Boston Public Library.</a></li>
<li>Cooling pipe for Saturn V rocket test system. <a href="https://www.flickr.com/photos/nasacommons/4861093477/">NASA, 1963.</a></li>
<li>Mentor and Telemachus. <a href="https://commons.wikimedia.org/wiki/File:Telemachus_and_Mentor1.JPG">Pablo E. Fabisch, illustration for "Aventuras de Telémaco", 1699.</a></li>
</ul>
    