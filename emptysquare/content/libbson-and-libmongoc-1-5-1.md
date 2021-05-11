+++
category = ['C', 'MongoDB', 'Programming']
date = '2016-12-17T14:25:39.357252'
description = 'Crash on NUMA, better errors from auth, OpenSSL build fixes.'
draft = false
tag = []
thumbnail = 'the-oaks-8.jpg'
title = 'Announcing libbson and libmongoc 1.5.1'
type = 'post'
+++

[![](the-oaks-8.jpg)](https://www.flickr.com/photos/emptysquare/30459585206/in/photolist-NpBmL9-NpBmnJ-NpBkSf-NpBkub-NpBk2h-NpBjAs-N1tond-N1tnhN-NpBiFG)

I'm pleased to announce version 1.5.1 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>,
the libraries constituting the MongoDB C Driver.

## **libbson**

No change since 1.5.0; released to keep pace with libmongoc's version.


## **libmongoc**

This is a bugfix release:

* Fix SEGFAULT with performance counters on NUMA (thanks to Jonathan Wang).
* Prevent rare assertion error in mongoc_cluster_stream_for_server.
* Improve error messages from auth failure.
* Escape quotes when appending CFLAGS to handshake metadata.
* Fix OpenSSL header lookups in non-default paths.
* Fix build failure with LibreSSL.

## **Links:**


* [libbson-1.5.1.tar.gz](https://github.com/mongodb/libbson/releases/download/1.5.1/libbson-1.5.1.tar.gz)
* [libmongoc-1.5.1.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.5.1/mongo-c-driver-1.5.1.tar.gz)
* [All bugs fixed in 1.5.1](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17727/)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Hannes Magnusson<li>Jeroen Ooms<li>Jonathan Wang</ul>

Peace,<br>
A. Jesse Jiryu Davis
