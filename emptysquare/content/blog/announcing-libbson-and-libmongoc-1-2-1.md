+++
type = "post"
title = "Announcing libbson and libmongoc 1.2.1"
date = "2015-10-29T21:25:58"
description = "An SSL bugfix for pooled clients, domain socket fix, El Capitan build guide."
categories = ["C", "Mongo", "Programming"]
tags = []
enable_lightbox = false
thumbnail = "miami-haze.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="miami-haze.jpg" alt="Miami Haze, by Dan DeChiaro" title="Miami Haze, by Dan DeChiaro" /></p>
<p>It is my pleasure to announce the 1.2.1 release of libbson and libmongoc, the C libraries that compose the MongoDB C Driver.</p>
<p>This release includes critical bugfixes for SSL connections with
<a href="http://api.mongodb.org/c/current/mongoc_client_pool_t.html"><code>mongoc_client_pool_t</code></a>, and for Unix domain socket connections.</p>
<p>The documentation is updated for a change introduced in version 1.2.0:
<a href="http://api.mongodb.org/c/current/mongoc_client_set_ssl_opts.html"><code>mongoc_client_set_ssl_opts</code></a> and <a href="http://api.mongodb.org/c/current/mongoc_client_pool_set_ssl_opts.html"><code>mongoc_client_pool_set_ssl_opts</code></a> now configure
the driver to require an SSL connection to the server, even if "ssl=true" is
omitted from the MongoDB URI. Before, SSL options were ignored unless
"ssl=true" was included in the URI.</p>
<p>The build instructions are improved, including <a href="http://api.mongodb.org/c/current/installing.html#installing-osx">the steps to build with OpenSSL
on OS X El Capitan</a>. Build errors and warnings are fixed for clang in gnu99
mode and for MinGW.</p>
<p>Links:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.2.1/libbson-1.2.1.tar.gz">libbson-1.2.1.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.2.1/mongo-c-driver-1.2.1.tar.gz">mongo-c-driver-1.2.1.tar.gz</a></li>
<li><a href="https://jira.mongodb.org/issues/?jql=fixVersion%20%3D%201.2.1%20AND%20project%20%3D%20CDRIVER">Issues resolved in 1.2.1</a></li>
<li><a href="http://docs.mongodb.org/ecosystem/drivers/c/">MongoDB C Driver Documentation</a></li>
</ul>
<p>Thanks to everyone who contributed to this version of libmongoc.</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Hannes Magnusson</li>
<li>Tamas Nagy</li>
</ul>
<p>Peace,</p>
<p>A. Jesse Jiryu Davis</p>
<hr />
<p><span style="color:gray"><a href="https://www.flickr.com/photos/dandechiaro/4197904546">Image: Dan DeChiaro.</a></span></p>
    