+++
type = "post"
title = "Announcing libbson and libmongoc 1.4.0"
date = "2016-08-10T18:46:01"
description = "Now with native TLS on Mac and Windows, no need for OpenSSL there."
category = ["C", "Programming", "Mongo"]
tag = []
enable_lightbox = false
thumbnail = "steamship@240.jpg"
draft = false
+++

<p><img alt="Image description: black and white etching of large steamship in harbor. A few sailors appear tiny in the foreground. Smoke billows from a single wide smokestack amidships." src="steamship.jpg" /></p>
<p>I'm pleased to announce version 1.4.0 of libbson and libmongoc, the libraries
constituting the MongoDB C Driver. This is a very big release a long time coming.</p>
<p>The headline feature is support for the TLS libraries included in Mac and Windows, so you no longer need OpenSSL there. Hannes Magnusson built this feature off contributions by Samantha Ritter and Mark Benvenuto. He overcame months of frustrations and roadblocks to achieve a secure, production-quality implementation; it's an extraordinary achievement.</p>
<hr />
<div class="toc">
<ul>
<li><a href="#libbson">libbson</a></li>
<li><a href="#libmongoc">libmongoc</a><ul>
<li><a href="#tls">TLS</a></li>
<li><a href="#application-performance-monitoring">Application Performance Monitoring</a></li>
<li><a href="#error-api">Error API</a></li>
<li><a href="#unacknowledged-write-results">Unacknowledged Write Results</a></li>
<li><a href="#public-api-for-higher-level-drivers">Public API For Higher-Level Drivers</a></li>
<li><a href="#other-features">Other Features</a></li>
<li><a href="#deprecations">Deprecations</a></li>
<li><a href="#notable-bug-fixes">Notable Bug Fixes</a></li>
</ul>
</li>
<li><a href="#links">Links</a></li>
<li><a href="#acknowledgments">Acknowledgments</a></li>
</ul>
</div>
<h1 id="libbson">libbson</h1>
<p>New features and bug fixes:</p>
<ul>
<li>bson_reader_reset seeks to the beginning of a BSON buffer.</li>
<li>bson_steal efficiently transfers contents from one bson_t to another.</li>
<li>Fix Windows compile error with BSON_EXTRA_ALIGN disabled.</li>
<li>Potential buffer overrun in bson_strndup.</li>
<li>bson_oid_to_string optimization for MS Visual Studio</li>
<li>bson_oid_is_valid accepts uppercase hex characters.</li>
<li>bson_json_reader_read aborted on some invalid Extended JSON documents.</li>
<li>All man page names now begin with "bson_" to avoid install conflicts.</li>
<li>Error messages sometimes truncated at 63 chars.</li>
</ul>
<p>This release tentatively supports the new BSON decimal type when built like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">./configure --enable-experimental-features
</pre></div>


<p>Or:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cmake -DENABLE_EXPERIMENTAL_FEATURES=ON
</pre></div>


<p>This feature may change between now and libbson 1.5.</p>
<h1 id="libmongoc">libmongoc</h1>
<h2 id="tls">TLS</h2>
<p>The driver can now use the native TLS and crypto functions included in Mac OS X
and Windows. OpenSSL is no longer required for TLS or authentication on Mac or
Windows. By default, OpenSSL is used if available, the default will switch in
version 2.0 to prefer native TLS.</p>
<p>For native TLS on Mac:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">./configure --enable-ssl=darwin
</pre></div>


<p>For Windows:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cmake &quot;-DENABLE_SSL=WINDOWS&quot; -G &quot;Visual Studio 10 Win64&quot; &quot;-DCMAKE_INSTALL_PREFIX=C:\mongo-c-driver&quot;
</pre></div>


