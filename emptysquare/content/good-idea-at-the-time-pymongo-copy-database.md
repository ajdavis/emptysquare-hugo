+++
type = "post"
title = "It Seemed Like A Good Idea At The Time: PyMongo's \"copy_database\""
date = "2014-12-09T09:11:41"
description = "Third in a four-part series about choices we regretted in the design of PyMongo."
category = ["MongoDB", "Programming", "Python"]
tag = ["good-idea-at-the-time", "pymongo"]
enable_lightbox = false
thumbnail = "copydb-auth.png"
draft = false
disqus_identifier = "547a7c6b53937409607d9310"
disqus_url = "https://emptysqua.re/blog/547a7c6b53937409607d9310/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="road-3.jpg" alt="Road" title="Road" /></p>
<p><em>The road to hell is paved with good intentions.</em></p>
<p>I'm writing <a href="/good-idea-at-the-time-pymongo/">eulogies for four regrettable decisions we made when we designed PyMongo</a>, the standard Python driver for MongoDB. Each of them made maintaining PyMongo painful, and confused our users. This winter, as I undo these regrettable designs in preparation for PyMongo 3.0, I carve for each a sad epitaph.</p>
<p>Today we reach the third regrettable decision: "copy_database".</p>
<div class="toc">
<ul>
<li><a href="#the-beginning">The Beginning</a></li>
<li><a href="#pymongo-and-copy_database">PyMongo and "copy_database"</a><ul>
<li><a href="#requests-again">Requests, Again</a></li>
<li><a href="#motor">Motor</a></li>
<li><a href="#scram-sha-1">SCRAM-SHA-1</a></li>
</ul>
</li>
<li><a href="#redemption">Redemption</a></li>
<li><a href="#bright-future">Bright Future</a></li>
</ul>
</div>
<hr />

<!--

commit 3332989338a5815c30a039213bf2e4581759e8c8
Author: Dwight <dmerriman@gmail.com>
Date:   Fri Sep 12 15:00:20 2008 -0400

    copydb - not yet done

commit e783239b3f9284d0dfe0161b8f8effc41d33aa57
Author: dwight <dwight@Dwights-MacBook.local>
Date:   Sun Sep 14 22:49:30 2008 -0400

    copydb work

commit 379a7562629ff0803cfb30e0abfcddcbee046a19
Author: Dwight <dmerriman@gmail.com>
Date:   Mon Sep 15 15:30:53 2008 -0400

    copydb

    first commit

commit 7ed81cdf6bc3af668273983c8dd890e545bcdaa4
Author: Aaron <aaron@10gen.com>
Date:   Tue Feb 16 15:20:35 2010 -0800

    SERVER-579 support copyDatabase from source running with security

commit 2213f813cf8c81ffa719adb46cfdbdf375bc8fae
Author: Mike Dirolf <mike@10gen.com>
Date:   Tue Mar 9 13:06:00 2010 -0500

    Adding copy_database

-->

