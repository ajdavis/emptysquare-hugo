+++
category = ['C', 'Mongo', 'Programming']
date = '2017-01-11T18:21:41.540710'
description = 'Fixes bugs in Windows TLS, building with MinGW or on FreeBSD, and complex queries.'
draft = false
tag = []
thumbnail = 'monstrosity.png'
title = 'Announcing libbson and libmongoc 1.5.3'
type = 'post'
+++

![](monstrosity.png)

I'm pleased to announce version 1.5.3 of libbson and libmongoc, the libraries constituting the MongoDB C Driver.

# libbson

This is a patch release that fixes [a build error with MinGW on Windows](https://jira.mongodb.org/browse/CDRIVER-1982).

# libmongoc

This release fixes the following bugs:

* [CDRIVER-1964](https://jira.mongodb/org/browse/CDRIVER-1964): Windows CA stores should be opened with read-only flag
* [CDRIVER-1970](https://jira.mongodb/org/browse/CDRIVER-1970): Conflicting symbols MAX and MIN on FreeBSD
* [CDRIVER-1971](https://jira.mongodb/org/browse/CDRIVER-1971): Missing exports of some GridFS functions
* [CDRIVER-1975](https://jira.mongodb/org/browse/CDRIVER-1975): Mixed $ and non-$ query operators should be allowed


There was a glitch on the road from 1.5.1 to this release, 1.5.3. We tried to update the driver to connect to IPv6-only MongoDB servers by hostname, ([CDRIVER-1972](https://jira.mongodb/org/browse/CDRIVER-1972)). For example, if the server listening on example.com only accepts IPv6 connections, we should be able to connect to it with the URI `mongodb://example.com`. Unfortunately we messed this up: if the server only accepts IPv4, we'd try IPv6 first, time out, and we did not then fall back to IPv4 ([CDRIVER-1988](https://jira.mongodb/org/browse/CDRIVER-1988)).

That bug was released in version 1.5.2 yesterday. I've pulled 1.5.2 from GitHub. Version 1.5.3 reverts to the old behavior: it connects to MongoDB over IPv6 if given an IPv6 connection string like `mongodb://[::1]`, and requires an IPv4 connection when given a hostname like `mongodb://example`. At some point we'll implement the desired behavior correctly.

# **Links:**

* [libbson-1.5.3.tar.gz](https://github.com/mongodb/libbson/releases/download/1.5.3/libbson-1.5.3.tar.gz)
* [libmongoc-1.5.3.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.5.3/mongo-c-driver-1.5.3.tar.gz)
* [All bugs fixed in 1.5.3](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17896/)
* [Documentation](http://mongoc.org/)


Peace,<br>
&mdash; A. Jesse Jiryu Davis

***

<a href="https://commons.wikimedia.org/wiki/File:MONSTROSITY;_Sea_Monter_Wellcome_L0032594.jpg" style="color: gray">Image: Sea monster. Ulisse Aldrovandi, 17th Century</a>
