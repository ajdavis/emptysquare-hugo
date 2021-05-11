+++
type = "post"
title = "An Enlightening Failure"
date = "2014-03-27T15:34:35"
description = "How I fooled myself into thinking I'd made my code eight times faster."
category = ["MongoDB", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "dammit.jpg"
draft = false
disqus_identifier = "53347ad7539374726c12b68e"
disqus_url = "https://emptysqua.re/blog/53347ad7539374726c12b68e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="dammit.jpg" alt="Facepalm" title="Facepalm" /></p>
<p>This year I plan to rewrite PyMongo's BSON decoder. The decoder is written in C, and it's pretty fast, but I had a radical idea for how to make it faster. That idea turned out to be wrong, although it took me a long time to discover that.</p>
<p>Discovering I'm wrong is the best way to learn. The second-best way is by writing. So I'll multiply the two by writing a story about my wrong idea.</p>
<h1 id="the-story">The Story</h1>
<p>Currently, when PyMongo decodes a buffer of BSON documents, it creates a Python dict (hashtable) for each BSON document. It returns the dicts in a list.</p>
<p>My radical idea was to make a maximally-lazy decoder. I wouldn't decode all the documents at once, I would decode each document just-in-time as you iterate. Even more radically, I wouldn't convert each document into a dict. Instead, each document would only know its offset in the BSON buffer. When you access a field in the document, like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">document[<span style="color: #BA2121">&quot;fieldname&quot;</span>]
</pre></div>


<p>...I wouldn't do a hashtable lookup anymore. I'd do a linear-search through the BSON. I thought this approach might be faster, since the linear search would usually be fast, and I'd avoid the overhead of creating the hashtable. If a document was frequently accessed or had many fields, I'd eventually "inflate" it into a dict.</p>
<p>I coded up a prototype in C, benchmarked it, and it was eight times faster than the current code. I rejoiced, and began to develop it into a full-featured decoder.</p>
<p>At some point I applied our unicode tests to my decoder, and I realized I was using <a href="http://docs.python.org/2/c-api/string.html#PyString_FromString"><code>PyString_FromString</code></a> to decode strings, when I should be using <a href="http://docs.python.org/2/c-api/unicode.html#PyUnicode_DecodeUTF8"><code>PyUnicode_DecodeUTF8</code></a>. (I was targeting only Python 2 at this point.) I added the call to <code>PyUnicode_DecodeUTF8</code>, and my decoder started passing our unicode tests. I continued adding features.</p>
<p>Then next day I benchmarked again, and my code was no longer any faster than the current decoder. I didn't know which change had caused the slowdown, so I learned how to use callgrind and tried all sorts of things and went a little crazy. Eventually I used <code>git bisect</code>, and I was enlightened: my prototype had only been fast as long as it didn't decode UTF-8 properly. Once I had fixed that, I had the same speed as the current PyMongo.</p>
<h1 id="lessons-learned">Lessons Learned</h1>
<ol>
<li>The cost of PyMongo's BSON decoding is typically dominated by UTF-8 decoding. There's no way to avoid it, and it's <a href="http://bugs.python.org/issue14738">already optimized like crazy</a>.</li>
<li>Python's dict is really fast for PyMongo's kind of workload. It's not worth trying to beat it.</li>
<li>When I care about speed, I need to run my benchmarks on each commit. I should use <code>git bisect</code> as the first resort, not the last.</li>
</ol>
<p>This is disappointing, but I've learned a ton about the Python C API, BSON, and callgrind. On my next attempt to rewrite the decoder, I won't forget my hard-won lessons.</p>
