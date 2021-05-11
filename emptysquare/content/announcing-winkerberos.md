+++
type = "post"
title = "Announcing WinKerberos"
date = "2016-02-26T04:46:29"
description = "My colleague Bernie Hackett just released WinKerberos, a Windows native library for Kerberos authentication in Python."
category = ["Python", "MongoDB", "Programming"]
tag = []
enable_lightbox = false
thumbnail = "kerberos.jpg"
draft = false
disqus_identifier = "/blog/announcing-winkerberos"
disqus_url = "https://emptysqua.re/blog//blog/announcing-winkerberos/"
+++

<p><img alt="Kerberos" src="kerberos.jpg" /></p>
<p>My colleague Bernie Hackett has published a new Python extension module called <a href="https://github.com/mongodb-labs/winkerberos">WinKerberos</a>. It provides native Kerberos support to Python applications on Windows. It's a drop-in replacement for the popular <a href="https://pypi.python.org/pypi/pykerberos">PyKerberos</a> package, but it uses Microsoft's own Kerberos implementation, the Security Support Provider Interface (SSPI), and supports some Windows specific options.</p>
<h1 id="motivation">Motivation</h1>
<p>A number of MongoDB customers have requested support for GSSAPI authentication with PyMongo on Windows, so they can use Kerberos with Python and MongoDB.</p>
<p>Why not PyKerberos? PyKerberos works great on Unix, and PyMongo uses PyKerberos there. But it doesn't give us access to Microsoft's SSPI on Windows. If you want to use PyKerberos on Windows you could first install the MIT Kerberos library, but this is a finicky setup and we've had trouble proving that PyKerberos even works this way. Better to use SSPI, the standard way to do Kerberos on Windows. </p>
<p>But how can we use SSPI in Python? The existing kerberos-sspi is a nice library to do this, but <a href="https://github.com/may-day/kerberos-sspi/issues/1">a segfault that we reported</a> prevents us from using it in PyMongo. Besides, we need some features it lacks, like the ability to authenticate as a different user than the process owner.</p>
<h1 id="advantages">Advantages</h1>
<p>Bernie decided to write a new Python extension in pure C to work around the segfault. The package he made has some additional advantages over kerberos-sspi:</p>
<ul>
<li>Authenticating as a different user than the process owner</li>
<li>Tiny library, no dependencies, whereas kerberos-sspi depends on the giant pywin32</li>
</ul>
<h1 id="try-it">Try It!</h1>
<p>We haven't published to PyPI yet. We need you to try it out first. Please, if you're using Kerberos in Python on Windows, give our new WinKerberos package a try and let us know&mdash;tweet at me <a href="https://twitter.com/jessejiryudavis">@jessejiryudavis</a> or <a href="https://github.com/mongodb-labs/winkerberos/issues">open an issue on GitHub</a> and tell us if it works for you or not.</p>
<p>Link:</p>
<ul>
<li><a href="https://github.com/mongodb-labs/winkerberos">github.com/mongodb-labs/winkerberos</a></li>
</ul>
<p><strong>Update:</strong> Bernie released to PyPI on March 28, 2016:</p>
<ul>
<li><a href="https://pypi.python.org/pypi/winkerberos">WinKerberos on PyPI</a></li>
</ul>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Cerberus_(PSF).jpg"><span style="color: gray">Image: Pearson Scott Foresman</span></a></p>
