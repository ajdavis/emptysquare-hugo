+++
category = ['MongoDB', 'Motor', 'Programming', 'Python']
date = '2016-11-29T22:58:25.403751'
description = 'Now wraps PyMongo 3.4+ and supports the latest features, like collation and write concern for commands'
draft = false
tag = []
thumbnail = 'motor-musho.png'
title = 'Announcing Motor 1.1 For MongoDB 3.4'
type = 'post'
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="motor-musho.png" alt="Motor" border="0" /></p>

MongoDB 3.4 was released this morning; tonight I've released Motor 1.1 with support for the latest MongoDB features.

Motor 1.1 now depends on PyMongo 3.4 or later. (It's an annoying coincidence that the latest MongoDB and PyMongo versions are the same number.)

With MongoDB 3.4 and the latest Motor, you can now configure unicode-aware string comparison using collations. See <a href="https://pymongo.readthedocs.io/en/stable/3.4.0/examples/collations.html#collation-on-operation">PyMongo's examples for collation</a>.</li> Motor also supports the new <a href="https://pymongo.readthedocs.io/en/stable/3.4.0/api/bson/decimal128.html#bson.decimal128.Decimal128"><code>Decimal128</code></a> BSON type. The new MongoDB version supports write concern with all commands that write, so `drop_database`, `create_collection`, `create_indexes`, and all the other commands that modify your data accept a writeConcern parameter.

The [Max Staleness Spec](https://github.com/mongodb/specifications/blob/master/source/max-staleness/max-staleness.rst) I've labored the last few months to complete is now implemented in all drivers, including Motor 1.1.

Motor has improved support for logging server discovery and monitoring events. See
<a href="https://pymongo.readthedocs.io/en/stable/3.4.0/api/pymongo/monitoring.html#module-pymongo.monitoring">PyMongo's monitoring documentation</a> for examples.

For a complete list of changes, see the [Motor 1.1 changelog](http://motor.readthedocs.io/en/stable/changelog.html) and [the PyMongo 3.4 changelog](http://api.mongodb.com/python/current/changelog.html). Post questions about Motor to the
<a class="reference external" href="https://groups.google.com/forum/?fromgroups#!forum/mongodb-user">mongodb-user list on Google Groups</a>.
For confirmed issues or feature requests, open a case in
<a class="reference external" href="http://jira.mongodb.org">Jira</a> in the "MOTOR" project.

Or, just <a href="https://twitter.com/jessejiryudavis">let me know on Twitter that you're using Motor</a>.
