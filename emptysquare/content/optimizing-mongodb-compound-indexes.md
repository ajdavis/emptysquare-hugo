+++
type = "post"
title = "Optimizing MongoDB Compound Indexes"
date = "2012-10-08T13:40:31"
description = "How to find the best multicolumn index for a complex query."
category = ["Mongo", "Programming"]
tag = ["best", "index", "optimization"]
enable_lightbox = false
thumbnail = "beinecke-library@240.jpg"
draft = false
disqus_identifier = "505e42f55393747b3cb3c153"
disqus_url = "https://emptysqua.re/blog/505e42f55393747b3cb3c153/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="beinecke-library.jpg" alt="Beinecke Library, Yale University, 1963" title="Beinecke Library, Yale University, 1963" border="0"   /></p>
<p><a href="http://commons.wikimedia.org/wiki/File:1960s_Yale_5062811384_card_catalog.jpg"><em>Courtesy The Beinecke Library</em></a></p>
<p>How do you create the best index for a complex MongoDB query? I'll present a method specifically for queries that combine equality tests, sorts, and range filters, and demonstrate the best order for fields in a compound index. We'll look at the <code>explain()</code> output to see exactly how well it performs, and we'll see how the MongoDB query-optimizer selects an index.</p>
<hr />
<p>Contents:</p>
<ul>
<li><a href="#setup">The Setup</a></li>
<li><a href="#range">Range Query</a></li>
<li><a href="#equality-plus-range">Equality Plus Range Query</a></li>
<li><a href="#optimizer">The Optimizer</a></li>
<li><a href="#equality-range-sort">Equality, Range Query, And Sort</a></li>
<li><a href="#method">Final Method</a></li>
</ul>
<h2 id="the-setup"><a name="setup"></a>The Setup</h2>
<p>Let's pretend I'm building a comments system like Disqus on MongoDB. (They actually use Postgres, but I'm asking you to use your imagination.) I plan to store millions of comments, but I'll begin with four. Each has a timestamp and a quality rating, and one was posted by an anonymous coward:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">1</span>, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">3</span> }
{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">2</span>, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">5</span> }
{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">3</span>, anonymous<span style="color: #666666">:</span>  <span style="color: #008000; font-weight: bold">true</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span> }
{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">4</span>, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">2</span> }
</pre></div>


<!---
db.comments.insert([    { timestamp: 1, anonymous: false, rating: 3 },
    { timestamp: 2, anonymous: false, rating: 5 },
    { timestamp: 3, anonymous:  true, rating: 1 },
    { timestamp: 4, anonymous: false, rating: 2 }])

-->

<p>I want to query for non-anonymous comments with timestamps from 2 to 4, and order them by rating. We'll build up the query in three stages and examine the best index for each using MongoDB's <code>explain()</code>.</p>
<h2 id="range-query"><a name="range"></a>Range Query</h2>
<p>We'll start with a simple range query for comments with timestamps from 2 to 4:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find( { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> } } )
</pre></div>


<p>There are three, obviously. <code>explain()</code> shows how Mongo found them:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find( { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> } } ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BasicCursor&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">4</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">4</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
    <span style="color: #408080; font-style: italic">// ... snipped output ...</span>
}
</pre></div>


<p>Here's how to read a MongoDB query plan: First look at the cursor type. "BasicCursor" is a warning sign: it means MongoDB had to do a full collection scan. That won't work once I have millions of comments, so I add an index on timestamp:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.createIndex( { timestamp<span style="color: #666666">:</span> <span style="color: #666666">1</span> } )
</pre></div>


<p>The <code>explain()</code> output is now:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find( { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> } } ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor timestamp_1&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
}
</pre></div>


<p>Now the cursor type is "BtreeCursor" plus the name of the index I made. "nscanned" fell from 4 to 3, because Mongo used an index to go directly to the documents it needed, skipping the one whose timestamp is out of range.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="range.png" alt="Range" title="range.png" border="0"   /></p>
<p>For indexed queries, nscanned is the number of <em>index keys</em> in the range that Mongo scanned, and nscannedObjects is the number of <em>documents</em> it looked at to get to the final result. nscannedObjects includes at least all the documents returned, even if Mongo could tell just by looking at the index that the document was definitely a match. Thus, you can see that nscanned &gt;= nscannedObjects &gt;= n always. For simple queries you want the three numbers to be equal. It means you've created the ideal index and Mongo is using it.</p>
<h2 id="equality-plus-range-query"><a name="equality-plus-range"></a>Equality Plus Range Query</h2>
<p>When would nscanned be greater than n? It's when Mongo had to examine some index keys pointing to documents that don't match the query. For example, I'll filter out anonymous comments:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor timestamp_1&quot;</span>,
<span style="background-color: #ffffcc">    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
</span>    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
}
</pre></div>


