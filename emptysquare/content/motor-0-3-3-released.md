+++
type = "post"
title = "Motor 0.3.3 Released"
date = "2014-10-04T20:47:26"
description = "Fixes an infinite loop and memory leak."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "543083145393740961f61a1e"
disqus_url = "https://emptysqua.re/blog/543083145393740961f61a1e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today I released version 0.3.3 of Motor, the asynchronous MongoDB driver for Python and Tornado. This release is compatible with MongoDB 2.2, 2.4, and 2.6. It requires PyMongo 2.7.1.</p>
<p>This release fixes <a href="https://jira.mongodb.org/browse/MOTOR-45">an occasional infinite loop and memory leak</a>. The bug was triggered when you passed a callback to <a href="http://motor.readthedocs.org/en/stable/api/motor_cursor.html#motor.MotorCursor.each">MotorCursor.each</a>, and Motor had to open a new socket in the process of executing your callback, and your callback raised an exception:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">tornado.ioloop</span> <span style="color: #008000; font-weight: bold">import</span> IOLoop
<span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">motor</span>

loop <span style="color: #666666">=</span> IOLoop<span style="color: #666666">.</span>instance()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">each</span>(result, error):
    <span style="color: #008000; font-weight: bold">raise</span> <span style="color: #D2413A; font-weight: bold">Exception</span>()

collection <span style="color: #666666">=</span> motor<span style="color: #666666">.</span>MotorClient()<span style="color: #666666">.</span>test<span style="color: #666666">.</span>test
cursor <span style="color: #666666">=</span> collection<span style="color: #666666">.</span>find()<span style="color: #666666">.</span>each(callback<span style="color: #666666">=</span>each)
loop<span style="color: #666666">.</span>start()
</pre></div>


<p>The bug has been present since Motor 0.2. I am indebted to Eugene Protozanov for an excellent bug report.</p>
<p>Get the latest version with <code>pip install --upgrade motor</code>. <a href="http://motor.readthedocs.org/en/stable">The documentation is on ReadTheDocs</a>. <a href="http://motor.readthedocs.org/en/stable/changelog.html">View the changelog here</a>. If you encounter any issues, please <a href="https://jira.mongodb.org/browse/MOTOR">file them in Jira</a>.</p>
