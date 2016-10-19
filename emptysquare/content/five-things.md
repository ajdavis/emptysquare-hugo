+++
type = "post"
title = "Five Things About Scaling MongoDB"
date = "2014-01-19T15:53:04"
description = "Scaling MongoDB is simpler than you think."
category = ["Mongo"]
tag = []
enable_lightbox = false
thumbnail = "king-tree@240.jpg"
draft = false
disqus_identifier = "52dc38935393742de813e627"
disqus_url = "https://emptysqua.re/blog/52dc38935393742de813e627/"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="king-tree.jpg" alt="King Tree" title="King Tree" /></p>
<p>There are a lot of articles about neat hacks for scaling MongoDB, but neat hacks are rarely necessary. MongoDB is designed to scale. Most applications just need to get these five things right.</p>
<h2 id="1-indexes">1. Indexes</h2>
<p>By far the most important aspect of scaling. For every common query on every collection, make sure you have the right indexes in place. Read the MongoDB manual's fine <a href="http://docs.mongodb.org/manual/core/indexes-introduction/">introduction to indexes</a>, and then my long article on <a href="/blog/optimizing-mongodb-compound-indexes/">optimizing compound indexes</a>. The latter offers simple rules for choosing indexes for almost any query.</p>
<h2 id="2-filesystem">2. Filesystem</h2>
<p>On Linux, <a href="http://docs.mongodb.org/manual/administration/production-notes/#mongodb-on-linux">choose ext4 or xfs</a>. Since MongoDB is constantly accessing its files, you can get significant performance by telling Linux not to track files' access times. Add <code>noatime</code> in your <code>/etc/fstab</code>:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"># /etc/fstab
# &lt;file system&gt; &lt;mount point&gt;   &lt;type&gt;  &lt;options&gt;       &lt;dump&gt;  &lt;pass&gt;
/dev/sda1       /               ext4    noatime         0       0
</pre></div>


<h2 id="3-working-set">3. Working Set</h2>
<p>Your working set is the portion of your data that's accessed frequently. On a social network, for example, the newest status updates are accessed far more often than older data. If your working set fits in RAM you can serve most queries from the OS's in-memory cache, without waiting for the disk.</p>
<p>Calculating working set size is a craft. You can estimate it by summing the size of the documents you commonly access or insert, plus all the indexes you use. If you overestimate your working set and buy too much RAM, that's a cheap mistake to make. If you underestimate it a bit, you'll see a high rate of page faults and won't get the best possible performance.</p>
<p>More <a href="http://docs.mongodb.org/manual/faq/diagnostics/#faq-memory">info on working sets is in the manual</a>.</p>
<h2 id="4-disks">4. Disks</h2>
<p>MongoDB uses your disk for random access, so it's the disk's seek time that is the bottleneck, rather than the disk's throughput. All spinning disks are capable of 100 or so seeks per second. If your working set fits in RAM, 100 seeks per second may suffice to serve your sustained load; otherwise, you can increase your seek performance with <a href="http://en.wikipedia.org/wiki/RAID">RAID 10</a>, <a href="http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/raid-config.html">even on EC2</a>. Or use SSDs.</p>
<h2 id="5-shard">5. Shard</h2>
<p>A single replica set can usually meet your performance requirements if you optimize your indexes and configure the filesystem correctly, if your working set fits in RAM and you choose the right disks. You can scale out further, if necessary, by sharding your data across multiple replica sets. This increases the total amount of RAM available in your cluster, since each shard need only cache the data it's responsible for. It also increases your write throughput, since you can write to all shards in parallel.</p>
<p>A sharded cluster is more complex to set up and administer than a replica set. Simple rules: if you don't have to shard, don't. If you must eventually shard, do it now. It's easier to design your application for a sharded cluster early, than to adapt an existing application.</p>
<p>You have many options. Rather than shard, you can put some collections on some replica sets, and other collections on others. Since MongoDB is non-relational, there's no need for all your data to live on the same machine. And if any single collection experiences too much load for one replica set to handle, you can shard just that collection and leave the others unsharded.</p>
<p><a href="http://docs.mongodb.org/manual/core/sharding-introduction/">Sharding is thoroughly covered in the manual</a>.</p>
<hr />
<p>There are always exceptions, of course. Sometimes you'll need more complex techniques to scale MongoDB. But in almost all cases, stick to the basics. These five things will usually get you the performance you need.</p>
