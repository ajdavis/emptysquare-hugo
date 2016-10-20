+++
type = "post"
title = "Announcing Motor 0.2 release candidate"
date = "2014-04-04T22:32:45"
description = "Motor 0.2 rc0 is a huge change from 0.1, reflecting big improvements in PyMongo, Tornado, and MongoDB itself."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "533f58dc53937441561c1131"
disqus_url = "https://emptysqua.re/blog/533f58dc53937441561c1131/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p>I'm excited to offer you Motor 0.2, release candidate zero. <a href="https://motor.readthedocs.org/en/latest/">Motor</a> is my non-blocking driver for MongoDB and Tornado.</p>
<p>The changes from Motor 0.1 to 0.2 are epochal. They were motivated primarily by three events:</p>
<ul>
<li>Motor wraps PyMongo, and PyMongo has improved substantially.</li>
<li>MongoDB 2.6 is nearly done, and Motor has added features to support it.</li>
<li>Tornado's support for coroutines and for non-blocking DNS has improved, and Motor 0.2 takes advantage of this.</li>
</ul>
<p><a href="http://motor.readthedocs.org/en/latest/changelog.html">Please read the changelog before upgrading</a>. There are backwards-breaking API changes; you <strong>must</strong> update your code. I tried to make the instructions clear and the immediate effort small. A summary of the changes is in my post, <a href="/motor-progress-report-the-road-to-0-2/">"the road to 0.2"</a>.</p>
<p>Once you're done reading, upgrade:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install pymongo==2.7
pip install https://github.com/mongodb/motor/archive/0.2rc0.zip
</pre></div>


<p>The owner's manual is on ReadTheDocs. At the time of this writing, Motor 0.2's docs are in the "latest" branch:</p>
<blockquote>
<p><a href="http://motor.readthedocs.org/en/latest/">http://motor.readthedocs.org/en/latest/</a></p>
</blockquote>
<p>...and Motor 0.1's docs are in "stable":</p>
<blockquote>
<p><a href="http://motor.readthedocs.org/en/stable/">http://motor.readthedocs.org/en/stable/</a></p>
</blockquote>
<p>Enjoy! If you find a bug or want a feature, <a href="https://jira.mongodb.org/browse/MOTOR">report it</a>. If I don't hear of any bugs in the next week I'll make the release official.</p>
<p>In any case, <a href="https://twitter.com/jessejiryudavis">tweet me</a> if you're building something nifty with Motor. I want to hear from you.</p>
