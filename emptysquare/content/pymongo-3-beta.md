+++
type = "post"
title = "Announcing PyMongo 3.0 Beta"
date = "2015-03-09T23:11:02"
description = "PyMongo 3.0 is conformant, responsive, robust, and modern. Try it!: pip install https://github.com/mongodb/mongo-python-driver/archive/3.0b0.tar.gz"
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "adder.png"
draft = false
disqus_identifier = "54fe5f9c539374097ee7db87"
disqus_url = "https://emptysqua.re/blog/54fe5f9c539374097ee7db87/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="adder.png" alt="Adder" title="Adder" /></p>
<p>You have no idea how it thrills me to tell you this. We have just shipped PyMongo 3.0 Beta. You need to <a href="http://api.mongodb.org/python/3.0b0/changelog.html">read the changelog</a> and install it in your dev environment now:</p>
<pre style="text-align: left"><code>pip install https://github.com/mongodb/mongo-python-driver/archive/3.0b0.tar.gz</code></pre>

<p>It's not common among Python folk, in my experience, to test each others' betas. But this month I really need your help: <strong>Please give PyMongo 3 a spin.</strong> </p>
<p>Tell me if the new interfaces work for you. Tell me if our API changes make sense, if they require more updates to your code than they're worth, if we documented them all properly in the changelog. And naturally, tell me if you found any bugs.</p>
<p>Vastly more information will come in the next few weeks. I'll write to you about how much more conformant, responsive, robust, and modern the new PyMongo is. Besides that, my colleagues and I at MongoDB are drafting articles on the specifications PyMongo 3 implements:</p>
<ul>
<li>The new <a href="https://github.com/mongodb/specifications/blob/master/source/crud/crud.rst">CRUD API spec</a> that gives you a clean new interface for basic operations on your data.</li>
<li>My <a href="/server-discovery-and-monitoring-spec/">Server Discovery And Monitoring Spec</a> defines how drivers connect to the servers in your replica set or sharded cluster and stay abreast of changes.</li>
<li>The <a href="https://github.com/mongodb/specifications/blob/master/source/server-selection/server-selection.rst">Server Selection Spec</a> is a straightforward new expression of how to choose replica set members for reads, or how to load balance among mongoses.</li>
</ul>
<p>Stay tuned.</p>
<p><a href="https://commons.wikimedia.org/wiki/File:Adder_(PSF).png"><span style="color:gray">Image: Pearson Scott Foresman.</span></a></p>
