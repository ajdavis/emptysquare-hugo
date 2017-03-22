+++
category = ['C', 'Mongo', 'Programming']
date = '2016-11-27T22:13:46.005610'
description = 'MongoDB 3.4 support, topology-change monitoring, and Decimal128 support.'
draft = false
tag = []
thumbnail = 'the-oaks-3.jpg'
title = 'Announcing libbson and libmongoc 1.5.0'
type = 'post'
+++

<a href="https://www.flickr.com/photos/emptysquare/30197750970/in/photolist-N1tond-NpBkub-NpBmnJ-NpBjAs-NpBmL9-NpBkSf-NpBiFG-N1tnhN-NpBk2h"><img src="the-oaks-3.jpg" /></a>

I'm pleased to announce version 1.5.0 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>,
the libraries constituting the MongoDB C Driver.

# libbson

We have a brand-new BSON Type, [Decimal128](http://mongoc.org/libbson/current/bson_decimal128_t.html), which MongoDB 3.4 and all drivers now implement.

The BSON "code" and "code with scope" types are better supported now: bson_append_code_with_scope now preserves the "code with scope" type if scope is an empty, non-NULL BSON document, and the "code" and "code with scope" types are properly translated to JSON like this:

```
'{"$code": "...", "$scope": {...}}'
```

We still [don't properly parse code and code with scope from JSON](https://jira.mongodb.org/browse/CDRIVER-1913), stay tuned for libbson 1.6.

Other changes:

* bson_json_reader functions now always validate UTF-8.
* JSON parsing now preserves integer width.
* bson_strtoll now matches stroll: it detects range errors, and when
parsing octal it stops at non-octal digits and returns what it parsed
instead of setting errno.
* The configure option "--enable-hardening" had had no effect. It is removed
in favor of system-wide compiler configuration.

# libmongoc

Most changes to the MongoDB C Driver are for MongoDB 3.4 Support. We have a new option you can set in the URI and read preference option, "maxStalenessSeconds", which expresses the maximum staleness a secondary can suffer and still be eligible for reads. I wrote [the spec for the Max Staleness feature](https://github.com/mongodb/specifications/blob/master/source/max-staleness/max-staleness.rst), which applies to all our drivers and to mongos; it's been a challenge but I think we came up with something useful.

Clients now tell MongoDB about the system you're running, the driver you use, and other information that can help you debug the source of your operations. You can set extra MongoDB client handshake data with mongoc_client_set_appname or mongoc_client_pool_set_appname.

We have some writeConcern and readConcern enhancements: all commands that write, like ``createIndexes`` or the ``aggregate`` command with ``$out``, now accept a write concern. We have a new read concern, ``linearizable``, for the most consistency-conscious applications.

MongoDB now supports collation. As with other databases, our collation feature lets you specifiy language-specific rules for sorting strings. There are collation examples for [mongoc_client_read_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_read_command_with_opts.html), [mongoc_collection_count_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_count_with_opts.html), [mongoc_collection_find_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_find_with_opts.html), and [mongoc_index_opt_t](http://mongoc.org/libmongoc/current/mongoc_index_opt_t.html), plus the ["Setting Collation Order" section of the "Bulk Write Operations" guide](http://mongoc.org/libmongoc/current/bulk.html#bulk-write-collation).

Hannes improved TLS support even further. On BSD he fixed our LibreSSL (libssl) support and added LibreSSL (libtls) support. On Windows, we can now build with Secure Channel and Visual Studio 2010. (We'd already built successfully with Secure Channel and Visual Studio 2013 and 2015.) Finally, we now support [Server Name Indication](https://en.wikipedia.org/wiki/Server_Name_Indication) with OpenSSL&mdash;all the other TLS libraries we work with had already supported SNI.

There are additional features for [Application Performance Monitoring](http://mongoc.org/libmongoc/current/application-performance-monitoring.html). You can now register for notifications about server topology changes, such as when a server or topology description changes, and when a monitoring heartbeat begins and succeeds or fails.

We have a stylish new API for executing commands with a flexible set of options passed as a BSON document. Read the docs for [mongoc_collection_find_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_find_with_opts.html) for details, and consult the list of new functions that implement this style:

* [mongoc_client_read_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_read_command_with_opts.html)
* [mongoc_client_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_write_command_with_opts.html)
* [mongoc_client_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_read_write_command_with_opts.html)
* [mongoc_database_read_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_read_command_with_opts.html)
* [mongoc_database_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_write_command_with_opts.html)
* [mongoc_database_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_read_write_command_with_opts.html)
* [mongoc_collection_read_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_read_command_with_opts.html)
* [mongoc_collection_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_write_command_with_opts.html)
* [mongoc_collection_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_read_write_command_with_opts.html)
* [mongoc_gridfs_find_with_opts](http://mongoc.org/libmongoc/current/mongoc_gridfs_find_with_opts.html)
* [mongoc_gridfs_find_one_with_opts](http://mongoc.org/libmongoc/current/mongoc_gridfs_find_one_with_opts.html)
* [mongoc_bulk_operation_remove_one_with_opts](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_remove_one_with_opts.html)
* [mongoc_bulk_operation_remove_many_with_opts](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_remove_many_with_opts.html)
* [mongoc_bulk_operation_replace_one_with_opts](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_replace_one_with_opts.html)
* [mongoc_bulk_operation_update_one_with_opts](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_update_one_with_opts.html)
* [mongoc_bulk_operation_update_many_with_opts](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_update_many_with_opts.html)

I fixed a tricky bug by making the [connectTimeoutMS timer begin **after** DNS resolution](https://jira.mongodb.org/browse/CDRIVER-1571), and reset for each interface attempted (e.g., if the driver first tries IPv6, then IPv4). Besides that bug, we squashed a few others: The random number generator used to select servers is now properly seeded, and secondary queries are now properly distributed according to localThresholdMS, not just to the lowest-latency secondary. The latency estimate is now reset after a connection error. I fixed crashes in mongoc_topology_invalidate_server and mongoc_client_kill_cursor.

I also dramatically improved error reporting when the driver fails to reach the server, and thanks to a bug report from Eliot Horowitz we now correctly distinguish "connection error" and "connection timeout".

# Links:


* [libbson-1.5.0.tar.gz](https://github.com/mongodb/libbson/releases/download/1.5.0/libbson-1.5.0.tar.gz)
* [libmongoc-1.5.0.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.5.0/mongo-c-driver-1.5.0.tar.gz)
* [All bugs fixed in 1.5.0](https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.5.0%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC)
* [Documentation](http://mongoc.org/)

Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Fiona Rowan<li>Ian Boros<li>Remi Collet<li>Brian McCarthy<li>Jeroen Ooms<li>J. Rassi<li>Christoph Schwarz<li>Alexey Vorobeyev<li>Brian Samek</ul>

Peace,<br>
&mdash; A. Jesse Jiryu Davis


<span style="color: gray">Image &copy; A. Jesse Jiryu Davis</span>
