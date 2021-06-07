+++
type = "post"
title = "Announcing PyMongo 3.2"
date = "2015-12-07T21:24:46"
description = "Supports all the new MongoDB 3.2 features."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "tree-boa.jpg"
draft = false
disqus_identifier = "56663f551e31ec1d4936ee5c"
disqus_url = "https://emptysqua.re/blog/56663f551e31ec1d4936ee5c/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="tree-boa.jpg" alt="Emerald Tree Boa" title="Emerald Tree Boa" /></p>
<p>Our Python team released PyMongo 3.2 today. This time I wasn't involved at all; Bernie Hackett, Anna Herlihy, and Luke Lovett developed this version, with a contribution from Felix Yan.</p>
<p>Version 3.2 implements the new server features introduced in MongoDB 3.2. (It's a coincidence that the version numbers are the same.)</p>
<ul>
<li>Support for ReadConcern.</li>
<li>WriteConcern is now applied to <code>find_one_and_replace()</code>, <code>find_one_and_update()</code>, and <code>find_one_and_delete()</code>.</li>
<li>Support for the new bypassDocumentValidation option in write helpers.</li>
<li>Reading and write raw BSON with <code>RawBSONDocument</code>&mdash;this feature is very exciting, show us what you can do with it!</li>
<li>We now prefer the package "Monotime" to the outdated "monotonic" to provide a safe clock.</li>
</ul>
<p>Some MongoClient properties, like <code>client.is_mongos</code>, will now block until a connection is established or raise ServerSelectionTimeoutError if no server is available.</p>
<p>Links:</p>
<ul>
<li><a href="https://pypi.python.org/pypi/pymongo/">PyPI</a>.</li>
<li><a href="https://pymongo.readthedocs.io/en/stable/">PyMongo documentation</a>.</li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20PYTHON%20AND%20fixVersion%20%3D%203.2%20ORDER%20BY%20updated%20DESC%2C%20priority%20DESC%2C%20created%20ASC">All features and bugfixes in PyMongo 3.2</a>.</li>
</ul>
<hr />
<p><a href="https://en.wikipedia.org/wiki/National_Aquarium_(Baltimore)#/media/File:National_Aquarium_in_Baltimore_Snake.jpg"><span style="color:gray">Image: Wikipedia</span></a></p>
