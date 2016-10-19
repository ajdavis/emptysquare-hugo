+++
type = "post"
title = "Motor 0.3.4 Released"
date = "2014-11-10T17:06:44"
description = "Fixes a leak in the connection pool."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
legacyid = "54613646539374096a7ddf6e"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today I released version 0.3.4 of Motor, the asynchronous MongoDB driver for Python and Tornado. This release is compatible with MongoDB 2.2, 2.4, and 2.6. It requires PyMongo 2.7.1.</p>
<p>This release fixes <a href="https://jira.mongodb.org/browse/MOTOR-57">a leak in the connection pool</a>. <code>MotorPool.get_socket()</code> proactively checks a socket for errors if it hasn't been used in more than a second. It calls <code>select()</code> on the socket's file descriptor to see if the socket has been shut down at the OS level. If this check fails, Motor discards the socket. But it forgot to decrement its socket counter, so the closed socket is forever counted against <code>max_pool_size</code>. This is the equivalent of a semaphore leak in a normal multi-threaded connection pool.</p>
<p>The bug has been present since Motor 0.2. I discovered it while testing Motor's handling of network errors with exhaust cursors, but the leak is not particular to exhaust cursors.</p>
<p>Get the latest version with <code>pip install --upgrade motor</code>. <a href="http://motor.readthedocs.org/en/stable">The documentation is on ReadTheDocs</a>. <a href="http://motor.readthedocs.org/en/stable/changelog.html">View the changelog here</a>. If you encounter any issues, please <a href="https://jira.mongodb.org/browse/MOTOR">file them in Jira</a>.</p>
