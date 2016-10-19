+++
type = "post"
title = "Motor Progress Report"
date = "2012-08-29T23:54:04"
description = ""
category = ["Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "503ee3dc5393744800000000"
disqus_url = "https://emptysqua.re/blog/503ee3dc5393744800000000/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p><a href="/motor/">Motor</a>, my async driver for <span style='text-decoration:underline;'>Mo</span>ngoDB and <span style='text-decoration:underline;'>Tor</span>nado, is now compatible with all the same Python versions as Tornado: CPython 2.5, 2.6, 2.7, and 3.2, and PyPy 1.9.</p>
<p>To get Motor working with Python 3 I had to make a <strong>backwards breaking change</strong>: <code>MotorCursor.next</code> is now <code>next_object</code>. So this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cursor <span style="color: #666666">=</span> db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find()
cursor<span style="color: #666666">.</span>next(my_callback)
</pre></div>


<p>... must now be:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cursor <span style="color: #666666">=</span> db<span style="color: #666666">.</span>collection<span style="color: #666666">.</span>find()
cursor<span style="color: #666666">.</span>next_object(my_callback)
</pre></div>


<p>I had to do this to neatly support Python 3, because <code>2to3</code> was unhelpfully transforming <code>MotorCursor.next</code> into <code>__next__</code>. But the change was worthy even without that problem: <code>next_object</code> is closer to <a href="http://mongodb.github.com/node-mongodb-native/markdown-docs/queries.html#cursors"><code>nextObject</code> in the Node.js MongoDB driver</a>, whose API I'm trying to emulate. Besides, I wasn't using <code>next</code> the way Python intends, so I went ahead and renamed it. I'm sorry if this breaks your code. This is what the alpha phase is for.</p>
<p>The only remaining feature to implement is <a href="http://www.mongodb.org/display/DOCS/GridFS">GridFS</a>, which I'll do within the month. There's some more testing and documentation to do, and then we'll move from alpha to beta.</p>
<p>I know a few people are trying out Motor. I've received no bug reports so far, but some users have reported omissions in the <a href="http://motor.readthedocs.org/en/stable/api/index.html">docs</a> which I've filled in. If you're using Motor, get in touch and let me know: <a href="mailto:jesse@10gen.com">jesse@10gen.com</a>.</p>
