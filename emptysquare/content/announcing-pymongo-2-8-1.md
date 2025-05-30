+++
type = "post"
title = "Announcing PyMongo 2.8.1"
date = "2015-05-11T21:18:35"
description = "Bugfix release for PyMongo 2.8."
category = ["MongoDB", "Programming", "Python"]
tag = ["pymongo"]
enable_lightbox = false
thumbnail = "vines.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="vines.jpg" alt="Vines" title="Vines" /></p>
<p><a href="https://pypi.python.org/pypi/pymongo/2.8.1">PyMongo 2.8.1</a> is a bugfix release that addresses issues discovered since PyMongo 2.8 was released, primarily related to authentication and metadata operations on replica sets. If you're on PyMongo 2.8 and not ready to update your code for the <a href="/pymongo-3-beta/">new APIs and behaviors of the PyMongo 3.0 line</a>, please upgrade to PyMongo 2.8.1 promptly.</p>
<ul style="text-align:left">
<li><a href='https://jira.mongodb.org/browse/PYTHON-842'>PYTHON-842</a> -         Unable to specify &#39;ssl_cert_reqs&#39; option using URI style connection string
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-864'>PYTHON-864</a> -         Fully support RFC-3339 offset format for $date
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-893'>PYTHON-893</a> -         Wrong wrapping function called for CommandCursor
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-903'>PYTHON-903</a> -         Properly handle network errors in auth
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-913'>PYTHON-913</a> -         UserWarning with read preference and command using direct connection
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-915'>PYTHON-915</a> - secondaryAcceptablelatencyMS should accept 0
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-918'>PYTHON-918</a> -         Auth err from resyncing member prevents primary discovery
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-920'>PYTHON-920</a> -         collection_names, options, and index_information prohibited on direct connection to secondary with MongoDB 3.0+
</li>
<li><a href='https://jira.mongodb.org/browse/PYTHON-921'>PYTHON-921</a> -         database_names prohibited on direct connection to secondary with MongoDB 3.0+
</li>
</ul>

<p>For the full list of bugs fixed in PyMongo 2.8.1, please <a href="https://jira.mongodb.org/browse/PYTHON/fixforversion/15324">see the release in Jira</a>. </p>