<p>Although n has fallen to 2, nscanned and nscannedObjects are still 3. Mongo scanned the timestamp index from 2 to 4, which includes both the signed comments and the cowardly one, and it couldn't filter out the latter until it had examined the document itself.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="eq-range-1.png" alt="Equality Check and Range Query 1" title="eq-range-1.png" border="0"   /></p>
<p>How do I get my ideal query plan back, where nscanned = nscannedObjects = n? I could try a compound index on timestamp and anonymous:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.createIndex( { timestamp<span style="color: #666666">:1</span>, anonymous<span style="color: #666666">:1</span> } )
<span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor timestamp_1_anonymous_1&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
}
</pre></div>


<p>This is better: nscannedObjects has dropped from 3 to 2. But nscanned is still 3! Mongo had to scan the range of the index from (timestamp 2, anonymous false) to (timestamp 4, anonymous false), <em>including</em> the entry (timestamp 3, anonymous true). When it scanned that middle entry, Mongo saw it pointed to an anonymous comment and skipped it, without inspecting the document itself. Thus the incognito comment is charged against nscanned but not against nscannedObjects, and nscannedObjects is only 2.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="eq-range-2.png" alt="Equality Check and Range Query 2" title="eq-range-2.png" border="0"   /></p>
<p>Can I improve this plan? Can I get nscanned down to 2, also? You probably know this: the order I declared the fields in my compound index was wrong. It shouldn't be "timestamp, anonymous" but "anonymous, timestamp":</p>
<!---
db.comments.find({ timestamp: { $gte: 2, $lte: 4 }, anonymous: false }).explain(true)
--->

<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.createIndex( { anonymous<span style="color: #666666">:1</span>, timestamp<span style="color: #666666">:1</span> } )
<span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor anonymous_1_timestamp_1&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
}
</pre></div>


<p>Order matters in MongoDB compound indexes, as with any database. If I make an index with "anonymous" first, Mongo can jump straight to the section of the index with signed comments, then do a range-scan from timestamp 2 to 4.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="eq-range-3.png" alt="Equality Check and Range Query 3" title="eq-range-3.png" border="0"   /></p>
<p>So I've shown the first part of my heuristic: equality tests before range filters!</p>
<p>Let's consider whether including "anonymous" in the index was worth it. In a system with millions of comments and millions of queries per day, reducing nscanned might seriously improve throughput. Plus, if the anonymous section of the index is rarely used, it can be paged out to disk and make room for hotter sections. On the other hand, a two-field index is larger than a one-field index and takes more RAM, so the win could be outweighed by the costs. Most likely, the compound index is a win if a significant proportion of comments are anonymous, otherwise not.</p>
<h2 id="digression-how-mongodb-chooses-an-index"><a name="optimizer"></a>Digression: How MongoDB Chooses An Index</h2>
<p>Let's not skip an interesting question. In the previous example I first created an index on "timestamp", then on "timestamp, anonymous", and finally on "anonymous, timestamp". Mongo chose the final, superior index for my query. How?</p>
<p>MongoDB's optimizer chooses an index for a query in two phases. First it looks for a prima facie "optimal index" for the query. Second, if no such index exists it runs an experiment to see which index actually performs best. The optimizer remembers its choice for all similar queries. (Until a thousand documents are modified or an index is added or removed.)</p>
<p>What does the optimizer consider an "optimal index" for a query? The optimal index must include all the query's filtered fields and sort fields. Additionally, any range-filtered or sort fields in the query must come after equality fields. (If there are multiple optimal indexes, Mongo chooses one arbitrarily.) In my example, the "anonymous, timestamp" index is clearly optimal, so MongoDB chooses it immediately.</p>
<p>This isn't a terrifically exciting explanation, so I'll describe how the second phase would work. When the optimizer needs to choose an index and none is obviously optimal, it gathers all the indexes relevant to the query and pits them against each other in a race to see who finishes, or finds 101 documents, first.</p>
<p>Here's my query again:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">db.comments.find({ timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> })
</pre></div>


