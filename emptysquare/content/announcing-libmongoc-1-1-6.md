+++
type = "post"
title = "Announcing libmongoc 1.1.6"
date = "2015-05-18T18:50:31"
description = "Major bugfixes, a performance enhancement, and two tiny little features."
category = ["C", "Mongo", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "Hans_Egede_sea_serpent_1734.jpg"
draft = false
disqus_identifier = "555a6bf85393741c7645a014"
disqus_url = "https://emptysqua.re/blog/555a6bf85393741c7645a014/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Hans_Egede_sea_serpent_1734.jpg" alt="Hans Egede sea serpent 1734" title="Hans Egede sea serpent 1734" /></p>
<p>I released libmongoc 1.1.6 today with some bugfixes and a major performance enhancement.</p>
<ul>
<li><a href="http://api.mongodb.org/c/current/mongoc_bulk_operation_execute.html"><code>mongoc_bulk_operation_execute</code></a> now coalesces consecutive update operations
  into a single message to a MongoDB 2.6+ server, yielding huge performance
  gains. Same for remove operations. (Inserts were always coalesced.)</li>
<li>Large numbers of insert operations are now properly batched according to
  number of documents and total data size.</li>
<li><a href="http://api.mongodb.org/c/current/authentication.html#kerberos">GSSAPI / Kerberos auth</a> now works.</li>
<li>The driver no longer tries three times in vain to reconnect to a primary,
  so <code>socketTimeoutMS</code> and <code>connectTimeoutMS</code> now behave <em>closer</em> to what you
  expect for replica sets with down members. A full fix awaits 1.2.0.</li>
</ul>
<p>I snuck in a feature:</p>
<ul>
<li><a href="http://api.mongodb.org/c/current/mongoc_matcher_t.html"><code>mongoc_matcher_t</code></a> does basic subdocument and array matching</li>
</ul>
<p>I also released libbson 1.1.6 to maintain version parity; it's identical to libbson 1.1.5.</p>
<p>Release tarballs are available for download:</p>
<ul>
<li><a href="https://github.com/mongodb/libbson/releases/download/1.1.6/libbson-1.1.6.tar.gz">libbson-1.1.6.tar.gz</a></li>
<li><a href="https://github.com/mongodb/mongo-c-driver/releases/download/1.1.6/mongo-c-driver-1.1.6.tar.gz">mongo-c-driver-1.1.6.tar.gz</a></li>
</ul>
<p>You'll notice this is just a week after <a href="/announcing-libbson-and-libmongoc-1-1-5/">the 1.1.5 release</a>, since there were a users waiting on these particular fixes that I couldn't get in to last week's release.</p>
<p>It's my intention to do only the most critical work for the 1.1.x line of the driver libraries, and concentrate on shipping 1.2.0 as soon as possible: a reasonably tested beta in the middle of June and a stable version at the beginning of August. (Circumstances are likely to intervene, of course.) Shipping version 1.2.0 will offer you a C driver that conforms with the modern MongoDB specs: <a href="http://www.mongodb.com/blog/post/server-discovery-and-monitoring-next-generation-mongodb-drivers">Server Discovery And Monitoring</a>, and <a href="http://www.mongodb.com/blog/post/server-selection-next-generation-mongodb-drivers">Server Selection</a>. It will resolve a heap of replica set issues in the current driver.</p>
<p>For further information:</p>
<ul>
<li><a href="https://api.mongodb.org/libbson/current/">libbson documentation</a></li>
<li><a href="http://api.mongodb.org/c/current/">libmongoc documentation</a></li>
<li><a href="https://jira.mongodb.org/secure/ReleaseNote.jspa?projectId=10030&amp;version=15434">Full release notes for libmongoc 1.1.6 in Jira</a></li>
</ul>
<p>Thanks to those who contributed:</p>
<ul>
<li>A. Jesse Jiryu Davis</li>
<li>Jason Carey</li>
<li>Kai Mast</li>
<li>Matt Cotter</li>
</ul>
<hr />
<p><a href="http://en.wikipedia.org/wiki/File:Hans_Egede_1734_sea_serpent.jpg">Image: The "Great Sea Serpent" according to Hans Egede</a></p>
