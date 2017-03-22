+++
category = ['C', 'Mongo', 'Programming']
date = '2017-02-01T21:23:48.446880'
description = 'A new JSON parser, native GSSAPI on Windows, and overhauled docs.'
draft = false
tag = []
thumbnail = 'norman-ship-rawscan.jpg'
title = 'Announcing libbson and libmongoc 1.6.0'
type = 'post'
+++

{{< gallery path="libbson-and-libmongoc-1-6-0" >}}

I'm pleased to announce version 1.6.0 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>,
the libraries constituting the MongoDB C Driver.

# **libbson**

New features and bug fixes:

* Use jsonsl instead of libyajl as our JSON parsing library, parse JSON more
strictly, fix minor parsing bugs.
* Extended JSON documents like ``{"$code": "...", "$scope": {}}`` are now parsed
into BSON "code" elements.
* ISO8601 dates now allow years from 0000 to 9999 inclusive. Before, years
before 1970 were prohibited.
* BSON floats and ints are now distinguished in JSON output.
* The library is now built and continuously tested with MinGW-W64 on Windows.
* The documentation is ported from Mallard XML to ReStructured Text, the
HTML documentation is restyled, and numerous man page syntax errors fixed.
* All public functions now have the ``__cdecl`` calling convention on Windows.

# **libmongoc**

It is my please to announce mongo-c-driver 1.6.0.

New features and bug fixes:

* Enterprise authentication on Windows now uses the native GSSAPI library;
Cyrus SASL is no longer required for enterprise auth on Windows.
* BSON documents are more thoroughly validated before insert or update.
* New function <a href="http://mongoc.org/libmongoc/current/mongoc_uri_set_mechanism_properties.html">mongoc_uri_set_mechanism_properties</a> to replace all the
authMechanismProperties on an existing URI.
* <a href="http://mongoc.org/libmongoc/current/mongoc_uri_get_mechanism_properties.html">mongoc_uri_get_mechanism_properties</a> asserts its inputs are not NULL.
* For consistency with other MongoDB drivers, <a href="http://mongoc.org/libmongoc/current/mongoc_collection_save.html">mongoc_collection_save</a> is
deprecated in favor of <a href="http://mongoc.org/libmongoc/current/mongoc_collection_insert.html">mongoc_collection_insert</a> or <a href="http://mongoc.org/libmongoc/current/mongoc_collection_update.html">mongoc_collection_update</a>.
* The driver is now built and continuously tested with MinGW-W64 on Windows.
* Experimental support for HPUX.
* The correct operation ids are now passed to Command Monitoring callbacks.
* Fix a crash if the driver couldn't connect to the server to create an index.
* The documentation is ported from Mallard XML to ReStructured Text, the
HTML documentation is restyled, and numerous man page syntax errors fixed.
* Getter functions for options in <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_t.html">mongoc_find_and_modify_opts_t</a>:
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_bypass_document_validation.html">mongoc_find_and_modify_opts_get_bypass_document_validation</a>
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_fields.html">mongoc_find_and_modify_opts_get_fields</a>
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_flags.html">mongoc_find_and_modify_opts_get_flags</a>
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_max_time_ms.html">mongoc_find_and_modify_opts_get_max_time_ms</a>
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_sort.html">mongoc_find_and_modify_opts_get_sort</a>
* <a href="http://mongoc.org/libmongoc/current/mongoc_find_and_modify_opts_get_update.html">mongoc_find_and_modify_opts_get_update</a>
* All public functions now have the ``__cdecl`` calling convention on Windows.


# **Links:**

* [libbson-1.6.0.tar.gz](https://github.com/mongodb/libbson/releases/download/1.6.0/libbson-1.6.0.tar.gz)
* [libmongoc-1.6.0.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.6.0/mongo-c-driver-1.6.0.tar.gz)
* [All bugs fixed in 1.6.0](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17213/)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Aleksander Melnikov<li>Jeroen Ooms<li>Brian McCarthy<li>Jonathan Wang<li>Peter Beckman<li>Remi Collet<li>Rockford Wei<li>Alexey Ponomarev<li>Christopher Wang<li>David Golden<li>Jeremy Mikola</ul>

Peace,<br>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

<hr/>

<a style="color: gray" href="http://www.oldbookillustrations.com/illustrations/norman-ship/">Image: Norman Ship, La Librairie Illustrée, 1885</a>