<p>All of the TLS implementations now load the native default certificate store,
with OpenSSL on Windows falling back on the Windows native certificate store if
no other can be found.</p>
<p>The "ca_dir" field on mongoc_ssl_opt_t is only supported by OpenSSL. All other
fields, including "pem_file", are supported by all implementations.</p>
<p>A new field, "allow_invalid_hostname", has been added to mongoc_ssl_opt_t and is
preferred over the existing "allow_invalid_certificate" to disable hostname
verification.</p>
<p><a href="https://api.mongodb.com/c/current/mongoc_ssl_opt_t.html">See the documentation for mongoc_ssl_opt_t for details.</a></p>
<p>The driver now supports the latest OpenSSL 1.1 in addition to past versions.</p>
<h2 id="application-performance-monitoring">Application Performance Monitoring</h2>
<p>The driver implements the MongoDB Command Monitoring Spec. Applications can
record the duration and other details of every operation the driver performs on
the server. See <a href="https://api.mongodb.com/c/current/application-performance-monitoring.html">Introduction to Application Performance Monitoring</a> in the
docs.</p>
<h2 id="error-api">Error API</h2>
<p>New functions mongoc_client_set_error_api and mongoc_client_pool_set_error_api
allow applications to distinguish client and server errors. <a href="https://api.mongodb.com/c/current/errors.html">See the "Error Reporting" doc</a>.</p>
<h2 id="unacknowledged-write-results">Unacknowledged Write Results</h2>
<p>Unacknowledged writes (writes whose mongoc_write_concern_t "w" value is zero)
now reply with an empty document instead of one with nInserted: 0, nUpdated: 0,
and so on.</p>
<p>Command functions now ignore the read preferences set on a client, database,
or collection. Instead, they use the mongoc_read_prefs_t passed in explicitly,
or default to "primary". This change was made to bring them in line with the
Server Selection Spec. These are the affected functions:</p>
<ul>
<li>mongoc_client_command</li>
<li>mongoc_client_command_simple</li>
<li>mongoc_database_command</li>
<li>mongoc_database_command_simple</li>
<li>mongoc_collection_command</li>
<li>mongoc_collection_command_simple</li>
</ul>
<p>On the other hand, the following command-specific helper functions now use the
collection's read preference:</p>
<ul>
<li>mongoc_collection_count</li>
<li>mongoc_collection_stats</li>
</ul>
<p>New functions to send maxTimeMS or any arbitrary options with findAndModify:</p>
<ul>
<li>mongoc_find_and_modify_opts_set_max_time_ms</li>
<li>mongoc_find_and_modify_opts_append</li>
</ul>
<p>New function to include a write concern with a generic command function
like mongoc_client_command_simple:</p>
<ul>
<li>mongoc_write_concern_append</li>
</ul>
<h2 id="public-api-for-higher-level-drivers">Public API For Higher-Level Drivers</h2>
<p>New functions support language drivers (specifically the PHP and HHVM drivers)
using only the libmongoc public API:</p>
<ul>
<li>mongoc_bulk_operation_get_hint</li>
<li>mongoc_client_command_simple_with_server_id</li>
<li>mongoc_client_get_server_description</li>
<li>mongoc_client_get_server_description_by_id</li>
<li>mongoc_client_get_server_descriptions</li>
<li>mongoc_client_select_server</li>
<li>mongoc_cursor_get_limit</li>
<li>mongoc_cursor_new_from_command_reply</li>
<li>mongoc_cursor_set_hint</li>
<li>mongoc_cursor_set_limit</li>
<li>mongoc_log_trace_disable</li>
<li>mongoc_log_trace_enable</li>
<li>mongoc_server_description_ismaster</li>
<li>mongoc_server_description_round_trip_time</li>
<li>mongoc_server_description_type</li>
<li>mongoc_server_descriptions_destroy_all</li>
<li>mongoc_uri_get_option_as_bool</li>
<li>mongoc_uri_get_option_as_int32</li>
<li>mongoc_uri_get_option_as_utf8</li>
<li>mongoc_uri_option_is_bool</li>
<li>mongoc_uri_option_is_int32</li>
<li>mongoc_uri_option_is_utf8</li>
<li>mongoc_uri_set_auth_source</li>
<li>mongoc_uri_set_database</li>
<li>mongoc_uri_set_option_as_bool</li>
<li>mongoc_uri_set_option_as_int32</li>
<li>mongoc_uri_set_option_as_utf8</li>
<li>mongoc_uri_set_password</li>
<li>mongoc_uri_set_read_concern</li>
<li>mongoc_uri_set_read_prefs_t</li>
<li>mongoc_uri_set_username</li>
<li>mongoc_uri_set_write_concern</li>
<li>mongoc_write_concern_is_acknowledged</li>
<li>mongoc_write_concern_is_valid</li>
<li>mongoc_write_concern_journal_is_set</li>
</ul>
<p>Now that these public APIs are available, the PHP drivers no longer define the
MONGOC_I_AM_A_DRIVER preprocessor symbol to access private APIs. The symbol is
removed from C Driver headers, and libmongoc-priv.so is no longer installed.</p>
<h2 id="other-features">Other Features</h2>
<ul>
<li>New connection string option "localThresholdMS".</li>
<li>zSeries, POWER8, and ARM 64-bit platform support.</li>
<li>Performance enhancements, reduce allocation and copying in command code.</li>
<li>All man page names now begin with "mongoc_" to avoid install conflicts.</li>
<li>New function mongoc_gridfs_file_set_id.</li>
</ul>
<h2 id="deprecations">Deprecations</h2>
<p>Automatically calling mongoc_init and mongoc_cleanup is a GCC-specific feature
that is now deprecated, and will be removed in version 2. The driver should be
built with:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">./configure --disable-automatic-init-and-cleanup
</pre></div>


