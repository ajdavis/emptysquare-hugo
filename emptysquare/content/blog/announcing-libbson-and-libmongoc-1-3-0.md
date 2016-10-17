+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.0"
date = "2015-12-07T21:09:33"
description = "Supports MongoDB 3.2."
"blog/category" = ["C", "Mongo", "Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "catania@240.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="catania.jpg" alt="San Giovanni li Cuti - Catania" title="San Giovanni li Cuti - Catania" /></p>
<p>I just released version 1.3.0 of libbson and libmongoc, the C libraries that compose the MongoDB C Driver. The changelist is massive; the highlights are support for new MongoDB 3.2 features, and a widespread cleanup of GridFS.</p>
<p>Links:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.0/libbson-1.3.0.tar.gz">libbson-1.3.0.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.0/mongo-c-driver-1.3.0.tar.gz">libmongoc-1.3.0.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?filter=18525">All features and bugfixes in 1.3.0</a></li>
<li><a href="http://api.mongodb.org/c/">Documentation for libmongoc</a></li>
</ul>
<h1 id="libbson">libbson</h1>
<p>Since the release candidate libbson 1.3.0-rc0, the only changes have been fixes for compiler warnings and errors on various platforms.</p>
<p>All changes since the previous stable release, libbson 1.2.1:</p>
<ul>
<li>Fix potential crash in bson_strncpy on Windows.</li>
<li>Parse DBRefs correctly from JSON.</li>
<li>CMake option to disable building tests: "cmake -DENABLE_TESTS:BOOL=OFF".</li>
<li>Refactor the build system to declare library version in one place.</li>
<li>Fix compiler warnings and errors, especially with Visual Studio 2015
    and IBM XL C.</li>
<li>Combine environment's CFLAGS with configure options when building.</li>
</ul>
<h1 id="libmongoc">libmongoc</h1>
<p>Changes since the the release candidate, libmongoc 1.3.0-rc0:</p>
<ul>
<li>Fix a cursor bug introduced on big-endian platforms in 1.3.0-beta0.</li>
<li>Improve documentation for mongoc_host_list_t.</li>
<li>Move private mongoc_host_list_t functions from public header.</li>
<li>Refactor the build system to declare library version in one place.</li>
</ul>
<p>All new features and changes since the previous stable release, libmongoc 1.2.1:</p>
<ul>
<li>If the driver is compiled without SSL support but a URI with "ssl=true"
    is passed to mongoc_client_new, mongoc_client_new_from_uri, or
    mongoc_client_pool_new, the function logs an error and returns NULL. Before,
    the driver would attempt a non-SSL connection.</li>
<li>mongoc_collection_find_and_modify will now apply the mongoc_collection_t's
    write_concern_t when talking to MongoDB 3.2.</li>
<li>Support for MongoDB 3.2's "readConcern" feature for queries, counts, and
    aggregations. The option "readConcernLevel" is now accepted in the MongoDB
    URI. New struct mongoc_read_concern_t, and functions operating on it:</li>
<li>mongoc_client_get_read_concern</li>
<li>mongoc_client_set_read_concern</li>
<li>mongoc_database_get_read_concern</li>
<li>mongoc_database_set_read_concern</li>
<li>mongoc_collection_get_read_concern</li>
<li>mongoc_collection_set_read_concern</li>
<li>mongoc_read_concern_copy</li>
<li>mongoc_read_concern_destroy</li>
<li>mongoc_read_concern_get_level</li>
<li>mongoc_read_concern_new</li>
<li>mongoc_read_concern_set_level</li>
<li>mongoc_uri_get_read_concern</li>
<li>Support for MongoDB 3.2's "bypassDocumentValidation" option for writes.</li>
<li>New struct mongoc_bulk_write_flags_t and related functions:</li>
<li>mongoc_bulk_operation_set_bypass_document_validation</li>
<li>New struct mongoc_find_and_modify_opts_t and related functions:</li>
<li>mongoc_find_and_modify_opts_new</li>
<li>mongoc_find_and_modify_opts_destroy</li>
<li>mongoc_find_and_modify_opts_set_sort</li>
<li>mongoc_find_and_modify_opts_set_update</li>
<li>mongoc_find_and_modify_opts_set_fields</li>
<li>mongoc_find_and_modify_opts_set_flags</li>
<li>mongoc_find_and_modify_opts_set_bypass_document_validation</li>
<li>mongoc_collection_find_and_modify_with_opts</li>
<li>New functions to copy database and collection handles:</li>
<li>mongoc_collection_copy</li>
<li>mongoc_database_copy</li>
<li>Support for MongoDB 3.2 wire protocol: use commands in place of OP_QUERY,
    OP_GETMORE, and OP_KILLCURSORS messages.</li>
<li>To explain a query plan with MongoDB 3.2, you must now call the "explain"
    command, instead of including the "$explain" key in a mongoc_collection_find
    query. See the mongoc_collection_find documentation page for details.</li>
<li>Configurable wait time on tailable cursors with MongoDB 3.2:</li>
<li>mongoc_cursor_get_max_await_time_ms</li>
<li>mongoc_cursor_set_max_await_time_ms</li>
<li>Use electionId to detect a stale replica set primary during a network split.</li>
<li>Disconnect from replica set members whose "me" field does not match the
    connection address.</li>
<li>The client side matching feature, mongoc_matcher_t and related functions,
    are deprecated and scheduled for removal in version 2.0.</li>
<li>New CMake options ENABLE_SSL, ENABLE_SASL, ENABLE_TESTS, and ENABLE_EXAMPLES.</li>
<li>Use constant-time comparison when verifying credentials.</li>
<li>Combine environment's CFLAGS with configure options when building.</li>
<li>Improved man page output and "whatis" entries.</li>
</ul>
<p>There are extensive bugfixes and improvements in GridFS since 1.2.1, including:</p>
<ul>
<li>Handle seeking, reading, and writing past the end of a GridFS file.</li>
<li>If a GridFS chunk is missing, mongoc_gridfs_file_readv sets file-&gt;error to
    domain MONGOC_ERROR_GRIDFS and a new code MONGOC_ERROR_GRIDFS_CHUNK_MISSING.</li>
<li>Optimization for long seeks forward with mongoc_gridfs_file_seek.</li>
</ul>
<p>Other fixes since 1.2.1:</p>
<ul>
<li>Memory leaks in mongoc_database_has_collection and mongoc_cursor_next.</li>
<li>Report writeConcern failures from findAndModify and from legacy writes.</li>
<li>Memory leak in mongoc_database_find_collections.</li>
<li>Set OP_QUERY's nToReturn from the provided limit.</li>
<li>Fix compiler warnings and errors, especially with Visual Studio 2015,
    GCC 4.8, and IBM XL C.</li>
<li>Bugs and typos in tutorial examples.</li>
</ul>
<p>Thanks to everyone who contributed to this release.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Kyle Suarez</li>
<li>Jose Sebastian Battig</li>
<li>Matt Cotter</li>
<li>Claudio Canella</li>
<li>alexeyvo</li>
<li>Christopher Wang</li>
<li>Flavio Medeiros</li>
<li>Iago Rubio</li>
<li>Jeremy Mikola</li>
<li>Victor Leschuk</li>
<li>Mark Benvenuto</li>
<li>Petr P&iacute;sa&#345;</li>
<li>xpol</li>
<li>Jeroen Ooms</li>
<li>Jason Carey</li>
</ul>
<p>Peace,<br />
 &mdash; A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://www.flickr.com/photos/somemixedstuff/517880144/"><span style="color:gray">Image: Davide Restivo</span></a></p>
    