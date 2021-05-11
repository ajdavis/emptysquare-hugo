+++
type = "post"
title = "Download Stats By Python Version: PyMongo, Motor, Tornado"
date = "2015-05-06T18:22:59"
description = "Some pretty charts about relative Python version usages from Donald Stufft."
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-downloads-python-3.png"
draft = false
disqus_identifier = "554a8f6d5393741c64c20acf"
disqus_url = "https://emptysqua.re/blog/554a8f6d5393741c64c20acf/"
+++

<p>After PyCon last month, Python packaging saint Donald Stufft <a href="https://twitter.com/dstufft/status/589596259071221762">generously tweeted</a>:</p>
<blockquote>
<p>If you&rsquo;re interested to see Py2 vs Py3 breakdowns for a Python package, let me know while I still have the data set loaded (~300GB DB).</p>
</blockquote>
<p>He had the database loaded for his diverting article on a <a href="https://caremad.io/2015/04/a-year-of-pypi-downloads/">Year of PyPI Downloads</a>, but I was curious about three packages I own or contribute to.</p>
<hr />
<div class="toc">
<ul>
<li><a href="#pymongo">PyMongo</a></li>
<li><a href="#motor">Motor</a></li>
<li><a href="#tornado">Tornado</a></li>
<li><a href="#conclusion">Conclusion</a></li>
</ul>
</div>
<h1 id="pymongo">PyMongo</h1>
<p>Here's PyMongo's downloads this year, by Python version:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-downloads.png" alt="PyMongo downloads" title="PyMongo downloads" /></p>
<p>Python 2.7 dominates, and it is growing at the expense of 2.6. Python 2.4 is absent, and PyMongo downloads for Python 2.5 vanished last year, which validates our decision to <a href="http://api.mongodb.org/python/current/changelog.html">drop Python 2.4 and 2.5 from the latest release, PyMongo 3.0</a>.</p>
<p>Donald made a second chart isolating the Python 3 downloads:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="pymongo-downloads-python-3.png" alt="PyMongo downloads for Python 3" title="PyMongo downloads for Python 3" /></p>
<p>As one expects, people who use Python 3 use the latest one, Python 3.4. When we released PyMongo 2.8.0 at the end of January, the download spike was <em>entirely</em> Python 3.4 users.</p>
<p>I expect Python 3.5 will soon dominate among Python 3 users, and Python 2.6 will continue to decline asymptotically, while the Python 2 versus 3 ratio overall will stay steady for a few more years.</p>
<h1 id="motor">Motor</h1>
<p>Something is wrong with Donald's chart for Motor, but it suggests that Motor users are like PyMongo users: 10% run the latest Python 3, 50% run Python 2.7, and the others run a smattering of other Pythons. (Motor has never supported Python before 2.6.)</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-downloads.png" alt="Motor downloads" title="Motor downloads" /></p>
<p>In Donald's Python 3 chart, it seems only Python 3.4 is represented:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-downloads-python-3.png" alt="Motor downloads for Python 3" title="Motor downloads for Python 3" /></p>
<h1 id="tornado">Tornado</h1>
<p>Motor's potential user base includes all Tornado users, so I was curious about Tornado's overall distribution:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tornado-downloads.png" alt="Tornado downloads" title="Tornado downloads" /></p>
<p>I have no explanation for the spike of Python 2.6 downloads last fall; Tornado's release schedule doesn't strongly correlate with it. Tornado's user base is distributed similarly to PyMongo's, though more inclined to stay on Python 2.6.</p>
<p>Again, Tornado's Python 3 users hold steady at ten percent, but they switched to Python 3.4 quickly after it was released.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tornado-downloads-python-3.png" alt="Tornado downloads for Python 3" title="Tornado downloads for Python 3" /></p>
<h1 id="conclusion">Conclusion</h1>
<p>The takeaways are: Python 2.4 is dead, and 2.5 is effectively dead for PyMongo, Motor, and Tornado users. It's important to keep packages working in Python 2.6&mdash;mainly for enterprises with long-term support contracts for Linux versions that shipped with 2.6&mdash;but adding features or optimizations that only work in Python 2.7 is reasonable now.</p>
<p>It's critical we keep testing Python 3.5 alphas and betas as they come out, because the 10% of people who run Python 3 will migrate to 3.5 rapidly. Python 3.2 is nearly dead, and 3.3 will also vanish soon.</p>
