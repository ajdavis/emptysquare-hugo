+++
type = "post"
title = "How Thoroughly Are You Testing Your C Extensions?"
date = "2014-02-27T09:16:49"
description = "How to measure code coverage in your Python C extension modules."
category = ["Programming", "Python"]
tag = ["c"]
enable_lightbox = false
thumbnail = "lcov-source-nomem@240.png"
draft = false
disqus_identifier = "530eb0f8539374095e323d47"
disqus_url = "https://emptysqua.re/blog/530eb0f8539374095e323d47/"
+++

<p>You probably know how to find Python code that isn't exercised by your tests. Install <a href="http://nedbatchelder.com/code/coverage/">coverage</a> and run:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>coverage run --source<span style="color: #666666">=</span>SOURCEDIR setup.py <span style="color: #008000">test</span>
</pre></div>


<p>Then, for a beautiful coverage report:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>coverage html
</pre></div>


<p>But what about your C extensions? They're harder to write than Python, so you better make sure they're thoroughly tested. On Linux, you can use <a href="http://gcc.gnu.org/onlinedocs/gcc-4.8.2/gcc/Gcov.html">gcov</a>. First, recompile your extension with the coverage hooks:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span><span style="color: #008000">export </span><span style="color: #19177C">CFLAGS</span><span style="color: #666666">=</span><span style="color: #BA2121">&quot;-coverage&quot;</span>
<span style="color: #19177C">$ </span>python setup.py build_ext --inplace
</pre></div>


<p>In your build directory (named like <code>build/temp.linux-x86_64-2.7</code>) you'll now see some files with the ".gcno" extension. These are gcov's data files. Run your tests again and the directory will fill up with ".gcda" files that contain statistics about which parts of your C code were run.</p>
<p>You have a number of ways to view this coverage information. I use Eclipse with <a href="http://wiki.eclipse.org/Linux_Tools_Project/GCov/User_Guide">the gcov plugin</a> installed. (Eclipse CDT includes it by default.) Delightfully, Eclipse on my Mac understands coverage files generated on a Linux virtual machine, with no hassle at all.</p>
<p><a href="http://ltp.sourceforge.net/coverage/lcov.php">lcov</a> can make you some nice HTML reports. Run it like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #19177C">$ </span>lcov --capture --directory . --output-file coverage.info
<span style="color: #19177C">$ </span>genhtml coverage.info --output-directory out
</pre></div>


<p>Here's a portion of its report for PyMongo's BSON decoder:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="lcov-table.png" alt="lcov table" title="lcov table" /></p>
<p>Our C code coverage is significantly lower than our Python coverage. This is mainly because such a large portion of the C code is devoted to error handling: it checks for <em>every</em> possible error, but we only trigger a subset of all possible errors in our tests. </p>
<p>A trivial example is in <code>_write_regex_to_buffer</code>, when we ensure the buffer is large enough to hold 4 more bytes. We check that <code>realloc</code>, if it was called, succeeded:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="lcov-source-nomem.png" alt="lcov source: No Memory" title="lcov source: No Memory" /></p>
<p>We don't run out of memory during our tests, so these two lines of error-handling are never run. A more realistic failure is in <code>decode_all</code>:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="lcov-source.png" alt="lcov source" title="lcov source" /></p>
<p>This is the error handler that runs when a message is shorter than five bytes. Evidently the size check runs 56,883 times during our tests, but this particular error never occurs so the error-handler isn't tested. This is the sort of insight that'd be onerous to attain without a tool like gcov.</p>
<p>Try it for yourself and see: are you testing your C code as thoroughly as your Python?</p>
<hr />
<p>You might also like my article on <a href="/blog/analyzing-python-c-extensions-with-cpychecker/">automatically detecting refcount errors in C extensions</a>, or the one on <a href="/blog/python-c-extensions-and-mod-wsgi/">making C extensions compatible with mod_wsgi</a>.</p>
