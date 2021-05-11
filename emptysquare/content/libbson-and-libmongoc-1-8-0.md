+++
category = ['C', 'MongoDB', 'Programming']
date = '2017-09-13T18:02:07.252271'
description = 'Enable network compression on Windows and use select() there, fix a rare crash in libbson.'
draft = false
tag = []
thumbnail = 'the-oaks-5.jpg'
title = 'Announcing libbson and libmongoc 1.8.0'
type = 'post'
+++

![Image description: black and white photograph of a black rock surrounded by waves, seen from above, with surf spraying over one edge of the rock.](the-oaks-5.jpg)

I'm pleased to announce version 1.8.0 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

# **libbson**

New features and bugfixes:

* Make symbols [bson_get_major_version](http://mongoc.org/libbson/current/bson_get_major_version.html), [bson_get_minor_version](http://mongoc.org/libbson/current/bson_get_minor_version.html),
[bson_get_micro_version](http://mongoc.org/libbson/current/bson_get_micro_version.html), [bson_get_version](http://mongoc.org/libbson/current/bson_get_version.html), and [bson_check_version](http://mongoc.org/libbson/current/bson_check_version.html) available
to C++ programs.
* New CMake option ENABLE_MAINTAINER_FLAGS.
* Crash iterating over invalid code with scope.

# **libmongoc**

* The zLib and Snappy compression libraries are bundled if not available.
Wire protocol compression is enabled on Windows.
* [mongoc_collection_find_and_modify_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_find_and_modify_with_opts.html) now respects a "writeConcern"
field in the "extra" BSON document in its [mongoc_find_and_modify_opts_t](http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_t.html).
* These command functions now ignore "read_prefs":
* [mongoc_client_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_read_write_command_with_opts.html),
* [mongoc_database_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_read_write_command_with_opts.html)
* [mongoc_collection_read_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_read_write_command_with_opts.html)
* These functions are both deprecated, use [mongoc_database_write_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_write_command_with_opts.html) instead. [A guide to creating an index using that function has been added](http://mongoc.org/libmongoc/current/create-indexes.html).
* [mongoc_collection_create_index](http://mongoc.org/libmongoc/current/mongoc_collection_create_index.html)
* [mongoc_collection_create_index_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_create_index_with_opts.html)
* [Use select, not WSAPoll, on Windows](https://daniel.haxx.se/blog/2012/10/10/wsapoll-is-broken/).
* Always mark a server "Unknown" after a network error (besides a timeout).
* [mongoc_client_pool_t](http://mongoc.org/libmongoc/current/mongoc_client_pool_t.html) sends platform metadata to the server; before, only a
single [mongoc_client_t](http://mongoc.org/libmongoc/current/mongoc_client_t.html) did.
* New stream method [mongoc_stream_timed_out](http://mongoc.org/libmongoc/current/mongoc_stream_timed_out.html).
* Wire version checks introduced in 1.8.0 will prevent the driver from
connecting to a future MongoDB server version if its wire protocol is
incompatible.
* New CMake option ENABLE_MAINTAINER_FLAGS.

# **Links:**

* [libbson-1.8.0.tar.gz](https://github.com/mongodb/libbson/releases/download/1.8.0/libbson-1.8.0.tar.gz)
* [libmongoc-1.8.0.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.8.0/mongo-c-driver-1.8.0.tar.gz)
* [All bugs fixed in 1.8.0](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.8.0%22)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Jeremy Mikola<li>Kevin Albertson<li>Michael Kuhn</ul>

***

<span style="color: gray">Image &copy; A. Jesse Jiryu Davis</span>