<h1 id="the-beginning">The Beginning</h1>
<p>In the beginning, MongoDB had <a href="http://docs.mongodb.org/manual/reference/command/copydb/">a "copydb" command</a>. Well, not the beginning, but it was an early feature: MongoDB was less than a year old when Dwight Merriman implemented "copydb" in September 2008.</p>
<p>The initial protocol was simple. The client told MongoDB the source and target database names, and MongoDB made a copy:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="copydb.png" alt="copydb" title="copydb" /></p>
<p>You could give the target server a "fromhost" option and it would clone from a remote server, similar to how a replica set member does an initial sync:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="copydb-fromhost.png" alt="copydb fromhost" title="copydb fromhost" /></p>
<p>This is a really useful feature for sysadmins who occasionally copy a database using the mongo shell, but of course it's not a likely use case for application developers. So the <a href="http://docs.mongodb.org/manual/reference/method/db.copyDatabase/">mongo shell has a "db.copyDatabase" helper function</a>, but at the time none of our drivers did.</p>
<p>A year later, in January 2010, a user <a href="https://jira.mongodb.org/browse/SERVER-579">wanted to do "copydb" from a remote server with authentication</a>. Aaron Staple came up with a secure protocol: as long as the client knows the password for the source server, it can instruct the target server to authenticate, without revealing its password to the target server. The client tells the target to call "getnonce" on the source, and the source responds with a <a href="https://en.wikipedia.org/wiki/Cryptographic_nonce">nonce</a>, which the target forwards to the client:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="copydbgetnonce.png" alt="copydbgetnonce" title="copydbgetnonce" /></p>
<p>Then the client hashes its password with the nonce, and gives the hashed password back to the target server, allowing the target to authenticate against the source <em>once</em>:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="copydb-auth.png" alt="copydb with auth" title="copydb with auth" /></p>
<p>There's one important detail (imagine foreboding music now): "copydbgetnonce" and "copydb" must be sent on the same socket. This will be important later.</p>
<p>In any case, Aaron added support for this new protocol to MongoDB and to the mongo shell, so sysadmins could copy a database from a password-protected remote server. So far so good. But in a moment, we would make a regrettable decision.</p>
<h1 id="pymongo-and-copy_database">PyMongo and "copy_database"</h1>
<p>Nicolas Clairon, author of the PyMongo wrapper library <a href="http://namlook.github.io/mongokit/">MongoKit</a>, asked us to add a feature to PyMongo. <a href="https://jira.mongodb.org/browse/PYTHON-110">He wanted PyMongo to have a special helper method for copydb</a> so "every third party lib can use this method". PyMongo's author, Mike Dirolf, leapt to it: just two days later, he'd implemented a "copy_database" method in PyMongo, including support for authentication.</p>
<p>I understand why this seemed like a good idea at the time. Let's avoid duplication! Put "copy_database" in PyMongo, so every third party lib can use it! No one asked whether any users actually executed "copy_database" in Python. Mike just went ahead and implemented it. How could he know he was setting a course to hell?</p>
<h2 id="requests-again">Requests, Again</h2>
<p>Remember how I said copydbgetnonce and copydb must be sent on the same socket? Well, that wasn't a problem for Mike: at this time PyMongo always reserved a socket for each thread, and you couldn't turn this "feature" off. So if one thread called copydbgetnonce and then copydb, the two commands were sent on the same socket automatically.</p>
<p><a href="/good-idea-at-the-time-pymongo-start-request/">But, as I described in my "start_request" story</a>, after Mike had left and I joined the company, I made major connection pooling improvements. This included the ability for threads to freely share sockets in the connection pool. For real applications this dramatically increased PyMongo's efficiency. But it was bad news for "copy_database" with auth: now we needed a special way to ensure that the two commands were executed on the same socket. So I had to update "copy_database": Before calling copydbgetnonce, it checked if the current thread had a socket reserved. If not, it reserved one. Then it called the two commands in a row. Finally, it returned the socket, but only if the socket had been specially reserved for the sake of "copy_database".</p>
<p>There were already two code paths for "copy_database": one with authentication and one without. Now there were four: with and without authentication, with and without a socket already reserved for the current thread. Since concurrency bugs were a greater threat, I bloated the test suite with a half-dozen tests, probing for logic bugs and race conditions.</p>
<h2 id="motor">Motor</h2>
<p>Six months after I'd made these changes to PyMongo's connection pool and its "copy_database" method, I first announced Motor, my asynchronous driver for Tornado and MongoDB. Motor wraps PyMongo and makes it asynchronous, allowing I/O concurrency on a single thread, using Tornado's event loop.</p>
<p>Tricking PyMongo into executing concurrently on one thread was straightforward, actually, except for one method: "copy_database". It wants to reserve a socket for the current thread, but in Motor, many I/O operations are in flight at once for the main thread. So I had to reimplement "copy_database" from scratch just for Motor. I also reimplemented all PyMongo's "copy_database" tests, and distorted Motor's design so it could reserve sockets for asynchronous tasks, purely to support "copy_database".</p>
<p>I made a horrible mistake, too: I introduced a bug in Motor's "copy_database" <a href="/let-us-now-praise-resourcewarnings/">that leaked a socket on every single call</a>, but no one ever complained. The method clearly was risky, and unused.</p>
<p>What the hell was I thinking when I added "copy_database" to Motor? Why would anyone need it? We'd seen no signs, after all, that anyone was even using "copy_database" in PyMongo. And compared to PyMongo, Motor is optimized for web applications with lots of small concurrent operations. It's not intended for rare, lengthy tasks like "copy_database". But I was new at the company and I was excited about making Motor feature-complete: it would include every PyMongo feature, no matter how silly.</p>
<h2 id="scram-sha-1">SCRAM-SHA-1</h2>
<p>The breaking point for the PyMongo team came this fall, when MongoDB 2.8 introduced a new authentication mechanism, SCRAM-SHA-1. When 2.8 is released, SCRAM-SHA-1 will be the new default. And it's not just a better way of hashing passwords: it requires a different authentication <em>protocol</em> than the old MongoDB Challenge-Response mechanism. The old "copydbgetnonce" trick doesn't work with SCRAM-SHA-1.</p>
<p>Our senior security engineer Andreas Nilsson devised a new protocol for copydb with SCRAM-SHA-1, using a SASL conversation. It's more complex than the old protocol:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="copydbsaslstart.png" alt="copydbsaslstart" title="copydbsaslstart" /></p>
<p>This accomplishes the same goal as the old copydbgetnonce protocol: it allows the target server to log in to the source server <em>once</em>, without the client revealing its password to either server. But instead of two round trips, three are now required. Andreas added the new protocol to the mongo shell. Bernie had already implemented <a href="/pymongo-2-8-rc0/#scram-sha-1-authentication">PyMongo's support for authentication with SCRAM-SHA-1</a>, and he asked me to add it to our "copy_database" helper, too.</p>
<p>I've worked at MongoDB over three years, but I'm still prone to rushing headlong into new features. "I know!" I thought, "I won't just add SCRAM-SHA-1 to copy_database, I'll add LDAP and Kerberos, too!" It took Bernie and Andreas some effort to talk me down. I scaled the work to reasonable proportions. <a href="https://github.com/mongodb/mongo-python-driver/commit/0b7b51975e0156fabe8ba36bb5c5c7b7b90a30de">My final patch is tight</a>.</p>
<p>But still, PyMongo's "copy_database" is silly. It now has eight code paths. It can run without authentication, or use SCRAM-SHA-1, or use the old authentication mechanism, or it can try to guess which mechanism to use. And it's implemented both for MongoClient and for MongoReplicaSetClient. The code is hard to follow and the test footprint is like a sasquatch's.</p>
<p>I began to contemplate adding SCRAM-SHA-1 to Motor's "copy_database", too, when suddenly I had a thought: what if we could stop the pain? What if we could just...delete "copy_database"?</p>
<h1 id="redemption">Redemption</h1>
<p>This year the company has created a dedicated Product Management team whose job is to know what users want, or to find out. Before, each of us at MongoDB had our various contacts with users&mdash;Bernie and I knew what Python programmers asked about, salespeople knew what customers asked for, the support team knew what questions people called with&mdash;but like any startup we were flying by the seat of our pants when we made decisions about what features to add and maintain.</p>
<p>Now we have a group of professionals gathering and sorting this data. This group can answer my question, "Hey, does anyone care about PyMongo's copy_database method, or is the mongo shell's method the only thing people use?" They researched for a few days and replied,</p>
<blockquote>
<p>Consensus from the field is that copydb comes up very little, whether across hosts or not. They are generally OK with not supporting it in the drivers as it is a more administrative task anyway, but would want it supported by the shell.</p>
</blockquote>
<p>Things were looking up. Maybe we could just delete the damn method. We polled the drivers team and found that of all <a href="http://docs.mongodb.org/ecosystem/drivers/">the eleven supported MongoDB drivers</a>, only PyMongo, Motor, and the Ruby Driver have a "copy_database" method. And the Ruby team plans to remove the method in version 2.0 of their driver. So we'll remove it from PyMongo in the next major release, and Motor too. Not only will we delete risky code, we'll be more consistent with the other drivers.</p>
<h1 id="bright-future">Bright Future</h1>
<p>In <a href="/pymongo-2-8-rc0/">PyMongo's next release, version 2.8</a>, "copy_database" still works; in fact it gains the ability to do SCRAM-SHA-1 authentication against the source server. But it's also <a href="https://jira.mongodb.org/browse/PYTHON-783">deprecated</a>. <a href="https://jira.mongodb.org/browse/PYTHON-788">In PyMongo 3.0 "copy_database" will be gone</a>, and good riddance: there's no evidence that anyone copies databases using Python, and it's one of the most difficult features to maintain. <a href="https://jira.mongodb.org/browse/MOTOR-56">It'll be gone from Motor 0.4 as well</a>.</p>
<p>The lesson I learned is similar to last week's: gather requirements. But this time, we didn't just make up a useless feature: someone actually asked us for it. Even so, we should have turned him down. "Innovation is saying no to a thousand things," according to Steve Jobs.</p>
<p>Features are like children. They're conceived in a moment of passion, but you must support them for years. Think!</p>
<hr />
<p><em>The final installment in "It Seemed Like A Good Idea At The Time" is <a href="/good-idea-at-the-time-pymongo-mongoreplicasetclient/">MongoReplicaSetClient</a>.</em></p>
