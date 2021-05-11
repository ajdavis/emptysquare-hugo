+++
category = ['C', 'MongoDB', 'Programming']
date = '2018-01-11T22:48:08.337713'
description = 'Fixes a mistake that causes a compile error in a macro definition.'
draft = false
enable_lightbox = true
tag = []
thumbnail = 'arctic.png'
title = 'Announcing libbson and libmongoc 1.9.2'
type = 'post'
+++

I made a mistake in libbson 1.9.1, so I've just released 1.9.2 of libbson and libmongoc.

libbson 1.9.2 completes reverting a
changed macro definition that broke API compatibility. The revert in 1.9.1 did
not completely fix the BC break. Thanks to Petr Písař for finding and fixing the
mistake. See [CDRIVER-2460](https://jira.mongodb.org/browse/CDRIVER-2460) for details. It's a comedy of errors.

libmongoc 1.9.2 has no changes since 1.9.1, I released it to keep pace with libbson's version number.

# **Links:**

* [libbson-1.9.2.tar.gz](https://github.com/mongodb/libbson/releases/download/1.9.2/libbson-1.9.2.tar.gz)
* [libmongoc-1.9.2.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.9.2/mongo-c-driver-1.9.2.tar.gz)
* [All the issues resolved in 1.9.2](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.9.2%22)
* [Documentation](http://mongoc.org/)

***

As [Jacob Kaplan-Moss said](https://www.youtube.com/watch?v=hIJdFxYlEKE), I too am a mediocre programmer. But the great thing about mistakes in code is they're easy to fix.

I like to accompany my blog posts about C with a sea-themed image, but on this occasion I will share a sea-themed video. It's extraordinary 360-degree footage under the Arctic ice, from the New York Times. Please accept it by way of an apology from me for my clumsiness.

Peace,<br>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

<iframe width="560" height="315" src="https://www.youtube.com/embed/ecmGq5LGNx8" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
