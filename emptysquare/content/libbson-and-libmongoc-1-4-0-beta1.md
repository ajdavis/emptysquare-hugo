+++
type = "post"
title = "Announcing libbson and libmongoc 1.4.0-beta1"
date = "2016-07-27T23:06:58"
description = "Native TLS on Mac and Windows, a new Command Monitoring API, and dozens of other features."
category = ["C", "Programming", "MongoDB"]
tag = []
enable_lightbox = false
thumbnail = "sea-black-and-white-water-ocean.jpg"
draft = false
+++

<p><img alt="Image Description: grainy black-and-white image of calm ocean with misty sky fading to white at the top" src="sea-black-and-white-water-ocean.jpg"/></p>
<p>I'm pleased to announce version 1.4.0-beta1 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>, the libraries
constituting the MongoDB C Driver.</p>
<h1 id="libbson">libbson</h1>
<p>New features and bug fixes:</p>
<ul>
<li><code>bson_reader_reset</code> seeks to the beginning of a BSON buffer.</li>
<li><code>bson_steal</code> efficiently transfers contents from one <code>bson_t</code> to another.</li>
<li>Fix Windows compile error with <code>BSON_EXTRA_ALIGN</code> disabled.</li>
<li>Potential buffer overrun in <code>bson_strndup</code>.</li>
<li><code>bson_oid_to_string</code> optimization for MS Visual Studio</li>
<li><code>bson_oid_is_valid</code> accepts uppercase hex characters.</li>
<li><code>bson_json_reader_read</code> aborted on some invalid Extended JSON documents.</li>
<li>All man page names now begin with "bson_" to avoid install conflicts.</li>
<li>Fix bug where error messages were sometimes truncated at 63 chars.</li>
</ul>
<p>This release tentatively supports the new BSON decimal type. This feature may
change between now and version 1.5. To try it now, build the library like:</p>

{{<highlight plain>}}
./configure --enable-experimental-features
{{< / highlight >}}

<p>Or:</p>

{{<highlight plain>}}
cmake -DENABLE_EXPERIMENTAL_FEATURES=ON, but this feature may change
{{< / highlight >}}

<h1 id="libmongoc">libmongoc</h1>
<p>The headline features are native TLS on Mac and Windows, and the new implementation of the Command
Monitoring Spec.</p>
<h3 id="tls">TLS</h3>
<p>The driver can now use the native TLS and crypto libraries included in Mac OS X
and Windows. OpenSSL is no longer required for TLS or authentication there. By default, OpenSSL is used if available. In version 2, the default will switch in
version 2.0 to prefer native TLS.</p>
<p>For native TLS on Mac:</p>

{{<highlight plain>}}
./configure --enable-ssl=darwin
{{< / highlight >}}

<p>For Windows:</p>

{{<highlight plain>}}
cmake "-DENABLE_SSL=WINDOWS" -G "Visual Studio 10 Win64" "-DCMAKE_INSTALL_PREFIX=C:\mongo-c-driver"
{{< / highlight >}}

