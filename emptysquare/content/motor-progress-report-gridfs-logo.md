+++
type = "post"
title = "Motor Progress Report: GridFS, Logo"
date = "2012-09-27T22:49:07"
description = "Two big updates to Motor, my non-blocking driver for MongoDB and Tornado. First, my friend Musho Rodney Alan Greenblat made a logo. Motor may or may not be ready for prime time, but it looks ready. Second, I implemented GridFS. GridFS is a [ ... ]"
category = ["Mongo", "Motor", "Programming", "Python"]
tag = ["gridfs"]
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "506510235393744109d6d2c0"
disqus_url = "https://emptysqua.re/blog/506510235393744109d6d2c0/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p>Two big updates to <a href="http://motor.readthedocs.org/">Motor</a>, my non-blocking driver for MongoDB and Tornado.</p>
<p>First, my friend <a href="http://www.whimsyload.com/">Musho Rodney Alan Greenblat</a> made a logo. Motor may or may not be ready for prime time, but it <strong>looks</strong> ready.</p>
<p>Second, I implemented GridFS. GridFS is a spec for storing blobs of data in MongoDB of arbitrary size and contents; it was Motor's last missing feature. You can see the <a href="http://motor.readthedocs.org/en/stable/api/gridfs.html">API documentation</a> and <a href="http://motor.readthedocs.org/en/stable/examples/gridfs.html">example code</a> for using GridFS with Motor.</p>
<p>I've been inspired by Christian Kvalheim's <a href="http://mongodb.github.com/node-mongodb-native/api-articles/nodekoarticle1.html">thorough, example-driven documentation for his MongoDB Node.js driver</a>. I want Motor to be equally easy to pick up, with an obvious example for each basic task. I started with examples for GridFS, but I'll go back and apply the same principle to the rest of Motor's docs soon.</p>
<p>Besides the big updates there's also a small one: the time has finally come to factor out some irritatingly repetitive code in the mechanisms Motor uses to wrap PyMongo, so I rewrote them and trimmed off a hundred lines. The tests all pass, but there may be dragons lurking in the changes. Update with your eyes open.</p>
<p>As always, let me know how Motor's working for you: <a href="mailto:jesse@10gen.com">jesse@10gen.com</a>.</p>
