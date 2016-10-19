+++
type = "post"
title = "MongoDB Full Text Search"
date = "2013-01-12T12:20:57"
description = "How to power your Python web application's search with MongoDB"
category = ["Mongo", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "320px-dictionary-indents-headon@240.jpg"
draft = false
disqus_identifier = "50f199ba53937408d1c6e87e"
disqus_url = "https://emptysqua.re/blog/50f199ba53937408d1c6e87e/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="320px-dictionary-indents-headon.jpg" alt="Dictionary indents headon" title="320px-Dictionary_indents_headon.jpg" border="0"   /></p>
<p><a href="http://commons.wikimedia.org/wiki/File:Dictionary_indents_headon.jpg" style="color: gray; text-decoration: none; font-style: italic">Wikimedia commons</a></p>
<p>Yesterday <a href="https://groups.google.com/d/topic/mongodb-announce/3SkNJdemy84/discussion">we released the latest unstable version of MongoDB</a>; the headline feature is basic full-text search. You can read all about <a href="http://docs.mongodb.org/manual/release-notes/2.4/#text-indexes">MongoDB's full text search in the release notes</a>.</p>
<p>This blog had been using a really terrible method for search, involving regular expressions, a full collection scan for every search, and no ranking of results by relevance. I wanted to replace all that cruft with MongoDB's full-text search ASAP. Here's what I did.</p>
<h1 id="plain-text">Plain Text</h1>
<p>My blog is written in Markdown and displayed as HTML. What I want to actually search is the posts' plain text, so we need a new field called <code>plain</code> on each <code>post</code> document in MongoDB. That <code>plain</code> field is what we're going to index.</p>
<p>First, I customized Python's standard <code>HTMLParser</code> to strip tags from the HTML:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">import</span> <span style="color: #0000FF; font-weight: bold">re</span>
<span style="color: #008000; font-weight: bold">from</span> <span style="color: #0000FF; font-weight: bold">HTMLParser</span> <span style="color: #008000; font-weight: bold">import</span> HTMLParser

whitespace <span style="color: #666666">=</span> re<span style="color: #666666">.</span>compile(<span style="color: #BA2121">&#39;\s+&#39;</span>)

<span style="color: #008000; font-weight: bold">class</span> <span style="color: #0000FF; font-weight: bold">HTMLStripTags</span>(HTMLParser):
    <span style="color: #BA2121; font-style: italic">&quot;&quot;&quot;Strip tags</span>
<span style="color: #BA2121; font-style: italic">    &quot;&quot;&quot;</span>
    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">__init__</span>(<span style="color: #008000">self</span>, <span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs):
        HTMLParser<span style="color: #666666">.</span>__init__(<span style="color: #008000">self</span>, <span style="color: #666666">*</span>args, <span style="color: #666666">**</span>kwargs)
        <span style="color: #008000">self</span><span style="color: #666666">.</span>out <span style="color: #666666">=</span> <span style="color: #BA2121">&quot;&quot;</span>

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">handle_data</span>(<span style="color: #008000">self</span>, data):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>out <span style="color: #666666">+=</span> data

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">handle_entityref</span>(<span style="color: #008000">self</span>, name):
        <span style="color: #008000">self</span><span style="color: #666666">.</span>out <span style="color: #666666">+=</span> <span style="color: #BA2121">&#39;&amp;</span><span style="color: #BB6688; font-weight: bold">%s</span><span style="color: #BA2121">;&#39;</span> <span style="color: #666666">%</span> name

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">handle_charref</span>(<span style="color: #008000">self</span>, name):
        <span style="color: #008000; font-weight: bold">return</span> <span style="color: #008000">self</span><span style="color: #666666">.</span>handle_entityref(<span style="color: #BA2121">&#39;#&#39;</span> <span style="color: #666666">+</span> name)

    <span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">value</span>(<span style="color: #008000">self</span>):
        <span style="color: #408080; font-style: italic"># Collapse whitespace</span>
        <span style="color: #008000; font-weight: bold">return</span> whitespace<span style="color: #666666">.</span>sub(<span style="color: #BA2121">&#39; &#39;</span>, <span style="color: #008000">self</span><span style="color: #666666">.</span>out)<span style="color: #666666">.</span>strip()

<span style="color: #008000; font-weight: bold">def</span> <span style="color: #0000FF">plain</span>(html):
    parser <span style="color: #666666">=</span> HTMLStripTags()
    parser<span style="color: #666666">.</span>feed(html)
    <span style="color: #008000; font-weight: bold">return</span> parser<span style="color: #666666">.</span>value()
</pre></div>


<p><strong>Updated Jan 14, 2013: Better code, fixed whitespace-handling bugs.</strong></p>
<p>I wrote <a href="https://github.com/ajdavis/motor-blog/blob/master/motor_blog/tools/add_plain_text_field.py">a script that runs through all my existing posts</a>, extracts the plain text from the HTML, and stores it in a new field on each document called <code>plain</code>. I also updated my blog's code so it now <a href="https://github.com/ajdavis/motor-blog/blob/master/motor_blog/models.py#L139">updates the <code>plain</code> field on each post</a> whenever I save a post.</p>
<h1 id="creating-the-index">Creating the Index</h1>
<p>I installed MongoDB 2.3.2 and started it with this command line option:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">--setParameter textSearchEnabled=true
</pre></div>


<p>Without that option, creating a text index causes a server error, "text search not enabled".</p>
<p>Next I created a text index on posts' titles, category names, tags, and the plain text that I generated above. I can set different relevance weights for each field. The title contributes most to a post's relevance score, followed by categories and tags, and finally the text. In Python, the index declaration looks like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db<span style="color: #666666">.</span>posts<span style="color: #666666">.</span>create_index(
    [
        (<span style="color: #BA2121">&#39;title&#39;</span>, <span style="color: #BA2121">&#39;text&#39;</span>),
        (<span style="color: #BA2121">&#39;categories.name&#39;</span>, <span style="color: #BA2121">&#39;text&#39;</span>),
        (<span style="color: #BA2121">&#39;tags&#39;</span>, <span style="color: #BA2121">&#39;text&#39;</span>), (<span style="color: #BA2121">&#39;plain&#39;</span>, <span style="color: #BA2121">&#39;text&#39;</span>)
    ],
    weights<span style="color: #666666">=</span>{
        <span style="color: #BA2121">&#39;title&#39;</span>: <span style="color: #666666">10</span>,
        <span style="color: #BA2121">&#39;categories.name&#39;</span>: <span style="color: #666666">5</span>,
        <span style="color: #BA2121">&#39;tags&#39;</span>: <span style="color: #666666">5</span>,
        <span style="color: #BA2121">&#39;plain&#39;</span>: <span style="color: #666666">1</span>
    }
)
</pre></div>


<p>Note that you'll need to install PyMongo from <a href="https://github.com/mongodb/mongo-python-driver/">the current master in GitHub</a> or wait for PyMongo 2.4.2 in order to create a text index. PyMongo 2.4.1 and earlier throw an exception:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">TypeError<span style="color: #666666">:</span> second item <span style="color: #008000; font-weight: bold">in</span> <span style="color: #008000; font-weight: bold">each</span> key pair must be
ASCENDING<span style="color: #666666">,</span> DESCENDING<span style="color: #666666">,</span> GEO2D<span style="color: #666666">,</span> or GEOHAYSTACK
</pre></div>


<p>If you don't want to upgrade PyMongo, just use the mongo shell to create the index:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db.posts.createIndex(
    {
        title<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;text&#39;</span>,
        <span style="color: #BA2121">&#39;categories.name&#39;</span><span style="color: #666666">:</span> <span style="color: #BA2121">&#39;text&#39;</span>,
        tags<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;text&#39;</span>,
        plain<span style="color: #666666">:</span> <span style="color: #BA2121">&#39;text&#39;</span>
    },
    {
        weights<span style="color: #666666">:</span> {
            title<span style="color: #666666">:</span> <span style="color: #666666">10</span>,
            <span style="color: #BA2121">&#39;categories.name&#39;</span><span style="color: #666666">:</span> <span style="color: #666666">5</span>,
            tags<span style="color: #666666">:</span> <span style="color: #666666">5</span>,
            plain<span style="color: #666666">:</span> <span style="color: #666666">1</span>
        }
    }
)
</pre></div>


<h1 id="searching-the-index">Searching the Index</h1>
<p>To use the text index I can't do a normal <code>find</code>, I have to run the <code>text</code> command. In my async driver Motor, this looks like:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">response <span style="color: #666666">=</span> <span style="color: #008000; font-weight: bold">yield</span> motor<span style="color: #666666">.</span>Op(<span style="color: #008000">self</span><span style="color: #666666">.</span>db<span style="color: #666666">.</span>command, <span style="color: #BA2121">&#39;text&#39;</span>, <span style="color: #BA2121">&#39;posts&#39;</span>,
<span style="background-color: #ffffcc">    search<span style="color: #666666">=</span>q,
</span>    <span style="color: #008000">filter</span><span style="color: #666666">=</span>{<span style="color: #BA2121">&#39;status&#39;</span>: <span style="color: #BA2121">&#39;publish&#39;</span>, <span style="color: #BA2121">&#39;type&#39;</span>: <span style="color: #BA2121">&#39;post&#39;</span>},
    projection<span style="color: #666666">=</span>{
        <span style="color: #BA2121">&#39;display&#39;</span>: <span style="color: #008000">False</span>,
        <span style="color: #BA2121">&#39;original&#39;</span>: <span style="color: #008000">False</span>,
        <span style="color: #BA2121">&#39;plain&#39;</span>: <span style="color: #008000">False</span>
    },
    limit<span style="color: #666666">=50</span>)
</pre></div>


<p>The <code>q</code> variable is whatever you typed into the search box on the left, like "mongo" or "hamster" or "python's thread locals are weird". The <code>filter</code> option ensures only published posts are returned, and the <code>projection</code> avoids returning large unneeded fields. Results are sorted with the most relevant first, and the limit is applied after the sort.</p>
<h1 id="in-conclusion">In Conclusion</h1>
<p>Simple, right? The new text index provides a simple, fully consistent way to do basic search without deploying any extra services. Go read up about it in <a href="http://docs.mongodb.org/manual/release-notes/2.4/#text-indexes">the release notes</a>.</p>
