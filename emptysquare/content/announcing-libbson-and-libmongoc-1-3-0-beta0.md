+++
type = "post"
title = "Announcing libbson and libmongoc 1.3.0-beta0"
date = "2015-11-18T17:42:50"
description = "MongoDB 3.2 features, many fixes and improvements in GridFS, better findAndModify API."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "morecambe-bay@240.jpg"
draft = false
legacyid = "564cfc771e31ec1d5090b5f8"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="morecambe-bay.jpg" alt="Morecambe Bay" title="Morecambe Bay" /></p>
<p>I've just released a beta of the MongoDB C driver 1.3.0, with support for new features in
the upcoming MongoDB 3.2. The driver is compatible with MongoDB 2.4 and later. Please try it out and <a href="https://jira.mongodb.org/browse/CDRIVER">file a ticket in Jira if you see any issues</a>.</p>
<p>Links:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.3.0-beta0/libbson-1.3.0-beta0.tar.gz">libbson-1.3.0-beta0.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.3.0-beta0/mongo-c-driver-1.3.0-beta0.tar.gz">mongo-c-driver-1.3.0-beta0.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%201.3.0-beta0%20AND%20project%20%3D%20CDRIVER">Issues resolved in 1.3.0-beta0</a></li>
<li><a href="http://api.mongodb.org/c/1.3.0/">MongoDB C Driver Documentation</a></li>
</ul>
<p>New features and changes:</p>
<ul>
<li><code>mongoc_collection_find_and_modify</code> will now apply the <code>mongoc_collection_t</code>'s
   <code>write_concern_t</code> when talking to MongoDB 3.2.</li>
<li>Support for MongoDB 3.2's "readConcern" feature for queries, counts, and
   aggregations. The option "readConcernLevel" is now accepted in the MongoDB
   URI. New struct <code>mongoc_read_concern_t</code>, and functions operating on it:<ul>
<li><code>mongoc_client_get_read_concern</code></li>
<li><code>mongoc_client_set_read_concern</code></li>
<li><code>mongoc_database_get_read_concern</code></li>
<li><code>mongoc_database_set_read_concern</code></li>
<li><code>mongoc_collection_get_read_concern</code></li>
<li><code>mongoc_collection_set_read_concern</code></li>
<li><code>mongoc_read_concern_copy</code></li>
<li><code>mongoc_read_concern_destroy</code></li>
<li><code>mongoc_read_concern_get_level</code></li>
<li><code>mongoc_read_concern_new</code></li>
<li><code>mongoc_read_concern_set_level</code></li>
<li><code>mongoc_uri_get_read_concern</code></li>
</ul>
</li>
<li>Support for MongoDB 3.2's "bypassDocumentValidation" option for writes.</li>
<li>New struct <code>mongoc_bulk_write_flags_t</code> and related functions:<ul>
<li><code>mongoc_bulk_operation_set_bypass_document_validation</code></li>
<li><code>mongoc_bulk_operation_set_flags</code></li>
</ul>
</li>
<li>New struct <code>mongoc_find_and_modify_opts_t</code> and related functions:<ul>
<li><code>mongoc_find_and_modify_opts_new</code></li>
<li><code>mongoc_find_and_modify_opts_destroy</code></li>
<li><code>mongoc_find_and_modify_opts_set_sort</code></li>
<li><code>mongoc_find_and_modify_opts_set_update</code></li>
<li><code>mongoc_find_and_modify_opts_set_fields</code></li>
<li><code>mongoc_find_and_modify_opts_set_flags</code></li>
<li><code>mongoc_find_and_modify_opts_set_bypass_document_validation</code></li>
<li><code>mongoc_collection_find_and_modify_with_opts</code></li>
</ul>
</li>
<li>Configurable wait time on tailable cursors with MongoDB 3.2:<ul>
<li><code>mongoc_cursor_get_max_await_time_ms</code></li>
<li><code>mongoc_cursor_set_max_await_time_ms</code></li>
</ul>
</li>
<li>Support for MongoDB 3.2 wire protocol: use commands in place of OP_QUERY,
   OP_GETMORE, and OP_KILLCURSORS messages.</li>
<li>To explain a query plan with MongoDB 3.2, you must now call the "explain"
   command, instead of including the "$explain" key in a mongoc_collection_find
   query. <a href="http://api.mongodb.org/c/1.3.0/mongoc_collection_find.html#explain-command">See the <code>mongoc_collection_find</code> documentation page for details.</a></li>
<li>Use constant-time comparison when verifying credentials</li>
<li>Combine environment's CFLAGS with configure options when building.</li>
<li>Improved man page output and "whatis" entries</li>
</ul>
<p>Extensive bugfixes and improvements in GridFS, including:</p>
<ul>
<li>Handle seeking, reading, and writing past the end of a GridFS file.</li>
<li>Better error reporting if a GridFS file has missing chunks.</li>
<li>Optimization for long seeks forward with <code>mongoc_gridfs_file_seek</code>.</li>
</ul>
<p>Other fixes:</p>
<ul>
<li>Potential crash in <code>bson_strncpy</code> on Windows.</li>
<li>Memory leak in <code>mongoc_database_find_collections</code>.</li>
<li>Set OP_QUERY's nToReturn from the provided limit.</li>
<li>Fix compiler warnings and errors, especially with Visual Studio 2015,
   GCC 4.8, and IBM XL C.</li>
<li>Include missing build script FindSASL2.cmake in distribution tarball</li>
<li>Bugs and typos in tutorial examples</li>
</ul>
<p>Thanks to everyone who contributed to this release.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Kyle Suarez</li>
<li>Matt Cotter</li>
<li>Jose Sebastian Battig</li>
<li>Jeremy Mikola</li>
<li>Iago Rubio</li>
<li>alexeyvo</li>
<li>Jeroen Ooms</li>
<li>Petr P&iacute;sa&#345;</li>
<li>xpol</li>
</ul>
<hr />
<p><a href="https://www.flickr.com/photos/100732098@N06/18166358058"><span style="color:gray">Image: Clive Varley</span></a></p>
