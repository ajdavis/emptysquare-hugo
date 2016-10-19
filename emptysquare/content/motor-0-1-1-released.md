+++
type = "post"
title = "Motor 0.1.1 released"
date = "2013-06-24T12:09:32"
description = "Fixes an incompatibility between Motor and the latest version of PyMongo, by pinning Motor's dependency to PyMongo 2.5.0 exactly."
category = ["Mongo", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho@240.png"
draft = false
legacyid = "51c86f1253937473788cbc8a"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" title="Motor" border="0"   /></p>
<p>Motor is my async driver for <a href="http://www.tornadoweb.org/">Tornado</a> and <a href="http://www.mongodb.org/">MongoDB</a>. Version 0.1 has been out since early March and is having a successful career with no serious bugs reported so far. Unfortunately PyMongo, the blocking driver that Motor wraps, has changed a bit since then and Motor is no longer compatible with the latest PyMongo. If you did <code>pip install motor</code> you'd pull in Motor 0.1 and PyMongo 2.5.2, and see a failure when opening a <code>MotorReplicaSetClient</code>, like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #0044DD">Traceback (most recent call last):</span>
  File <span style="color: #008000">&quot;example.py&quot;</span>, line <span style="color: #666666">3</span>, in &lt;module&gt;
    client <span style="color: #666666">=</span> MotorReplicaSetClient(replicaSet<span style="color: #666666">=</span><span style="color: #BA2121">&#39;foo&#39;</span>)<span style="color: #666666">.</span>open_sync()
  File <span style="color: #008000">&quot;motor/__init__.py&quot;</span>, line <span style="color: #666666">967</span>, in open_sync
    <span style="color: #008000">super</span>(MotorReplicaSetClient, <span style="color: #008000">self</span>)<span style="color: #666666">.</span>open_sync()
  File <span style="color: #008000">&quot;motor/__init__.py&quot;</span>, line <span style="color: #666666">804</span>, in open_sync
    <span style="color: #008000; font-weight: bold">for</span> pool <span style="color: #AA22FF; font-weight: bold">in</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>_get_pools():
  File <span style="color: #008000">&quot;motor/__init__.py&quot;</span>, line <span style="color: #666666">1004</span>, in _get_pools
    <span style="color: #008000">self</span><span style="color: #666666">.</span>delegate<span style="color: #666666">.</span>_MongoReplicaSetClient__members<span style="color: #666666">.</span>values()]
  File <span style="color: #008000">&quot;pymongo/collection.py&quot;</span>, line <span style="color: #666666">1418</span>, in __call__
    <span style="color: #008000">self</span><span style="color: #666666">.</span>__name)
<span style="color: #FF0000">TypeError</span>: &#39;Collection&#39; object is not callable. If you meant to call the &#39;values&#39; method on a &#39;Database&#39; object it is failing because no such method exists.
</pre></div>


<p>This morning I've released a bugfix version of Motor, version 0.1.1, to correct the problem. This version simply updates the installer to pull in PyMongo 2.5.0, the last version that works with Motor, rather than PyMongo 2.5.2, the latest.</p>
<p>In the medium term, we'll release a PyMongo 3.0 with well-specified hooks for Motor, and for other libraries that want to do deep customization. Motor can switch to using those hooks, and be much less tightly coupled with particular PyMongo versions.</p>
<p>When that happens I can release a Motor 1.0. Meanwhile, I think Motor's low version numbers properly reflect that it's too tightly coupled to PyMongo's internal properties.</p>
