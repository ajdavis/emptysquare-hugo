+++
type = "post"
title = "Cross-linking Mallard HTML Pages With yelp-build"
date = "2015-10-23T11:37:08"
description = "How to link from pages of one Mallard document to another."
categories = ["C", "Programming"]
tags = []
enable_lightbox = false
thumbnail = "Mallard_Ducks_Drawing.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Mallard_Ducks_Drawing.jpg" alt="Mallard Ducks - John James Audubon" title="Mallard Ducks - John James Audubon" /></p>
<p>From its start, the MongoDB C Driver has been split into two projects: libbson and libmongoc. Each has its own reference manual, each comprising hundreds of pages, written in the <a href="http://projectmallard.org/">Mallard XML format</a>. We use <a href="https://github.com/GNOME/yelp-tools">yelp-build</a> to convert the Mallard to HTML and put it online. For example, here's the reference page for libmongoc's <code>mongoc_collection_find</code>:</p>
<hr />
<div style="font-family: monospace !important; text-align: left !important">
<h2>mongoc_collection_find</h2>
<div><pre>mongoc_cursor_t *
mongoc_collection_find (mongoc_collection_t       *collection,
                        mongoc_query_flags_t       flags,
                        uint32_t                   skip,
                        uint32_t                   limit,
                        uint32_t                   batch_size,
                        const bson_t              *query,
                        const bson_t              *fields,
                        const mongoc_read_prefs_t *read_prefs);</pre></div>
<h2>Parameters</h2>
<style>
#parameters-table td p { margin-right: 10px; }
</style>
<table id="parameters-table">
<tr>
<td><p>collection</p></td>
<td><p>A <a href="http://api.mongodb.org/c/current/mongoc_collection_t.html" title="mongoc_collection_t">mongoc_collection_t</a>.</p></td>
</tr>
<tr>
<td><p>flags</p></td>
<td><p>A <a href="http://api.mongodb.org/c/current/mongoc_query_flags_t.html" title="mongoc_query_flags_t">mongoc_query_flags_t</a>.</p></td>
</tr>
<tr>
<td><p>skip</p></td>
<td><p>Number of documents to skip.</p></td>
</tr>
<tr>
<td><p>limit</p></td>
<td><p>Max number of documents to return or 0.</p></td>
</tr>
<tr>
<td><p>batch_size</p></td>
<td><p>Batch size of document result sets or 0 for default.</p></td>
</tr>
<tr>
<td><p>query</p></td>
<td><p>A <a href="http://api.mongodb.org/libbson/current/bson_t.html" title="bson:bson_t">bson_t</a>.</p></td>
</tr>
<tr>
<td><p>fields</p></td>
<td><p>A <a href="http://api.mongodb.org/libbson/current/bson_t.html" title="bson:bson_t">bson_t</a> containing fields to return or NULL.</p></td>
</tr>
<tr>
<td><p>read_prefs</p></td>
<td><p>A <a href="http://api.mongodb.org/c/current/mongoc_read_prefs_t.html" title="mongoc_read_prefs_t">mongoc_read_prefs_t</a> or NULL for default read preferences.</p></td>
</tr>
</table>
</div>

<hr />
<p>Notice how names like <code>mongoc_collection_t</code> are links to other pages in libmongoc's manual. That's easy enough to do with yelp-build:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">&lt;code</span> <span style="color: #7D9029">xref=</span><span style="color: #BA2121">&quot;mongoc_collection_t&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>mongoc_collection_t<span style="color: #008000; font-weight: bold">&lt;/code&gt;</span>
</pre></div>


<p>What I couldn't figure out was this: how can I link references from libmongoc's manual to libbson's?</p>
<p>With incredible generosity, Shaun McCance designed a solution for me. He told me how to <a href="http://projectmallard.org/pipermail/mallard-list/2015-April/000216.html">create an "xref extension" using an XML transformation</a> so that an element like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">&lt;code</span> <span style="color: #7D9029">xref=</span><span style="color: #BA2121">&quot;bson:bson_t&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>bson_t<span style="color: #008000; font-weight: bold">&lt;/code&gt;</span>
</pre></div>