<p>All of the TLS implementations now load the native default certificate store,
with OpenSSL on Windows falling back on the Windows native certificate store if
no other can be found.
The <code>ca_dir</code> field on <code>mongoc_ssl_opt_t</code> is only supported by OpenSSL. All other
fields, including <code>pem_file</code>, are supported by all implementations.
A new field, <code>allow_invalid_hostname</code>, has been added to <code>mongoc_ssl_opt_t</code> and is
preferred over the existing <code>allow_invalid_certificate</code> to disable hostname
verification.
The driver now supports the latest OpenSSL 1.1 in addition to past versions.</p>
<h2 id="application-performance-monitoring">Application Performance Monitoring</h2>
<p>The driver implements the MongoDB <a href="https://github.com/mongodb/specifications/blob/master/source/command-monitoring/command-monitoring.rst">Command Monitoring Spec</a>. Applications can
record the duration and other details of every operation the driver performs on
the server. See "Introduction to Application Performance Monitoring" in the
docs.</p>
<h2 id="error-api">Error API</h2>
<p>New functions <code>mongoc_client_set_error_api</code> and <code>mongoc_client_pool_set_error_api</code>
allow applications to distinguish client and server errors. See the "Error
Reporting" doc.</p>
<h2 id="unacknowledged-write-results">Unacknowledged Write Results</h2>
<p>Unacknowledged writes (writes whose <code>mongoc_write_concern_t</code> "w" value is zero)
now reply with an empty document instead of one with "nInserted": 0, "nUpdated": 0,
and so on.
Command functions now ignore the read preferences set on a client, database,
or collection. Instead, they use the <code>mongoc_read_prefs_t</code> passed in explicitly,
or default to "primary". This change was made to bring them in line with the
<a href="https://github.com/mongodb/specifications/blob/master/source/server-selection/server-selection.rst">Server Selection Spec</a>. These are the affected functions:</p>
<ul>
<li><code>mongoc_client_command</code></li>
<li><code>mongoc_client_command_simple</code></li>
<li><code>mongoc_database_command</code></li>
<li><code>mongoc_database_command_simple</code></li>
<li><code>mongoc_collection_command</code></li>
<li><code>mongoc_collection_command_simple</code></li>
</ul>
<p>On the other hand, the following command-specific helper functions now use the
collection's read preference:</p>
<ul>
<li><code>mongoc_collection_count</code></li>
<li><code>mongoc_collection_stats</code></li>
</ul>
<p>New functions to send maxTimeMS or any arbitrary options with findAndModify:</p>
<ul>
<li><code>mongoc_find_and_modify_opts_set_max_time_ms</code></li>
<li><code>mongoc_find_and_modify_opts_append</code></li>
</ul>
<p>New function to include a write concern with a generic command function
like <code>mongoc_client_command_simple</code>:</p>
<ul>
<li><code>mongoc_write_concern_append</code></li>
</ul>
<h2 id="public-api-for-higher-level-drivers">Public API For Higher-Level Drivers</h2>
<p>New functions support language drivers (specifically the PHP and HHVM drivers)
using only the libmongoc public API:</p>
<ul>
<li><code>mongoc_bulk_operation_get_hint</code></li>
<li><code>mongoc_client_command_simple_with_server_id</code></li>
<li><code>mongoc_client_get_server_description</code></li>
<li><code>mongoc_client_get_server_description_by_id</code></li>
<li><code>mongoc_client_get_server_descriptions</code></li>
<li><code>mongoc_client_select_server</code></li>
<li><code>mongoc_cursor_get_limit</code></li>
<li><code>mongoc_cursor_new_from_command_reply</code></li>
<li><code>mongoc_cursor_set_hint</code></li>
<li><code>mongoc_cursor_set_limit</code></li>
<li><code>mongoc_log_trace_disable</code></li>
<li><code>mongoc_log_trace_enable</code></li>
<li><code>mongoc_server_description_ismaster</code></li>
<li><code>mongoc_server_description_round_trip_time</code></li>
<li><code>mongoc_server_description_type</code></li>
<li><code>mongoc_server_descriptions_destroy_all</code></li>
<li><code>mongoc_uri_get_option_as_bool</code></li>
<li><code>mongoc_uri_get_option_as_int32</code></li>
<li><code>mongoc_uri_get_option_as_utf8</code></li>
<li><code>mongoc_uri_option_is_bool</code></li>
<li><code>mongoc_uri_option_is_int32</code></li>
<li><code>mongoc_uri_option_is_utf8</code></li>
<li><code>mongoc_uri_set_auth_source</code></li>
<li><code>mongoc_uri_set_database</code></li>
<li><code>mongoc_uri_set_option_as_bool</code></li>
<li><code>mongoc_uri_set_option_as_int32</code></li>
<li><code>mongoc_uri_set_option_as_utf8</code></li>
<li><code>mongoc_uri_set_password</code></li>
<li><code>mongoc_uri_set_read_concern</code></li>
<li><code>mongoc_uri_set_read_prefs_t</code></li>
<li><code>mongoc_uri_set_username</code></li>
<li><code>mongoc_uri_set_write_concern</code></li>
<li><code>mongoc_write_concern_is_acknowledged</code></li>
<li><code>mongoc_write_concern_is_valid</code></li>
<li><code>mongoc_write_concern_journal_is_set</code></li>
</ul>
<p>Now that these public APIs are available, the PHP drivers no longer define the
<code>MONGOC_I_AM_A_DRIVER</code> preprocessor symbol to access private APIs. The symbol is
removed from C Driver headers, and libmongoc-priv.so is no longer installed.</p>
<h2 id="other-features">Other Features</h2>
<ul>
<li>New connection string option "localThresholdMS".</li>
<li>zSeries and POWER8 platform support.</li>
<li>Performance enhancements, reduce allocation and copying in command code.</li>
<li>All man page names now begin with "mongoc_" to avoid install conflicts.</li>
<li>New function <code>mongoc_gridfs_file_set_id</code>.</li>
</ul>
<h2 id="deprecations">Deprecations</h2>
<p>Automatically calling <code>mongoc_init</code> and <code>mongoc_cleanup</code> is a GCC-specific feature
that is now deprecated, and will be removed in version 2. The driver should be
built with:</p>

