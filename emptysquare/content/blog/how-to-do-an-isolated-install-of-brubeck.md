+++
type = "post"
title = "How To Do An Isolated Install of Brubeck"
date = "2012-01-05T15:56:56"
description = "I wanted to install James Dennis's Brubeck web framework, but lately I've become fanatical about installing nothing, nothing, in the system-wide directories. A simple rm -rf brubeck/ should make it like nothing ever happened. So that I [ ... ]"
categories = ["Programming", "Python"]
tags = ["brubeck", "isolated", "virtualenv"]
enable_lightbox = false
thumbnail = "brubeck.png"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="brubeck.png" title="Brubeck" /></p>
<p>I wanted to install James Dennis's <a href="http://brubeck.io/">Brubeck</a> web
framework, but lately I've become fanatical about installing nothing,
<strong>nothing</strong>, in the system-wide directories. A simple <code>rm -rf brubeck/</code>
should make it like nothing ever happened.</p>
<p>So that I remember this for next time, here's how I did an isolated
install of Brubeck and all its dependencies on Mac OS Lion.</p>
<p>Install virtualenv and virtualenvwrapper (but of course you've already
done this, because you're elite like me).</p>
<h2 id="make-a-virtualenv">Make a virtualenv</h2>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">mkvirtualenv brubeck; cdvirtualenv
</pre></div>


<h2 id="zeromq">ZeroMQ</h2>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">wget http://download.zeromq.org/zeromq-2.2.0.tar.gz
tar zxf zeromq-2.2.0.tar.gz 
cd zeromq-2.2.0
./autogen.sh
./configure --prefix=$<span style="color: #19177C">VIRTUAL_ENV</span> <span style="border: 1px solid #FF0000">#</span> Don&#39;t install system-wide, just in this directory
make &amp;&amp; make install./c
cd ..
</pre></div>


<h2 id="mongrel2">Mongrel2</h2>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">git clone https://github.com/zedshaw/mongrel2.git
cd mongrel2
emacs Makefile
</pre></div>


<p>Add a line like this to the top of the Makefile, so the compiler can
find where you've installed ZeroMQ's header and lib files:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">OPTFLAGS</span> <span style="color: #666666">+=</span> -I<span style="color: #008000; font-weight: bold">$(</span>VIRTUAL_ENV<span style="color: #008000; font-weight: bold">)</span>/include -L<span style="color: #008000; font-weight: bold">$(</span>VIRTUAL_ENV<span style="color: #008000; font-weight: bold">)</span>/lib
</pre></div>


<p>and replace <code>PREFIX?=/usr/local</code> with <code>PREFIX?=$(VIRTUAL_ENV)</code></p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">make &amp;&amp; make install
cd ..
</pre></div>


<h2 id="libevent">Libevent</h2>
<p>Libevent (required by Gevent) is pretty much the same dance as ZeroMQ:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">wget https://github.com/downloads/libevent/libevent/libevent-2.0.19-stable.tar.gz
tar zxf libevent-2.0.19-stable.tar.gz
cd libevent-2.0.19-stable
./configure --prefix=$<span style="color: #19177C">VIRTUAL_ENV</span>
make
make install
cd ..
</pre></div>


<h2 id="python-packages">Python Packages</h2>
<p>First get Brubeck's requirements file:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">git clone https://github.com/j2labs/brubeck.git
cd brubeck
</pre></div>


<p>Now we need our isolated include/ and lib/ directories available on the
path when we install Brubeck's Python package dependencies.
Specifically, the gevent_zeromq package has some C code that needs to
find zmq.h and libzmq in order to compile. We'll do that by setting the
LIBRARY_PATH and C_INCLUDE_PATH environment variables:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">export LIBRARY_PATH=$<span style="color: #19177C">VIRTUAL_ENV</span>/lib
export C_INCLUDE_PATH=$<span style="color: #19177C">VIRTUAL_ENV</span>/include
pip install -I -r ./envs/brubeck.reqs
pip install -I -r ./envs/gevent.reqs
</pre></div>


<p>How nice is that?</p>
<p>(If it didn't work because of a gcc error message, try symlinking gcc into the place that Python expects it:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">sudo ln -s /usr/bin/gcc /usr/bin/gcc-4.2
</pre></div>


<p>... and try <code>pip install</code> again.)</p>
<h2 id="next">Next</h2>
<p>Once you're here, you have a completely isolated install of ZeroMQ,
Mongrel2, Brubeck, and all its package dependencies. Continue with
James's <a href="http://brubeck.io/installing.html">Brubeck installation
instructions</a> at the "A Demo"
portion.</p>
    