<p>All three indexes are relevant, so MongoDB lines them up in an arbitrary order and advances each index one entry in turn:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="optimizer.png" alt="Optimizer" title="optimizer.png" border="0"   /></p>
<p>(I omitted the ratings for brevity; I'm just showing the documents' timestamps and anonymosity.)</p>
<p>All the indexes return</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">2</span>, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">5</span> }
</pre></div>


<p>first. On the second pass through the indexes, the left and middle return</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">3</span>, anonymous<span style="color: #666666">:</span>  <span style="color: #008000; font-weight: bold">true</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span> }
</pre></div>


<p>which isn't a match, and our champion index on the right returns</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">{ timestamp<span style="color: #666666">:</span> <span style="color: #666666">4</span>, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">2</span> }
</pre></div>


<p>which <em>is</em> a match. Now the index on the right is finished before the others, so it's declared the winner and used until the next race.</p>
<p>In short: if there are several useful indexes, MongoDB chooses the one that gives the lowest nscanned.</p>
<p><strong>Update:</strong> <a href="/optimizing-mongodb-compound-indexes/#comment-777924667">Betlista reminded me in the comments</a> that you can do <code>explain({ verbose: true })</code> to get all the plans Mongo tried. In this example, there are three relevant indexes, but the verbose explain will only show one plan, because one index is an "optimal index."</p>
<h2 id="equality-range-query-and-sort"><a name="equality-range-sort"></a>Equality, Range Query, And Sort</h2>
<p>Now I have the perfect index to find signed comments with timestamps between 2 and 4. The last step is to sort them, top-rated first:</p>
<!---
db.comments.find({ timestamp: { $gte: 2, $lte: 4 }, anonymous: false }).sort( { rating: -1 } ).explain()
--->

<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).sort( { rating<span style="color: #666666">:</span> <span style="color: #666666">-1</span> } ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor anonymous_1_timestamp_1&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">true</span>
}
</pre></div>


<p>This is the same access plan as before, and it's still good: nscanned = nscannedObjects = n. But now "scanAndOrder" is true. This means MongoDB had to batch up all the results in memory, sort them, and then return them. Infelicities abound. First, it costs RAM and CPU on the server. Also, instead of <a href="http://www.mongodb.org/display/DOCS/Queries+and+Cursors#QueriesandCursors-Executionofqueriesinbatches">streaming my results in batches</a>, Mongo just dumps them all onto the network at once, taxing the RAM on my app servers. And finally, Mongo enforces a 32MB limit on data it will sort in memory. We're only dealing with four comments now, but we're designing a system to handle millions!</p>
<p>How can I avoid scanAndOrder? I want an index where Mongo can jump to the non-anonymous section, and scan that section in order from top-rated to bottom-rated:</p>
<!---
db.comments.find({ timestamp: { $gte: 2, $lte: 4 }, anonymous: false }).sort( { rating: -1 } ).hint({ anonymous:1, rating: 1 }).explain(true)
--->

<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.createIndex( { anonymous<span style="color: #666666">:</span> <span style="color: #666666">1</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span> } )
</pre></div>


<p>Will Mongo use this index? No, because it doesn't win the race to the lowest nscanned. The optimizer does <em>not</em> consider whether the index helps with sorting.<sup id="fnref:1"><a class="footnote-ref" href="#fn:1" rel="footnote">1</a></sup></p>
<p>I'll use a hint to force Mongo's choice:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).sort( { rating<span style="color: #666666">:</span> <span style="color: #666666">-1</span> }
... ).hint( { anonymous<span style="color: #666666">:</span> <span style="color: #666666">1</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span> } ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor anonymous_1_rating_1 reverse&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>
}
</pre></div>


<p>The argument to <code>hint</code> is the same as <code>createIndex</code>. Now nscanned has risen to 3 but scanAndOrder is false. Mongo walks through the "anonymous, rating" index in reverse, getting comments in the correct order, and then checks each document to see if its timestamp is in range.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="eq-range-sort-1.png" alt="Equality Check, Range Query, and Sort 1" title="eq-range-sort-1.png" border="0"   /></p>
<p>This is why the optimizer won't choose this index, but prefers to go with the old "anonymous, <strong>timestamp</strong>" index which requires an in-memory sort but has a lower nscanned.</p>
<p>So I've solved the scanAndOrder problem, at the cost of a higher nscanned. I can't reduce nscanned, but can I reduce nscannedObjects? I'll put the timestamp in the index so Mongo doesn't have to get it from each document:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.createIndex( { anonymous<span style="color: #666666">:</span> <span style="color: #666666">1</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span>, timestamp<span style="color: #666666">:</span> <span style="color: #666666">1</span> } )
</pre></div>