<p>Or:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">cmake &quot;-DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF&quot; -G &quot;Visual Studio 10 Win64&quot; &quot;-DCMAKE_INSTALL_PREFIX=C:\mongo-c-driver&quot;
</pre></div>


<p>In this configuration, applications must explicitly init and cleanup libmongoc.</p>
<p>Deprecated functions:</p>
<ul>
<li>mongoc_write_concern_get_fsync</li>
<li>mongoc_write_concern_set_fsync</li>
</ul>
<h2 id="notable-bug-fixes">Notable Bug Fixes</h2>
<ul>
<li>Logic bugs using tag sets to select replica set members with complex configs</li>
<li>mongoc_client_get_database_names no longer filters out a replica set
    member's "local" database.</li>
<li>mongoc_client_get_gridfs now ensures the proper indexes on the files and
    chunks collections.</li>
<li>SecondaryPreferred fails if primary matches tags but secondaries don't.</li>
<li>mongoc_collection_find_and_modify_with_opts can return true on
    writeConcernError.</li>
<li>mongoc_collection_validate doesn't always init "reply".</li>
<li>The strings referred to by mongoc_ssl_opt_t, like pem_file and ca_file, are
    now copied into the client or client pool by mongoc_client_set_ssl_opts or
    mongoc_client_pool_set_ssl_opts, and need not be kept valid afterward.</li>
<li>mongoc_collection_count_with_opts ignored flags and read_prefs.</li>
<li>minPoolSize of 0 should mean "no minimum".</li>
<li>mongoc_database_create_collection should always use the primary.</li>
<li>The GSSAPI properties SERVICE_NAME and CANONICALIZE_HOST_NAME are now
    properly parsed from the URI, <a href="https://api.mongodb.com/c/current/authentication.html">see the "Authentication" doc for details</a>.</li>
<li>Comprehensive compatibility with various C standards and compilers.</li>
<li>mongoc_bulk_operation_execute didn't initialize "reply" if it was passed
    invalid arguments.</li>
</ul>
<h1 id="links">Links</h1>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.4.0/libbson-1.4.0.tar.gz">libbson-1.4.0.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.4.0/mongo-c-driver-1.4.0.tar.gz">libmongoc-1.4.0.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.4.0%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All bugs fixed in 1.4.0</a></li>
<li><a href="https://api.mongodb.org/c/">Documentation</a></li>
</ul>
<h1 id="acknowledgments">Acknowledgments</h1>
<p>Thanks to everyone who contributed to this release.</p>
<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Ian Boros<li>Fiona Rowan<li>Jeremy Mikola<li>Christoph Schwarz<li>Remi Collet<li>Derick Rethans<li>Mike Lloyd<li>David Hatch<li>Brian Samek<li>Jean-Bernard Jansen<li>Shane Harvey<li>Runar Buvik<li>Raymond Jacobson<li>ReadmeCritic<li>Maverick Chan</ul>

<p>Peace,<br />
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis</p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Potsdam,_steamship_(1900)_-_LoC_4a20852u.jpg">Image: Steamship in Potsdam Harbor, circa 1900.</a></p>
