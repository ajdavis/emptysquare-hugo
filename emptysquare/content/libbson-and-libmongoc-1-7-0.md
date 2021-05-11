+++
category = ['C', 'MongoDB', 'Programming']
date = '2017-08-09T12:51:14.418308'
description = 'Updated JSON-BSON codec, more resilient network layer, convenient linking.'
draft = false
tag = []
thumbnail = 'USM_steamship_Arctic_1850.jpg'
title = 'Announcing libbson and libmongoc 1.7.0'
type = 'post'
+++

![](USM_steamship_Arctic_1850.jpg)

I'm pleased to announce version 1.7.0 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

The main new features are an updated JSON-BSON codec, more resilient network layer, and convenient linking.

# **libbson**

New features and bug fixes:

* Changes to JSON encoding and decoding:
* New functions [`bson_as_canonical_extended_json`](http://mongoc.org/libbson/current/bson_as_canonical_extended_json.html) and
[`bson_as_relaxed_extended_json`](http://mongoc.org/libbson/current/bson_as_relaxed_extended_json.html) convert BSON to canonical and relaxed
extended JSON according to MongoDB Extended JSON Spec.
Output for the existing [`bson_as_json`](http://mongoc.org/libbson/current/bson_as_json.html) function has not been changed.
* When parsing JSON type wrappers like "$timestamp", any missing or extra
keys are an error.
* The JSON format for BSON regular expressions is now "$regularExpression":
{"pattern": "...", "options": "..."}. The old format {"$regex": "...",
"$options": "..."} is still parsed.
* The JSON format for BSON binary elements is now "$binary": {"base64":
"...", "subType": "..."}. The old format {"$binary": "...", "$type":
"..."} is still parsed.
* BSON dates can be parsed from "$date" as an ISO8601 date or "$numberLong"
as milliseconds since the epoch: "t": {"$date": {"$numberLong": "1234"}}.
Dates can no longer be formatted as raw integers. [`bson_as_json`](http://mongoc.org/libbson/current/bson_as_json.html) writes a
BSON date after 1970 as "$date" with an ISO8601 string, and dates before
1970 as negative milliseconds wrapped in "$numberLong".
[`bson_as_canonical_extended_json`](http://mongoc.org/libbson/current/bson_as_canonical_extended_json.html) always writes dates with "$numberLong".
[`bson_as_relaxed_extended_json`](http://mongoc.org/libbson/current/bson_as_relaxed_extended_json.html) always writes dates with "$date".
* The non-numbers NaN, Infinity, and -Infinity are now recognized (regardless
of case) when parsing JSON.
* CMake build now installs .pc files for programs that link to libbson using
pkg-config. Both the CMake and Autotools build systems now install .cmake
files for programs that link to libbson using CMake. Linking to libbson
statically or dynamically is now much more convenient.
* New CMake option, "ENABLE_STATIC", defaults to ON.
* Minimum required CMake version has been increased to 3.1.
* CMake remains experimental on non-Windows platforms and issues a warning now
* New functions
* [`bson_strcasecmp`](http://mongoc.org/libbson/current/bson_strcasecmp.html), a portable equivalent of strcasecmp.
* [`bson_iter_as_double`](http://mongoc.org/libbson/current/bson_iter_as_double.html), cast the current value to double.
* [`bson_iter_init_from_data`](http://mongoc.org/libbson/current/bson_iter_init_from_data.html), creates an iterator from BSON string.
* [`bson_validate_with_error`](http://mongoc.org/libbson/current/bson_validate_with_error.html), checks a document like [`bson_validate`](http://mongoc.org/libbson/current/bson_validate.html) does but
also reports which key was invalid
* New convenience macros
* `BSON_ITER_HOLDS_INT`, checks if iterator holds int32 or int64
* `BSON_ITER_HOLDS_NUMBER`, checks if iterator holds int32, int64 or double
* Raised BSON recursion limit to 200


# **libmongoc**

New features and bug fixes:

* CMake build now installs .pc files for programs that link to libmongoc using
pkg-config. Both the CMake and Autotools build systems now install .cmake
files for programs that link to libmongoc using CMake. Linking to libmongoc
statically or dynamically is now much more convenient. [See the new tutorial
section "Include and link libmongoc in your C program"](http://mongoc.org/libmongoc/current/tutorial.html#include-and-link-libmongoc-in-your-c-program).
* New CMake option ENABLE_STATIC can be ON, OFF, or AUTO (the default)
* Minimum required CMake version has been increased to 3.1.
* CMake remains experimental on non-Windows platforms and issues a warning now
* Support for wire compression.
* Support for snappy and zlib. MongoDB 3.4 only supports snappy, while zlib
support is expected in MongoDB 3.6.
The enable, configure mongoc like so:
`./configure --with-snappy --with-zlib`
* New functions: `mongoc_uri_get_compressors` and `mongoc_uri_set_compressors`, to
get and set compressor configuration on [`mongoc_uri_t`](http://mongoc.org/libmongoc/current/mongoc_uri_t.html)
* Added support for comma seperated "compressors" connection string option (e.g.
`mongodb://localhost/?compressors=snappy,zlib`)
* Added support for configuring zlib compression level in the connection string
(e.g. `mongodb://localhost/?compressors=zlib&zlibcompressionlevel=8`)
* Now requires the use of CMake config files for libbson to build libmongoc
with CMake
* Added pkg-config support for libressl.
* New function [`mongoc_uri_set_auth_mechanism`](http://mongoc.org/libmongoc/current/mongoc_uri_set_auth_mechanism.html) to update the authentication
mechanism of a [`mongoc_uri_t`](http://mongoc.org/libmongoc/current/mongoc_uri_t.html) after it is created from a string.
* New function [`mongoc_bulk_operation_insert_with_opts`](http://mongoc.org/libmongoc/current/mongoc_bulk_operation_insert_with_opts.html) provides immediate
error checking.
* New function `mongoc_uri_new_with_error` provides a way to parse a connection
string, and retrieve the failure reason, if any.
* Support for MongoDB Connection String specification
* All connection string options are now represented by `MONGOC_URI_xxx` macros
* Paths to Unix Domain Sockets must be url encoded
* Repeated options now issue warnings
* Special characters in username, password and other values must be url encoded
* Unsupported connection string options now issue warnings
* Boolean values can now be represented as true/yes/y/t/1 and false/no/n/f/0.
* Case is now preserved in Unix domain paths.
* New function [`mongoc_cursor_error_document`](http://mongoc.org/libmongoc/current/mongoc_cursor_error_document.html) provides access to server's error
reply if a query or command fails.
* New function [`mongoc_write_concern_is_default`](http://mongoc.org/libmongoc/current/mongoc_write_concern_is_default.html) determines whether any write
concern options have been set, and [`mongoc_read_concern_is_default`](http://mongoc.org/libmongoc/current/mongoc_read_concern_is_default.html) checks if
read concern options are set.
* [`mongoc_gridfs_find_one_with_opts`](http://mongoc.org/libmongoc/current/mongoc_gridfs_find_one_with_opts.html) optimized to use limit 1.

# **Links:**

* [libbson-1.7.0.tar.gz](https://github.com/mongodb/libbson/releases/download/1.7.0/libbson-1.7.0.tar.gz)
* [libmongoc-1.7.0.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.7.0/mongo-c-driver-1.7.0.tar.gz)
* [All bugs fixed in 1.7.0](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17909/)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>Hannes Magnusson<li>A. Jesse Jiryu Davis<li>David Golden<li>Jeremy Mikola<li>Bernard Spil<li>Aleksander Melnikov<li>Adam Seering<li>Remi Collet<li>gael Magnan<li>Hannes Magn?sson<li>David Carlier<li>Paul Melnikow<li>Petr Písař<li>Shane Harvey<li>alexeyvo<li>Greg Rowe</ul>

Peace,<br>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

***

[Image: United States Mail steamship Arctic (launched 1850). Lithograph by N. Currier.](https://en.wikipedia.org/wiki/File:USM_steamship_Arctic_(1850).jpg)
