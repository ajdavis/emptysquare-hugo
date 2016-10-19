+++
type = "post"
title = "Motor 0.3.1 Released"
date = "2014-07-08T15:13:20"
description = "Fixes a bug when GridFSHandler is combined with a timezone-aware MotorClient."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
legacyid = "53bc41ed5393745d31c3f83e"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today I released version 0.3.1 of Motor, the asynchronous MongoDB driver for Python and Tornado. This release is compatible with MongoDB 2.2, 2.4, and 2.6. It requires PyMongo 2.7.1.</p>
<p>There are no new features. Changes:</p>
<ul>
<li>Fix <a href="https://jira.mongodb.org/browse/MOTOR-43">an error with GridFSHandler and timezone-aware MotorClients</a>.</li>
<li>Fix <a href="http://motor.readthedocs.org/en/stable/examples/gridfs.html">GridFS examples</a> that hadn't been updated for Motor 0.2's new syntax.</li>
<li>Fix <a href="https://github.com/mongodb/motor/commit/395ccac2823cbd193fdc5a9345f79f084656c5e3">a unittest that hadn't been running</a>.</li>
</ul>
<p>Get the latest version with <code>pip install --upgrade motor</code>. <a href="http://motor.readthedocs.org/en/stable">The documentation is on ReadTheDocs</a>. If you encounter any issues, please <a href="https://jira.mongodb.org/browse/MOTOR">file them in Jira</a>.</p>
<p>Meanwhile, I'm prototyping <code>asyncio</code> support alongside Tornado for Motor's next major release.</p>
