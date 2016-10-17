+++
type = "post"
title = "Nginx spellcasting"
date = "2011-11-20T22:45:35"
description = "Gandalf in Ralph Bakshi's animated version of The Lord of the Rings. I write the following lines for the sake of future generations, seeking lore about Nginx. Should this omen appear: nginx: [warn] 1024 worker_connections are more than [ ... ]"
"blog/category" = ["Programming"]
"blog/tag" = []
enable_lightbox = false
thumbnail = "BakshiGandalf@240.jpg"
draft = false
legacyid = "188 http://emptysquare.net/blog/?p=188"
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="BakshiGandalf.jpg" title="Gandalf in Ralph Bakshi's animated version of The Lord of the Rings." /></p>
<p>Gandalf in Ralph Bakshi's animated version of The Lord of the Rings.</p>
<p>I write the following lines for the sake of future generations, seeking
lore about Nginx. Should this omen appear:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">nginx: [warn] 1024 worker_connections are more than open file resource limit: 256
</pre></div>


<p>Recite the following incantation in a deep, resonant voice:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">sudo bash; ulimit -n 65536
</pre></div>


<p>Then start Nginx again in the shell in which you called <code>ulimit</code>.</p>
<p>Another spell needful to the young wizard is this, which rids you of all
daemonic Nginxes:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%">ps aux|grep nginx\:\ master\ process|grep -v grep|awk &#39;{ print $2; }&#39;|sudo xargs kill
</pre></div>


<p>Use it wisely.</p>
    