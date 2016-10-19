+++
type = "post"
title = "Motor 0.3.2 Released"
date = "2014-07-14T15:46:27"
description = "Fixes a socket leak in \"copy_database\" that has been present since Motor 0.2."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "53c433935393741fc69c6917"
disqus_url = "https://emptysqua.re/blog/53c433935393741fc69c6917/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Today I released version 0.3.2 of Motor, the asynchronous MongoDB driver for Python and Tornado. This release is compatible with MongoDB 2.2, 2.4, and 2.6. It requires PyMongo 2.7.1.</p>
<p>This release fixes <a href="https://jira.mongodb.org/browse/MOTOR-44">a socket leak in the "copy_database" method</a> that has been present since Motor 0.2. Evidently Motor users don't call "copy_database" much. I've written about the bug and lessons learned in <a href="/let-us-now-praise-resourcewarnings/">"Let Us Now Praise ResourceWarnings"</a>.</p>
<p>Get the latest version with <code>pip install --upgrade motor</code>. <a href="http://motor.readthedocs.org/en/stable">The documentation is on ReadTheDocs</a>. If you encounter any issues, please <a href="https://jira.mongodb.org/browse/MOTOR">file them in Jira</a>.</p>
