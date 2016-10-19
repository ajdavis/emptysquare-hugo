+++
type = "post"
title = "Using jQTouch.js with iButton.js"
date = "2011-10-26T10:27:52"
description = "Fixing an incompatibility between two Javascript libraries for making iOS-like web apps."
category = ["Programming"]
tag = ["javascript"]
enable_lightbox = false
thumbnail = "how_wide@240.png"
draft = false
disqus_identifier = "41 http://emptysquare.net/blog/?p=41"
disqus_url = "https://emptysqua.re/blog/41 http://emptysquare.net/blog/?p=41/"
+++

<p><a href="http://www.jqtouch.com/">jQTouch</a> is a jQuery-based Javascript library
that simulates an iPhone-like interface using only Javascript and HTML5.
It's designed for WebKit browsers (Safari Desktop, Safari Mobile,
Android, Chrome) but is adaptable to Firefox with little work. (Don't
ask about IE.) By default, it renders HTML like this:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">&lt;span</span> <span style="color: #7D9029">class=</span><span style="color: #BA2121">&quot;toggle&quot;</span><span style="color: #008000; font-weight: bold">&gt;&lt;input</span> <span style="color: #7D9029">type=</span><span style="color: #BA2121">&quot;checkbox&quot;</span><span style="color: #008000; font-weight: bold">&gt;&lt;/span&gt;</span>
</pre></div>


<p>... as toggle switches, like this:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Screen-shot-2011-10-25-at-11.48.18-PM.png" title="" /></p>
<p>&nbsp;Another library,
<a href="http://www.givainc.com/labs/ibutton_jquery_plugin.htm">iButton.js</a>, provides
similar functionality but has some advantages: it works on all browsers,
you can easily togglify your checkboxes at runtime, dragging laterally
across the control with your mouse or fingertip works as expected, and
frankly it makes prettier toggles:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="Screen-shot-2011-10-25-at-11.51.51-PM.png" title="" /></p>
<p>So you might be motivated to combine jQTouch with iButton.js. It should
be simple&nbsp;&mdash; just remove all the \&lt;span class="toggle"> tags and run
iButton's initialization method&nbsp;&mdash; but you'll run into some troubles. (If
you don't believe me when I say "troubles", <a href="http://groups.google.com/group/jqtouch/browse_thread/thread/38d5535369ed3511">skim this
discussion</a>.)</p>
<p>So, here's the precise problem with combining these two libraries.</p>
<p>When jQTouch initializes, it styles every top-level div with
display=none, except for the currently showing div. Here's the CSS rules
it uses:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #0000FF">#jqt</span> <span style="color: #666666">&gt;</span> <span style="color: #666666">*</span> {
  <span style="color: #008000; font-weight: bold">display</span><span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">none</span>;
}

<span style="color: #0000FF">#jqt</span> <span style="color: #666666">&gt;</span> <span style="color: #0000FF; font-weight: bold">.current</span> {
  <span style="color: #008000; font-weight: bold">display</span><span style="color: #666666">:</span> <span style="color: #008000; font-weight: bold">block</span> <span style="color: #BC7A00">!important</span>;
  <span style="color: #008000; font-weight: bold">z-index</span><span style="color: #666666">:</span> <span style="color: #666666">10</span>;
}
</pre></div>


<p>This way jQTouch can treat top-level divs like screens (for you iOS
devs, that's a UIViewController) in an iOS app, hiding and showing them
according to where the user is in the navigation stack.</p>
<p>When iButton.js initializes, it wraps every checkbox with its fancy
toggle-control HTML, and then it measures the width of the HTML it
created so it knows how far to slide the toggle control when a user
clicks on it.</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="how_wide.png" title="" /></p>
<p>Alas, it's impossible to measure the width of a hidden element. First
jQTouch hides all but the current div, then iButton tries to initialize
all the toggles, and it thinks they're all zero pixels wide.</p>
<p>My solution is to wait for jQTouch to display a page before I run
iButton on the checkboxes in that page, like so:</p>
<div class="codehilite" style="background: #f8f8f8"><pre style="line-height: 125%"><span style="color: #008000; font-weight: bold">var</span> pagesWithCheckboxes <span style="color: #666666">=</span> _.uniq($(<span style="color: #BA2121">&#39;input</span><span style="color: #BC7A00">[</span><span style="color: #008000; font-weight: bold">type</span><span style="color: #666666">=</span><span style="color: #BA2121">&quot;checkbox&quot;</span><span style="color: #BC7A00">]</span><span style="color: #BA2121">&#39;</span>).closest(<span style="color: #BA2121">&#39;div.page&#39;</span>));
_.each(pagesWithCheckboxes, <span style="color: #008000; font-weight: bold">function</span>(page) {
    <span style="color: #008000; font-weight: bold">var</span> $page <span style="color: #666666">=</span> $(page);
    $page.bind(<span style="color: #BA2121">&#39;pageAnimationEnd&#39;</span>, <span style="color: #008000; font-weight: bold">function</span>(e, info) {
        <span style="color: #008000; font-weight: bold">if</span>(info.direction <span style="color: #666666">===</span> <span style="color: #BA2121">&#39;in&#39;</span>) {
            $page.find(<span style="color: #BA2121">&#39;input</span><span style="color: #BC7A00">[</span><span style="color: #008000; font-weight: bold">type</span><span style="color: #666666">=</span><span style="color: #BA2121">&quot;checkbox&quot;</span><span style="color: #BC7A00">]</span><span style="color: #BA2121">&#39;</span>).iButton();
        }
    });
});
</pre></div>


<p>_.uniq() and _.each() are from underscore.js. I use _uniq() to ensure
I don't bind the event handler multiple times to pages with multiple
checkboxes.</p>
<p>A final note: if you create checkboxes dynamically after the page has
loaded, you must call \$(my_new_checkbox_element).iButton() on them,
once they're visible, to ensure they get the proper toggle-switch
behavior.</p>
