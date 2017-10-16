+++
category = ['C', 'Mongo', 'Programming']
date = '2017-10-11T22:34:57.995170'
description = 'Fixes some build system bugs related to zlib and snappy compression.'
draft = false
tag = []
thumbnail = 'Potsdam,_steamship_(1900)_-_LoC_4a20322u.jpg'
title = 'Announcing libbson and libmongoc 1.8.1'
type = 'post'
+++

![](Potsdam,_steamship_(1900)_-_LoC_4a20322u.jpg)

I'm pleased to announce version 1.8.1 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

# **libbson**

This release removes a syntax
error in the configure script that affects some shells, and fixes the encoding
of the NEWS file.

# **libmongoc**

This release fixes the following bugs:

* Remove a syntax error in the configure script that affects some shells.
* The configure script respects --with-zlib=system and --with-snappy=system.
* The internal [mongoc_server_description_t](http://mongoc.org/libmongoc/current/mongoc_server_description_t.html) struct is properly reinitialized
after a network error.
* Fix the encoding of the NEWS file.

# **Links:**

* [libbson-1.8.1.tar.gz](https://github.com/mongodb/libbson/releases/download/1.8.1/libbson-1.8.1.tar.gz)
* [libmongoc-1.8.1.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.8.1/mongo-c-driver-1.8.1.tar.gz)
* [All the issues resolved in 1.8.1](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.8.1%22)
* [Documentation](http://mongoc.org/)


Thanks to Jeremy Mikola for his contributions to this release.

Peace,<br>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

***

<a style="color: gray" href="https://commons.wikimedia.org/wiki/File:Potsdam,_steamship_(1900)_-_LoC_4a20322u.jpg">Image: Steamship "Potsdam", Fred Pansing circa 1900</a>
