+++
type = "post"
title = "PyMongo 2.7 Has Shipped"
date = "2014-04-03T14:35:27"
description = "New features, mainly to support MongoDB 2.6."
categories = ["Mongo", "Motor", "Programming", "Python"]
tags = ["pymongo"]
enable_lightbox = false
thumbnail = "amethystine-scrub-python.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="amethystine-scrub-python.jpg" alt="Amethystine scrub python" title="Amethystine scrub python" /></p>
<p><span style="color:gray"><a href="https://www.flickr.com/photos/bitterbug/420932565/">Source: inrideo on Flickr</a></span></p>
<p>I announce with satisfaction that we've released PyMongo 2.7, the successor to PyMongo 2.6.3. The bulk of the driver's changes are to support MongoDB 2.6, which is currently a release candidate. The newest MongoDB has an enhanced wire protocol and some big new features, so PyMongo 2.7 is focused on supporting it. However, the driver still supports server versions as old as 1.8.</p>
<p><a href="/blog/pymongo-2-7-rc0/">Read my prior post for a full list of the features and improvements in PyMongo</a>. Since I wrote that, we've fixed some compatibility issues with MongoDB 2.6, dealt with recent changes to the <code>nose</code> and <code>setuptools</code> packages, and made a couple memory optimizations.</p>
<p>Motor 0.2 is about to ship, as well. I'll give the details in my next post.</p>
<p>What's next for PyMongo? We now embark on a partial rewrite, which will become PyMongo 3.0. The next-generation driver will delete many deprecated APIs: <code>safe</code> will disappear, since it was deprecated in favor of <code>w=1</code> years ago. <code>Connection</code> will walk off into the sunset, giving way to <code>MongoClient</code>. We'll make a faster and more thread-safe core for PyMongo, and we'll expose a clean API so Motor and ODMs can wrap PyMongo more neatly.</p>
<p>We'll discard PyMongo's current C extension for BSON-handling. We'll replace it with <a href="https://github.com/mongodb/libbson">libbson</a>, a common codec that our C team is building. If you're handling BSON in PyPy, we aim to give you a much faster pure-Python codec there, too.</p>
    