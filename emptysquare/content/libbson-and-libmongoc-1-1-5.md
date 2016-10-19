+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.5"
date = "2015-05-12T19:07:59"
description = "Bugfix releases for the MongoDB C libraries."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "SeaSmoke@240.jpg"
draft = false
legacyid = "555278f15393741c76457303"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="SeaSmoke.jpg" alt="Sea Smoke" title="Sea Smoke" /></p>
<p>I've released versions 1.1.5 today of libbson and libmongoc.</p>
<p>libbson is a C library for creating, parsing, and manipulating BSON documents. libmongoc is the C Driver for MongoDB, a library for building high-performance applications that communicate with MongoDB in the C language. It also serves as the base for drivers in some higher-level languages.</p>
<p>Release tarballs are available for download:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.1.5/libbson-1.1.5.tar.gz">libbson-1.1.5.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.1.5/mongo-c-driver-1.1.5.tar.gz">mongo-c-driver-1.1.5.tar.gz</a></li>
</ul>
<p>This is a patch release with small bug fixes. In libbson:</p>
<ul>
<li>Fix link error "missing __sync_add_and_fetch_4" in GCC on i386 - the functions <code>bson_atomic_int_add</code> and <code>bson_atomic_int64_add</code> are now compiled and exported if needed in i386 mode</li>
<li>Fix version check for GCC 5 and future versions of Clang</li>
<li>Fix warnings and errors building on various platforms</li>
</ul>
<p>In libmongoc:</p>
<ul>
<li>The <code>fsync</code> and <code>j</code> write concern flags now imply acknowledged writes</li>
<li>Prevent using <code>fsync</code> or <code>j</code> with conflicting <code>w=0</code> write concern</li>
<li>Obey socket timeout consistently in TLS/SSL mode</li>
<li>Return an error promptly after a network hangup in TLS mode</li>
<li>Prevent crash using SSL in FIPS mode</li>
<li>Always return NULL from <code>mongoc_database_get_collection_names</code> on error</li>
<li>Fix version check for GCC 5 and future versions of Clang</li>
<li>Fix warnings and errors building on various platforms</li>
<li>Add configure flag to enable/disable shared memory performance counters</li>
<li>Minor docs improvements and fix links from libmongoc to libbson docs</li>
</ul>
<p>For further information:</p>
<ul>
<li><a href="https://api.mongodb.org/libbson/current/">libbson documentation</a></li>
<li><a href="http://api.mongodb.org/c/current/">libmongoc documentation</a></li>
<li><a href="https://jira.mongodb.org/secure/ReleaseNote.jspa?projectId=10030&amp;version=15316">Full release notes for libbson 1.1.5 and libmongoc 1.1.5 in Jira</a></li>
</ul>
<p>With this release, I abandon the convention that odd-numbered patch versions indicate unstable releases. I am switching to simple semantic versioning: 1.1.5 is a stable release with bug fixes since 1.1.4. During subsequent development the libmongoc and libbson versions will be "1.1.6-dev".</p>
<p>This is my first release of libbson and libmongoc; I needed a lot of help and I received it. Thanks to those who contributed:</p>
<ul>
<li>Christian Hergert</li>
<li>Hannes Magnusson</li>
<li>Jason Carey</li>
<li>Jeremy Mikola</li>
<li>Jeroen Ooms</li>
<li>Paul Melnikow</li>
</ul>
<hr />
<p><a href="http://commons.wikimedia.org/wiki/File:SeaSmoke.jpg">Image: Kristopher Wilson/ US Navy</a></p>
