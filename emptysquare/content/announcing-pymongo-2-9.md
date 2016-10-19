+++
type = "post"
title = "Announcing PyMongo 2.9"
date = "2015-10-06T12:11:44"
description = "A compatibility bridge between PyMongo 2 and PyMongo 3 APIs."
category = ["Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "Boelen_Python@240.jpg"
draft = false
legacyid = "5613f2485393742358ca4629"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Boelen_Python.jpg" alt="Boelen Python" title="Boelen Python" /></p>
<p>Bernie Hackett, Anne Herlihy, and Luke Lovett released PyMongo 2.9 last week. "Why," you ask, "was PyMongo 2.9 released after PyMongo 3?"</p>
<p>PyMongo 2.9 is a bridge for PyMongo 2.8 users who want to upgrade applications to PyMongo 3's new API. There are substantial API changes in the 3.0 release, so the PyMongo team created a version that supports nearly the entire APIs for <em>both</em> PyMongo 2 and 3. That's PyMongo 2.9.</p>
<p>Read the <a href="http://api.mongodb.org/python/2.9/migrate-to-pymongo3.html">Migration Guide</a> for complete instructions. The short version is: upgrade your application to PyMongo 2.9 first. Turn on DeprecationWarnings like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">python -Wd my_application.py
</pre></div>


<p>Once you have run your tests and fixed all your uses of deprecated PyMongo 2 APIs, you are most of the way to PyMongo 3 readiness. There are a few API changes this technique can't catch, so read the rest of the migration guide carefully. Once you've done that, upgrade to PyMongo 3 and run your tests once again. Now you've safely reached PyMongo 3, with all <a href="/blog/announcing-pymongo-3/">the performance and robustness enhancements it offers</a>.</p>
<p>(I'm a little late announcing this one&mdash;last week's <a href="/blog/announcing-libbson-and-libmongoc-1-2-0-release-candidate/">C Driver release</a> and <a href="/blog/march-to-triumph-as-a-mentor-video/">the Philadelphia meetup</a> took all my attention.)</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Boelen_Python_01.jpg">Image: Danleo on Wikimedia Commons.</a></p>
