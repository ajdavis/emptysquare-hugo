+++
category = ['C', 'Mongo', 'Programming']
date = '2018-01-09T17:46:11.089954'
description = 'Revert an incompatible change to a macro definition, fix an off-by-one bug in regexes.'
draft = false
enable_lightbox = true
tag = []
thumbnail = 'Sea-monster_Terme_di_Nettuno_Ostia_Antica_2006-09-08.jpg'
title = 'Announcing libbson and libmongoc 1.9.1'
type = 'post'
+++

![Image description: black and white mosaic of a creature with the head and paws of a lion and the lower body and tail of a snake, with three-lobed fish tail. It appears to have cartoonish ripple lines drawn with mosaic tile around its paws showing it is paddling, and lines beneath it showing forward motion.](Sea-monster_Terme_di_Nettuno_Ostia_Antica_2006-09-08.jpg)

I'm pleased to announce version 1.9.1 of libbson and libmongoc,
the libraries constituting the MongoDB C Driver.

# **libbson**

This release reverts a changed
macro definition that broke API compatibility, and fixes an off-by-one error
in [bson_append_regex](http://mongoc.org/libbson/current/bson_append_regex.html) that resulted in corrupt BSON, thanks to Derick Rethans.

# **libmongoc**

We fixed a bug
that caused session ID to be included in authentication and server monitoring
commands. Thanks to Jeremy Mikola for finding and fixing the issue.

# **Links:**

* [libbson-1.9.1.tar.gz](https://github.com/mongodb/libbson/releases/download/1.9.1/libbson-1.9.1.tar.gz)
* [libmongoc-1.9.1.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.9.1/mongo-c-driver-1.9.1.tar.gz)
* [All the issues resolved in 1.9.1](https://jira.mongodb.org/issues/?jql=project%3D%22C%20Driver%22%20and%20fixVersion%3D%221.9.1%22)
* [Documentation](http://mongoc.org/)

Peace,<br/>
&nbsp;&nbsp;&mdash; A. Jesse Jiryu Davis

***

<a href="https://commons.wikimedia.org/wiki/File:Sea-monster_Terme_di_Nettuno_Ostia_Antica_2006-09-08.jpg" style="color: gray">Image: Sea-monster, detail of a mosaic representing Poseidon. Room 4 of the Baths of Neptune, Ostia Antica, Latium, Italy.</a>
