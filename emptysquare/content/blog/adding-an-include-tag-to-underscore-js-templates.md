+++
type = "post"
title = "Adding an \"include\" tag to Underscore.js templates"
date = "2011-11-18T14:32:19"
description = ""
"blog/category" = ["Programming"]
"blog/tag" = ["javascript"]
enable_lightbox = false
draft = false
+++

<p>I use <a href="http://documentcloud.github.com/backbone/">Backbone.js</a> a lot
lately, and since Backbone requires
<a href="http://documentcloud.github.com/underscore/">Underscore.js</a>, I usually
end up using Underscore's templates rather than introducing another
Javascript library dependency like <a href="http://mustache.github.com/">Mustache
templates</a>. But Underscore's
micro-templating language has an omission that bothered me today:
templates can't include each other.</p>
<p>So here's a quick and dirty <code>&lt;% include %&gt;</code> tag for Underscore
templates:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic">// Extend underscore&#39;s template() to allow inclusions</span>
<span style="color: #008000; font-weight: bold">function</span> template(str, data) {
    <span style="color: #408080; font-style: italic">// match &quot;&lt;% include template-id %&gt;&quot;</span>
    <span style="color: #008000; font-weight: bold">return</span> _.template(
        str.replace(
            <span style="color: #BB6688">/&lt;%\s*include\s*(.*?)\s*%&gt;/g</span>,
            <span style="color: #008000; font-weight: bold">function</span>(match, templateId) {
                <span style="color: #008000; font-weight: bold">var</span> el <span style="color: #666666">=</span> <span style="color: #008000">document</span>.getElementById(templateId);
                <span style="color: #008000; font-weight: bold">return</span> el <span style="color: #666666">?</span> el.innerHTML <span style="color: #666666">:</span> <span style="color: #BA2121">&#39;&#39;</span>;
            }
        ),
        data
    );
}
</pre></div>


<p>As you can see, the code simply replaces tags like</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #BC7A00">&lt;%</span> <span style="color: #008000">include</span> foo <span style="color: #BC7A00">%&gt;</span>
</pre></div>


<p>with the contents of the element with id "foo". Use it by throwing code
like this into the body of your HTML page:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">&lt;script </span><span style="color: #7D9029">type=</span><span style="color: #BA2121">&quot;text/template&quot;</span> <span style="color: #7D9029">id=</span><span style="color: #BA2121">&quot;base-template&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>
    Here is a number<span style="color: #666666">:</span> <span style="color: #666666">&lt;%=</span> n <span style="color: #666666">%&gt;</span>
<span style="color: #008000; font-weight: bold">&lt;/script&gt;</span>

<span style="color: #008000; font-weight: bold">&lt;script </span><span style="color: #7D9029">type=</span><span style="color: #BA2121">&quot;text/template&quot;</span> <span style="color: #7D9029">id=</span><span style="color: #BA2121">&quot;imaginary-template&quot;</span><span style="color: #008000; font-weight: bold">&gt;</span>
    <span style="color: #666666">&lt;%</span> include base<span style="color: #666666">-</span>template <span style="color: #666666">%&gt;</span> <span style="color: #666666">+</span> <span style="color: #666666">&lt;%=</span> imaginary <span style="color: #666666">%&gt;</span>i
<span style="color: #008000; font-weight: bold">&lt;/script&gt;</span>
</pre></div>


<p>And in your Javascript code, do this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #408080; font-style: italic">// Outputs &quot;Here&#39;s a number: 17&quot;</span>
<span style="color: #008000; font-weight: bold">function</span> showSimpleNumber() {
    <span style="color: #008000; font-weight: bold">var</span> t <span style="color: #666666">=</span> template($(<span style="color: #BA2121">&#39;#base-template&#39;</span>).html());
    $(<span style="color: #BA2121">&#39;body&#39;</span>).html(t({ n<span style="color: #666666">:</span> <span style="color: #666666">17</span> }));
}

<span style="color: #408080; font-style: italic">// Outputs &quot;Here&#39;s a number: 17 + 42i&quot;</span>
<span style="color: #008000; font-weight: bold">function</span> showComplexNumber() {
    <span style="color: #008000; font-weight: bold">var</span> t <span style="color: #666666">=</span> template($(<span style="color: #BA2121">&#39;#imaginary-template&#39;</span>).html());
    $(<span style="color: #BA2121">&#39;body&#39;</span>).html(t({ n<span style="color: #666666">:</span> <span style="color: #666666">17</span>, i<span style="color: #666666">:</span> <span style="color: #666666">42</span> }));
}
</pre></div>


<p>Enjoy! I leave as an exercise for the reader:</p>
<ol>
<li>Cache included templates so the template() function needn't keep doing document.getElementById().innerHTML for an often-included template</li>
<li>Create replaceable blocks in templates</li>
<li>Pass variables from one template to another</li>
</ol>
    