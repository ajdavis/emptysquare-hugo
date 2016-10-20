+++
type = "post"
title = "Motor Installation Instructions"
date = "2012-10-31T12:31:41"
description = ""
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "50914b165393741e3a02ed17"
disqus_url = "https://emptysqua.re/blog/50914b165393741e3a02ed17/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="motor-musho.png" border="0"   /></p>
<p><strong>Update:</strong> <a href="/motor-officially-released/">Motor is in PyPI now, this is all moot</a></p>
<p>I've done a bad job with installation instructions for <a href="/motor/">Motor</a>, my non-blocking driver for MongoDB and Tornado. I've gotten a bunch of emails from people complaining about this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">Traceback (most recent call last):    
  File <span style="color: #008000">&quot;myfile.py&quot;</span>, line <span style="color: #666666">2</span>, in &lt;module&gt;
    connection <span style="color: #666666">=</span> motor<span style="color: #666666">.</span>MotorConnection()<span style="color: #666666">.</span>open_sync()
  File <span style="color: #008000">&quot;.../motor/__init__.py&quot;</span>, line <span style="color: #666666">690</span>, in open_sync
    <span style="color: #008000; font-weight: bold">raise</span> outcome[<span style="color: #BA2121">&#39;error&#39;</span>]
<span style="color: #FF0000">pymongo.errors.ConfigurationError</span>: Unknown option _pool_class
</pre></div>


<p>You'll get this ConfigurationError if you installed Motor without <em>uninstalling</em> PyMongo first. But you couldn't know that, because I forgot to tell you.</p>
<p>Here's installation instructions, followed by an explanation of why installation is wonky right now and how it will improve, and what Motor's status is now.</p>
<h2 id="installation">Installation</h2>
<p>I assume you have <a href="http://www.pip-installer.org/en/latest/installing.html">pip</a>, and I recommend you use <a href="http://www.virtualenv.org/en/latest/">virtualenv</a>&mdash;these are just best practices for all Python application development. You need regular CPython, 2.5 or better. </p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic"># if you have pymongo installed previously, you MUST uninstall it</span>
pip uninstall pymongo

<span style="color: #408080; font-style: italic"># install prerequisites</span>
pip install tornado greenlet

<span style="color: #408080; font-style: italic"># get motor</span>
pip install git+https://github.com/ajdavis/mongo-python-driver.git@motor
</pre></div>


<p>Now you should have my versions of pymongo, bson, gridfs, and motor installed:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;&gt;&gt;</span> <span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">motor</span>
<span style="color: #666666">&gt;&gt;&gt;</span>
</pre></div>


<p><strong>Update:</strong> If you're testing against a particular version of Motor, you can freeze that requirement and install that version by git hash, like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install git+https://github.com/ajdavis/mongo-python-driver.git@694436f
</pre></div>


<p>pip will say, "Could not find a tag or branch '694436f', assuming commit," which is what you want. You can put Motor and its dependencies in your requirements.txt:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">greenlet<span style="color: #666666">==0.4.0</span>
tornado<span style="color: #666666">==2.4</span>
git<span style="color: #666666">+</span><span style="color: #A0A000">https</span>:<span style="color: #408080; font-style: italic">//github.com/ajdavis/mongo-python-driver.git@694436f</span>
</pre></div>


<p>And install:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip install -r requirements.txt
</pre></div>


<p>Confusingly, the command to uninstall Motor is:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">pip uninstall pymongo
</pre></div>


<h2 id="why-is-installation-wonky">Why Is Installation Wonky?</h2>
<p>Why do you have to uninstall 10gen's official PyMongo before installing Motor? Why isn't Motor in PyPI? Why doesn't Motor automatically install the Tornado and Greenlet packages as dependencies? All will be revealed.</p>
<p>Implementing Motor requires a few extra hooks in the core PyMongo module. For example, I added a <code>_pool_class</code> option to PyMongo's Connection class. Thus Motor and PyMongo are coupled, and I want them to be versioned together. Motor is a <strong>feature</strong> of PyMongo that you can choose to use. In the future when Motor is an official 10gen product, Motor and PyMongo will be in the same git repository, and in the same package in PyPI, and when you <code>pip install pymongo</code>, you'll get the <code>motor</code> module installed in your site-packages, just like the <code>pymongo</code>, <code>bson</code>, <code>gridfs</code> modules now. There will never be a separate "Motor" package in PyPI.</p>
<p>Even once Motor is official, the whole PyMongo package shouldn't require Tornado and Greenlet as dependencies. So you'll still need to manually install them to make Motor work. PyMongo will still work without Tornado and Greenlet, of course&mdash;they won't be necessary until you <code>import motor</code>.</p>
<p>Since that's the goal&mdash;the Motor module as a feature of PyMongo, in the same repository and the same PyPI package&mdash;this beta period is awkward. I'm building Motor <a href="https://github.com/ajdavis/mongo-python-driver/tree/motor/">in my fork of the PyMongo repo, on a <code>motor</code> branch</a>, and regularly merging the upstream repo's changes. Sometimes, upstream changes to PyMongo break Motor and need small fixes.</p>
<p>I don't want to make a PyPI package for Motor, since that package will be obsolete once Motor's merged upstream. And since the eventual version of the PyMongo package that includes Motor won't require Tornado or Greenlet as dependencies, neither does the version in my git repo.</p>
<h2 id="status">Status</h2>
<p>Motor is feature-complete, and it's compatible with <a href="http://pypi.python.org/pypi/tornado">all the Python versions that Tornado is</a>. MotorConnection has been load-tested by the QA team at a large corporation, with good results. At least one small startup has put MotorReplicaSetConnection in production, with one bug reported and <a href="https://github.com/ajdavis/mongo-python-driver/commit/d9fa6fd92726be8f8f165a6e5cd74867024ead96">fixed</a>&mdash;Motor threw the wrong kinds of exceptions during a replica-set failover. I'm now hunting a similar MotorReplicaSetConnection bug <a href="https://groups.google.com/d/topic/python-tornado/vvS9xzP8mm4/discussion">reported on the Tornado mailing list</a>.</p>
<p>Besides that bug, Motor has 37 TODOs. All are reminders to myself to refactor Motor's interaction with PyMongo, and to ensure every corner of Motor is reviewed, tested, and documented. I need to:</p>
<ul>
<li>Complete those refactoring, testing, and documentation TODOs</li>
<li>Ensure 100% code coverage by unittests</li>
<li>Complete my own load-testing to make sure Motor matches AsyncMongo's performance</li>
<li>Pass code reviews from PyMongo's maintainer Bernie Hackett</li>
</ul>
<p>At that point, Bernie and I will decide if Motor is ready to go official, and I'll announce on this blog, and throw a party.</p>
<p><a href="http://nedroid.com/2009/05/party-cat-full-series/">
<img style="display:block; margin-left:auto; margin-right:auto;" src="party-cat.png" alt="Party Cat" title="party-cat.png" border="0"   />
</a></p>