{{<highlight plain>}}
./configure --disable-automatic-init-and-cleanup
{{< / highlight >}}

<p>Or:</p>

{{<highlight plain>}}
cmake "-DENABLE_AUTOMATIC_INIT_AND_CLEANUP=OFF" -G "Visual Studio 10 Win64" "-DCMAKE_INSTALL_PREFIX=C:\mongo-c-driver"
{{< / highlight >}}

<p>In this configuration, applications must explicitly init and cleanup libmongoc.</p>
<p>Deprecated functions:</p>
<ul>
<li><code>mongoc_write_concern_get_fsync</code></li>
<li><code>mongoc_write_concern_set_fsync</code></li>
</ul>
<h2 id="notable-bug-fixes">Notable Bug Fixes</h2>
<ul>
<li><code>mongoc_client_get_database_names</code> no longer filters out a replica set
    member's "local" database.</li>
<li><code>mongoc_client_get_gridfs</code> now ensures the proper indexes on the files and
    chunks collections.</li>
<li>SecondaryPreferred failed if primary matches tags but secondaries don't.</li>
<li><code>mongoc_collection_find_and_modify_with_opts</code> can return true on
    writeConcernError.</li>
<li><code>mongoc_collection_validate</code> doesn't always init "reply".</li>
<li>The strings referred to by <code>mongoc_ssl_opt_t</code>, like "pem_file" and "ca_file", are
    now copied into the client or client pool by <code>mongoc_client_set_ssl_opts</code> or
    <code>mongoc_client_pool_set_ssl_opts</code>, and need not be kept valid afterward.</li>
<li><code>mongoc_collection_count_with_opts</code> ignored flags and read_prefs.</li>
<li>minPoolSize of 0 should mean "no minimum".</li>
<li><code>mongoc_database_create_collection</code> should always use the primary.</li>
<li>The GSSAPI properties SERVICE_NAME and CANONICALIZE_HOST_NAME are now
    properly parsed from the URI. See the "Authentication" doc for details.</li>
<li>Comprehensive compatibility with various C standards and compilers.</li>
</ul>
<h1 id="acknowledgments">Acknowledgments</h1>
<p>Thanks to everyone who contributed to this release.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Ian Boros</li>
<li>Fiona Rowan</li>
<li>Jeremy Mikola</li>
<li>Christoph Schwarz</li>
<li>Mike Lloyd</li>
<li>Remi Collet</li>
<li>Jean-Bernard Jansen</li>
<li>David Hatch</li>
<li>Derick Rethans</li>
<li>Brian Samek</li>
<li>Shane Harvey</li>
<li>Runar Buvik</li>
<li>Raymond Jacobson</li>
<li>Maverick Chan</li>
</ul>
<p>Peace,<br/>
  — A. Jesse Jiryu Davis</p>
<h2 id="links">Links:</h2>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.4.0-beta1/libbson-1.4.0-beta1.tar.gz">libbson-1.4.0-beta1.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.4.0-beta1/mongo-c-driver-1.4.0-beta1.tar.gz">libmongoc-1.4.0-beta1.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=project%20%3D%20CDRIVER%20AND%20fixVersion%20%3D%201.4.0%20ORDER%20BY%20due%20ASC%2C%20priority%20DESC%2C%20created%20ASC">All issues resolved or in progress in 1.4.0</a></li>
<li><a href="http://mongoc.org/libmongoc/current/">Documentation</a></li>
</ul>
<hr/>
<p>Image: <a href="https://unsplash.com/@taylorleopold">Taylor Leopold</a>.</p>