<p>Again, the optimizer won't prefer this index so I have to force it:</p>
<!---
db.comments.find({ timestamp: { $gte: 2, $lte: 4 }, anonymous: false }).sort( { rating: -1 } ).hint({ anonymous:1, rating: 1, timestamp: 1 }).explain()
--->

<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #666666">&gt;</span> db.comments.find(
...     { timestamp<span style="color: #666666">:</span> { $gte<span style="color: #666666">:</span> <span style="color: #666666">2</span>, $lte<span style="color: #666666">:</span> <span style="color: #666666">4</span> }, anonymous<span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span> }
... ).sort( { rating<span style="color: #666666">:</span> <span style="color: #666666">-1</span> }
... ).hint( { anonymous<span style="color: #666666">:</span> <span style="color: #666666">1</span>, rating<span style="color: #666666">:</span> <span style="color: #666666">1</span>, timestamp<span style="color: #666666">:</span> <span style="color: #666666">1</span> } ).explain()
{
    <span style="color: #BA2121">&quot;cursor&quot;</span> <span style="color: #666666">:</span> <span style="color: #BA2121">&quot;BtreeCursor anonymous_1_rating_1_timestamp_1 reverse&quot;</span>,
    <span style="color: #BA2121">&quot;n&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscannedObjects&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">2</span>,
    <span style="color: #BA2121">&quot;nscanned&quot;</span> <span style="color: #666666">:</span> <span style="color: #666666">3</span>,
    <span style="color: #BA2121">&quot;scanAndOrder&quot;</span> <span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">false</span>,
}
</pre></div>


<p>This is as good as it gets. Mongo follows a similar plan as before, moonwalking across the "anonymous, rating, timestamp" index so it finds comments in the right order. But now, nscannedObjects is only 2, because Mongo can tell from the index entry alone that the comment with timestamp 1 isn't a match.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="eq-range-sort-2.png" alt="Equality Check, Range Query, and Sort 2" title="eq-range-sort-2.png" border="0"   /></p>
<p>If my range filter on timestamp is selective, adding timestamp to the index is worthwhile; if it's not selective then the additional size of the index won't be worth the price.</p>
<h2 id="final-method"><a name="method"></a>Final Method</h2>
<p>So here's my method for creating a compound index for a query combining equality tests, sort fields, and range filters:</p>
<ol>
<li>Equality Tests<ul>
<li>Add all equality-tested fields to the compound index, in any order</li>
</ul>
</li>
<li>Sort Fields (ascending / descending only matters if there are multiple sort fields)<ul>
<li>Add sort fields to the index in the same order and direction as your query's sort</li>
</ul>
</li>
<li>Range Filters<ul>
<li>First, add the range filter for the field with the lowest cardinality (fewest distinct values in the collection)</li>
<li>Then the next lowest-cardinality range filter, and so on to the highest-cardinality</li>
</ul>
</li>
</ol>
<p>You can omit some equality-test fields or range-filter fields if they are not selective, to decrease the index size&mdash;a rule of thumb is, if the field doesn't filter out at least 90% of the possible documents in your collection, it's probably better to omit it from the index. Remember that if you have several indexes on a collection, you may need to hint Mongo to use the right index.</p>
<p>That's it! For complex queries on several fields, there's a heap of possible indexes to consider. If you use this method you'll narrow your choices radically and go straight to a good index.</p>
<div class="footnote">
<hr />
<ol>
<li id="fn:1">
<p>Gory details: the scanAndOrder query plan "anonymous, timestamp" wins over the pre-ordered plan "anonymous, rating," because it gets to the end of my small result set first. But if I had a larger result set, then the pre-ordered plan might win. First, because it returns data in the right order, so it crosses the finish line when it finds 101 documents, while a scanAndOrder query plan isn't declared finished until it's found <strong>all</strong> the results. Second, because a scanAndOrder plan quits the race if it reaches 32MB of data, leaving the pre-ordered plans to finish. I told you these details would be gory.&#160;<a class="footnote-backref" href="#fnref:1" rev="footnote" title="Jump back to footnote 1 in the text">&#8617;</a></p>
</li>
</ol>
</div>
