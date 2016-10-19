+++
type = "post"
title = "Announcing libbson and libmongoc 1.1.11"
date = "2015-09-23T17:24:16"
description = "Documentation improvements and many network-layer bugfixes."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "crow-sea@240.jpg"
draft = false
disqus_identifier = "560315bc5393742358c9e4b8"
disqus_url = "https://emptysqua.re/blog/560315bc5393742358c9e4b8/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="crow-sea.jpg" alt="Crow, sea - by Mark Abercrombie" title="Crow, sea - by Mark Abercrombie" /></p>
<p>Today I released version 1.1.11 of libbson and libmongoc, the two libraries that constitute the MongoDB C Driver.</p>
<p>In libbson, my new team member Kyle Suarez improved the documentation with <a href="https://github.com/mongodb/libbson/blob/master/examples/bson-streaming-reader.c">an example of streaming BSON over a socket</a>, and added pages for the callback function types <a href="https://api.mongodb.org/libbson/1.1.11/bson_reader_destroy_func_t.html"><code>bson_reader_destroy_func_t</code></a> and <a href="https://api.mongodb.org/libbson/1.1.11/bson_reader_read_func_t.html"><code>bson_reader_read_func_t</code></a>.</p>
<p>In libmongoc, Jason Carey and Hannes Magnusson fixed an assortment of undetected network errors when sending messages to the server, and Jason plugged a memory leak when the driver parses a URI that contains an invalid option. Jose Sebastian Battig contributed a patch for an off-by-one error in mongoc_gridfs_file_seek with mode SEEK_END. GitHub user "rubicks" updated the libbson submodule's URL to use the recommended "https://" instead of "git://".</p>
<p>The documentation is here:</p>
<ul>
<li><a href="http://docs.mongodb.org/ecosystem/drivers/c/">http://docs.mongodb.org/ecosystem/drivers/c/</a></li>
</ul>
<p>Tarballs:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.1.11/libbson-1.1.11.tar.gz">libbson-1.1.11.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.1.11/mongo-c-driver-1.1.11.tar.gz">mongo-c-driver-1.1.11.tar.gz</a></li>
</ul>
<p>Thanks to everyone who contributed to the development of this release!</p>
<hr />
<p><a href="https://www.flickr.com/photos/streetseens/16689162036/">Image: Mark Abercrombie</a></p>
