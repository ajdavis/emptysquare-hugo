+++
type = "post"
title = "Motor Is Growing Up"
date = "2013-01-24T23:36:21"
description = "Motor, my async driver for MongoDB and Python Tornado, will be its own package."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
disqus_identifier = "51020bc55393747de89b6614"
disqus_url = "https://emptysqua.re/blog/51020bc55393747de89b6614/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p>For a long time I've thought that <a href="/motor/">Motor</a>, my non-blocking Python driver for MongoDB and Tornado, ought to be included as a module within the standard <a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a> package. Everyone both inside and outside 10gen has told me they'd prefer Motor be a separate distribution. Last week, I was suddenly enlightened. I agree!</p>
<p>(My argument for keeping Motor and PyMongo together was that changes in PyMongo might require changes in Motor, so they should be versioned and released together. But as Motor nears completion and I see the exact extent of its coupling with PyMongo, the risk of incompatibilities arising seems lower to me than it had.)</p>
<p>We completed the first step of the separation yesterday: <a href="/blog/pymongo-2-4-2-is-out/">We released PyMongo 2.4.2</a>, the first version of PyMongo that includes the hooks Motor needs to wrap it and make it non-blocking.</p>
<p>The next step is to make a standalone distribution of Motor, and that's almost done, too. Motor has left its parent's house. It has:</p>
<ul>
<li><a href="https://github.com/mongodb/motor/">Its own GitHub repo</a></li>
<li>A <a href="http://motor.readthedocs.org/">ReadTheDocs page</a></li>
<li>A <a href="https://travis-ci.org/mongodb/motor">Travis page</a></li>
</ul>
<p>And now, installing Motor is finally normal:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>git clone git://github.com/mongodb/motor.git
<span style="color: #19177C">$ </span><span style="color: #008000">cd </span>motor
<span style="color: #19177C">$ </span>python setup.py install
</pre></div>


<p>Motor's not done yet, but it's heading to a 0.1 release in PyPI, as a standalone package, real soon now.</p>
