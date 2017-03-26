+++
category = ['C', 'Mongo', 'Programming']
date = '2017-03-07T10:10:22.382108'
description = 'Fix localThresholdMS parsing, a crash in mongoc_cursor_destroy, and an interesting failure on MIPS'
draft = false
tag = []
thumbnail = 'Sea_serpent.jpg'
title = 'Announcing libbson and libmongoc 1.6.1'
type = 'post'
+++

![](4.Great-Norway-Sea-Serpent.jpg)

I'm pleased to announce version 1.6.1 of <a href="http://mongoc.org/libbson/current/">libbson</a> and <a href="http://mongoc.org/libmongoc/current/">libmongoc</a>,
the libraries constituting the MongoDB C Driver.

# **libbson**

This is a bugfix release that
resolves GCC 7 compiler warnings, improves HP-UX compatibility, and avoids
a test failure on 32-bit MIPS.

Debugging the MIPS bug was a small saga. I don't have a MIPS machine and I've only partly learned how to simulate one with QEMU; therefore it wasn't until the Debian Autobuilder Network emailed me that I knew the libbson test suite had begun failing on 32-bit MIPS.

My friend Roberto Sanchez and I logged into a MIPS machine that's provided for Debian developers and we tried to track down the failure. Since libbson runs its test suite in parallel on many threads, we couldn't easily tell which test called ``abort`` and terminated the test runner. Binary-searching, we disabled half the tests, then a quarter of them, and so on, but we observed very strange behavior: if we disabled the first quarter of the tests, the rest of the suite succeeded. "Fine," Roberto said, "so there's a failing test among the first quarter." To verify this theory, we enabled the first quarter and disabled the rest. Still the suite succeeded!

It occurred to me that it didn't matter *which* tests ran, but how *many* of them, which we confirmed by disabling some chunks of tests at random. We could run perhaps 250 tests, but not the full suite of about 300. I looked at how libbson's test runner worked and was surprised to learn that it starts as many threads as there are tests, and runs them all in parallel! I hypothesized that, circa libbson 1.6.0, we'd added enough new tests that we exceeded some limit imposed by 32-bit MIPS, a cramped old architecture. If it hadn't been for MIPS, we might have muddled along another year this way, until we added enough tests to reach the thread limit on some other platform.

Another Debian developer, James Cowgill, [provided a more rigorous analysis](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=854130):

> The tests appear to use up all of the MIPS virtual address space. MIPS
was hit first because it only has 2GB of virtual memory (whereas most
other 32-bit Linux arches have 3GB).

The test suite didn't allocate a very large amount of real RAM, but the address space reserved for hundreds of threads' stacks hit a virtual limit. My solution was to always start ten threads, and apportion the hundreds of tests among them.

# **libmongoc**

No dramatic story here, just some bug fixes:

* Correct the rules to parse localThresholdMS option from the MongoDB URI.
* Prevent crash in <a href="http://mongoc.org/libmongoc/current/mongoc_cursor_destroy.html">mongoc_cursor_destroy</a> if "query" or "filter" are invalid.
* Include a file, mongoc-cluster-sspi.c, that had been omitted from the
release archive.
* Fix logic bugs in <a href="http://mongoc.org/libmongoc/current/mongoc_bulk_operation_t.html">mongoc_bulk_operation_t</a> validation code.

I've backported the localThresholdMS and <a href="http://mongoc.org/libmongoc/current/mongoc_cursor_destroy.html">mongoc_cursor_destroy</a> fixes to the 1.5 branch and released libbson and libmongoc 1.5.5 with those changes only, for the PHP Driver's sake.


# **Links:**

* [libbson-1.6.1.tar.gz](https://github.com/mongodb/libbson/releases/download/1.6.1/libbson-1.6.1.tar.gz)
* [libmongoc-1.6.1.tar.gz](https://github.com/mongodb/mongo-c-driver/releases/download/1.6.1/mongo-c-driver-1.6.1.tar.gz)
* [All bugs fixed in 1.6.1](https://jira.mongodb.org/browse/CDRIVER/fixforversion/17959/)
* [Documentation](http://mongoc.org/)


Thanks to everyone who contributed to this release.

<ul><li>A. Jesse Jiryu Davis<li>Jeremy Mikola<li>Remi Collet</ul>

Peace,<br>
&mdash; A. Jesse Jiryu Davis

![](Sea_serpent.jpg)

<span style="color: gray">Images: Conrad Gessn 1580, Olaus Magnus 1555.</span>
