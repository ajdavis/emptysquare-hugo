+++
type = "post"
title = "Ubuntu 16.04 Includes The MongoDB C Driver"
date = "2016-05-02T13:42:05"
description = "Installing the driver on Xenial is as easy as \"apt-get install libmongoc-1.0\"."
category = ["Programming", "Mongo", "C"]
tag = ["packaging"]
enable_lightbox = false
thumbnail = "debian-ubuntu.png"
draft = false
disqus_identifier = "/blog/c-driver-ubuntu"
disqus_url = "https://emptysqua.re/blog//blog/c-driver-ubuntu/"
+++

<p><img alt="Debian and Ubuntu logos" src="debian-ubuntu.png" /></p>
<p>I've been working with an expert Debian developer, Roberto Sanchez, to package libbson and libmongoc for Debian. Our efforts paid off: the MongoDB C Driver is now included in Debian Unstable and in Ubuntu 16.04 Xenial Xerus. If you run Xenial, get the driver as easily as:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">apt-get install libmongoc-1.0
</pre></div>


<p>Roberto's patience and passion to teach me about Debian packaging has made it a joy for me.</p>
<hr />
<p>If you're on a RedHat-like system, you're in luck. Remi Collet maintains excellent RPMs for the C Driver. Commands to enable Remi's repository and install libmongoc depend on your exact system. For example, on CentOS 6:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>yum install http://rpms.remirepo.net/enterprise/remi-release-6.rpm
<span style="color: #19177C">$ </span>yum update
<span style="color: #19177C">$ </span>yum install mongo-c-driver
</pre></div>


<p>The <a href="http://rpms.remirepo.net/wizard/">Configuration Wizard for Remi's RPM Repository</a> generates detailed instructions for your system.</p>
<p>As always, to get a specific version of the C Driver or to control how it's compiled, follow <a href="https://api.mongodb.org/c/current/installing.html">the installation instructions in our manual</a>.</p>
