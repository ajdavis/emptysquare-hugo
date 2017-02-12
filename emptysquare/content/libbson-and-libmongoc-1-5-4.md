+++
category = ['C', 'Mongo', 'Programming']
date = '2017-01-30T10:19:34.985038'
description = 'Fixes a bug in cursor iteration with readConcern.'
draft = false
tag = []
thumbnail = 'dive-life-rawscan.jpg'
title = 'Announcing libbson and libmongoc 1.5.4'
type = 'post'
+++

{{< gallery path="libbson-and-libmongoc-1-5-4" >}}

I'm pleased to announce version 1.5.4 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

There is no change to libbson since 1.5.3; we released it to keep pace with libmongoc's version.

The libmongoc release fixes an [error
in cursor iteration when a readConcern is set](https://jira.mongodb.org/browse/CDRIVER-2003). Thanks to Jeremy Mikola and
Hannes Magnusson.


# **Links:**

* [libbson-1.5.4.tar.gz](https://github.com/mongodb/libbson/releases/download/1.5.4/libbson-1.5.4.tar.gz)
* [libmongoc-1.5.4.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.5.4/mongo-c-driver-1.5.4.tar.gz)
* [All bugs fixed in 1.5.4](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17931/)
* [Documentation](http://mongoc.org/)

Peace,<br/>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

<a href="http://www.oldbookillustrations.com/illustrations/dive-life/" style="color: gray">Illustration from Tales of Adventure on the Sea, 1875.</a>
