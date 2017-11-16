+++
category = ['C', 'Mongo', 'Programming']
description = ''
draft = true
tag = []
thumbnail = ''
title = 'Announcing libbson and libmongoc 1.8.2'
type = 'post'
+++

[![Image description: black and white photograph of clam shells densely piled on the shore](the-oaks-10.jpg)](https://www.flickr.com/photos/emptysquare/30459588196)

I'm pleased to announce version 1.8.2 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver. Sadly, this is the final version that I worked on with Hannes Magnusson. He's moved on to fight new bugs on new battlefields.

# **libbson**

No change since 1.8.1; released to keep pace with libmongoc's version.


# **libmongoc**

This release fixes the
following bugs:

  * Remove option to bundle the Snappy compression library, it caused issues
    for programs linking to libmongoc
  * Fix pkg-config and CMake config file flags for programs that statically
    link to libmongoc when libmongoc is statically linked to zLib
  * The configure flag "--with-zlib=no" was ignored
    Crash in authentication when username is NULL


# **Links:**

* [libbson-1.8.2.tar.gz](https://github.com/mongodb/libbson/releases/download/1.8.2/libbson-1.8.2.tar.gz)
* [libmongoc-1.8.2.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.8.2/mongo-c-driver-1.8.2.tar.gz)
* [All the issues resolved in 1.8.2](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.8.2%22)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Derick Rethans<li>Hannes Magnusson<li>Jeremy Mikola</ul>

Peace,<br>
A. Jesse Jiryu Davis

***

<span style="color: gray">Image (c) A. Jesse Jiryu Davis</span>
