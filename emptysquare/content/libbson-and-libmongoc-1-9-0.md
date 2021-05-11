+++
category = ['C', 'MongoDB', 'Programming']
date = '2017-12-20T21:29:51.104161'
description = 'Support for new MongoDB 3.6 features like change streams and retryable writes.'
draft = false
enable_lightbox = 'true'
tag = []
thumbnail = 'frigate-uss-constitution-rawscan.jpg'
title = 'Announcing libbson and libmongoc 1.9.0'
type = 'post'
+++

![](frigate-uss-constitution-rawscan.jpg)

I'm pleased to announce version 1.9.0 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

# **libbson**

It is my pleasure to announce Libbson-1.9.0.

New features and bugfixes:

  * Fix Autotools syntax for OpenBSD and any platform lacking stdint.h.
  * Fix Android NDK incompatibilities.
  * Fix a one-byte write past the end of a buffer in bson_decimal128_to_string.
  * Avoid reading past the end of a string that contains UTF-8 multibyte NIL.
  * Fix some pedantic warnings in C99 mode.


# **libmongoc**

It is my pleasure to announce mongo-c-driver 1.9.0. This version drops support
for MongoDB 2.4 and adds support for MongoDB 3.6 features:

  * New struct [mongoc_change_stream_t](http://mongoc.org/libmongoc/current/mongoc_change_stream_t.html) to watch a collection for changes.
  * New struct [mongoc_client_session_t](http://mongoc.org/libmongoc/current/mongoc_client_session_t.html) represents a MongoDB 3.6 session,
    which supports causal consistency: you are guaranteed to read your writes
    and to perform monotonic reads, even when reading from secondaries or in
    a sharded cluster.
  * New functions that accept flexible options as a BSON document. These
    accept a "sessionId" option and any future options. In addition, the
    two new "update" functions accept the "arrayFilters" option that is new
    in MongoDB 3.6:
      * [mongoc_collection_insert_one](http://mongoc.org/libmongoc/current/mongoc_collection_insert_one.html)
      * [mongoc_collection_insert_many](http://mongoc.org/libmongoc/current/mongoc_collection_insert_many.html)
      * [mongoc_collection_update_one](http://mongoc.org/libmongoc/current/mongoc_collection_update_one.html)
      * [mongoc_collection_update_many](http://mongoc.org/libmongoc/current/mongoc_collection_update_many.html)
      * [mongoc_collection_replace_one](http://mongoc.org/libmongoc/current/mongoc_collection_replace_one.html)
      * [mongoc_collection_delete_one](http://mongoc.org/libmongoc/current/mongoc_collection_delete_one.html)
      * [mongoc_collection_delete_many](http://mongoc.org/libmongoc/current/mongoc_collection_delete_many.html)
      * [mongoc_client_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_command_with_opts.html)
      * [mongoc_database_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_command_with_opts.html)
      * [mongoc_collection_command_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_command_with_opts.html)
      * [mongoc_client_find_databases_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_find_databases_with_opts.html)
      * [mongoc_client_get_database_names_with_opts](http://mongoc.org/libmongoc/current/mongoc_client_get_database_names_with_opts.html)
      * [mongoc_collection_create_bulk_operation_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_create_bulk_operation_with_opts.html)
      * [mongoc_collection_find_indexes_with_opts](http://mongoc.org/libmongoc/current/mongoc_collection_find_indexes_with_opts.html)
      * [mongoc_database_find_collections_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_find_collections_with_opts.html)
      * [mongoc_database_get_collection_names_with_opts](http://mongoc.org/libmongoc/current/mongoc_database_get_collection_names_with_opts.html)
  * New URI option "retryWrites=true" safely and automatically retries certain
    write operations if the server is a MongoDB 3.6 replica set or sharded
    cluster.
  * Support for MongoDB OP_MSG wire protocol.

Additional changes not specific to MongoDB 3.6:

  * Support for mongodb+srv URIs to query DNS for SRV and TXT records that
    configure the connection to MongoDB.
  * Support LibreSSL with CMake build
  * The "minPoolSize" URI option is deprecated: it's confusing and not useful.

Bug fixes:

  * [mongoc_bulk_operation_execute](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_execute.html) did not always initialize "reply".
  * Fix C99 pedantic warnings.


# **Links:**

* [libbson-1.9.0.tar.gz](https://github.com/mongodb/libbson/releases/download/1.9.0/libbson-1.9.0.tar.gz)
* [libmongoc-1.9.0.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.9.0/mongo-c-driver-1.9.0.tar.gz)
* [All the issues resolved in 1.9.0](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.9.0%22)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Jeremy Mikola<li>Kevin Albertson<li>Jeroen Ooms<li>Iulian Rotaru<li>Derick Rethans<li>Graham Whitted<li>Brian Moss<li>Alex Masterov<li>Michael Kuhn<li>Sriharsha Vardhan<li>Jean-Marc Le Roux<li>Dimitri Gence</ul><p><br>
Peace,<br>
A. Jesse Jiryu Davis</p>

***

<a style="color: gray" href="https://www.oldbookillustrations.com/illustrations/frigate-uss-constitution/">Image: the frigate USS Constitution, in Nouveau dictionnaire encyclopédique universel illustré, circa 1885</a>