<p>...is rendered as a link to libbson's page about the <code>bson_t</code> type.</p>
<p>Here's the XSL file that does the transform:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">&lt;xsl:stylesheet&gt;</span>
    <span style="color: #408080; font-style: italic">&lt;!--</span>
<span style="color: #408080; font-style: italic">    Turn markup like this:</span>
<span style="color: #408080; font-style: italic">    &lt;code xref=&quot;bson:bson_t&quot;&gt;bson_t&lt;/code&gt;</span>
<span style="color: #408080; font-style: italic">    ... into a link like this:</span>
<span style="color: #408080; font-style: italic">    http://api.mongodb.org/libbson/current/bson_t.html</span>
<span style="color: #408080; font-style: italic">    --&gt;</span>
    <span style="color: #008000; font-weight: bold">&lt;xsl:template</span> <span style="color: #7D9029">name=</span><span style="color: #BA2121">&quot;mal.link.target.custom&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>
        <span style="color: #008000; font-weight: bold">&lt;xsl:param</span> <span style="color: #7D9029">name=</span><span style="color: #BA2121">&quot;node&quot;</span> <span style="color: #7D9029">select=</span><span style="color: #BA2121">&quot;.&quot;</span><span style="color: #008000; font-weight: bold">/&gt;</span>
        <span style="color: #008000; font-weight: bold">&lt;xsl:param</span> <span style="color: #7D9029">name=</span><span style="color: #BA2121">&quot;xref&quot;</span> <span style="color: #7D9029">select=</span><span style="color: #BA2121">&quot;$node/@xref&quot;</span><span style="color: #008000; font-weight: bold">/&gt;</span>
        <span style="color: #008000; font-weight: bold">&lt;xsl:if</span> <span style="color: #7D9029">test=</span><span style="color: #BA2121">&quot;starts-with($xref, &#39;bson:&#39;)&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>
            <span style="color: #008000; font-weight: bold">&lt;xsl:variable</span> <span style="color: #7D9029">name=</span><span style="color: #BA2121">&quot;ref&quot;</span>
                          <span style="color: #7D9029">select=</span><span style="color: #BA2121">&quot;substring-after($xref, &#39;bson:&#39;)&quot;</span><span style="color: #008000; font-weight: bold">/&gt;</span>
            <span style="color: #008000; font-weight: bold">&lt;xsl:text&gt;</span>http://api.mongodb.org/libbson/current/<span style="color: #008000; font-weight: bold">&lt;/xsl:text&gt;</span>
            <span style="color: #008000; font-weight: bold">&lt;xsl:value-of</span> <span style="color: #7D9029">select=</span><span style="color: #BA2121">&quot;$ref&quot;</span><span style="color: #008000; font-weight: bold">/&gt;</span>
            <span style="color: #008000; font-weight: bold">&lt;xsl:text&gt;</span>.html<span style="color: #008000; font-weight: bold">&lt;/xsl:text&gt;</span>
        <span style="color: #008000; font-weight: bold">&lt;/xsl:if&gt;</span>
    <span style="color: #008000; font-weight: bold">&lt;/xsl:template&gt;</span>
<span style="color: #008000; font-weight: bold">&lt;/xsl:stylesheet&gt;</span>
</pre></div>


<p>Pass that to <code>yelp-build -x</code> and Bob, as they say, is your uncle.</p>
<p><a href="http://projectmallard.org/pipermail/mallard-list/2015-April/000216.html"><strong>Read the complete discussion on the Project Mallard mailing list.</strong></a></p>
<hr />
<p><a href="https://commons.wikimedia.org/wiki/File:Mallard_Ducks_Drawing.jpg"><span style="color:gray">Image: Mallard Ducks, John James Audubon.</span></a></p>
    