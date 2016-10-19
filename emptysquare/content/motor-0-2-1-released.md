+++
type = "post"
title = "Motor 0.2.1 Released"
date = "2014-05-27T15:41:29"
description = "A patch release that fixes two bugs."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "5384ea4453937409329fca1e"
disqus_url = "https://emptysqua.re/blog/5384ea4453937409329fca1e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0" /></p>
<p>Version 0.2.1 of Motor, the asynchronous MongoDB driver for Python and Tornado, has been released. It fixes two bugs:</p>
<ul>
<li><a href="https://jira.mongodb.org/browse/MOTOR-32">MOTOR-32</a>:
  The documentation claimed that <code>MotorCursor.close</code> immediately
  halted execution of <code>MotorCursor.each</code>, but it didn't.
  <code>MotorCursor.each()</code> is now halted correctly.</li>
<li><a href="https://jira.mongodb.org/browse/MOTOR-33">MOTOR-33</a>:
  An incompletely iterated cursor's <code>__del__</code> method sometimes got stuck
  and cost 100% CPU forever, even though the application was still responsive.</li>
</ul>
<p><a href="http://motor.readthedocs.org/en/stable/">The manual is on ReadTheDocs</a>. If you find a bug or want a feature, I exhort you to <a href="https://jira.mongodb.org/browse/MOTOR">report it</a>.</p>
