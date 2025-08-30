+++
type = "post"
title = "How My Blog Handles Math and Images in HTML, Atom, and Email in 2025"
description = "A stack of kludges that seems to work."
category = ["Programming"]
tag = []
draft = true
enable_lightbox = true
+++

I want to explain computer science on my blog, and show photos, and I want every article to look exquisite. My goal is to display math and images (especially SVGs) as beautifully as possible for people who read my articles on my site, and via Atom and email. This is hard with today's technology, plus I don't have real frontend or design skills. I've recently started [a series of articles about epistemology and distributed systems](/series/knowledge), which included diagrams and equations that broke my existing publication system. I came up with a new stack of kludges that work for me. I'll them down here so I remember, and perhaps you'll learn something you can use.

Throughout this post, you can refer to this map:

![](blog-pipeline.svg)

# My site generator

I use Hugo. I learned about Hugo early, since Steve Francia was my boss at MongoDB when he created it, but I resisted using it for some time. It's not as extensible as the Python-based static site generators, and it relies on Markdown, which is a hacky format. But the various Python generators were all much too slow for me, so eventually I switched. Hugo is super fast enough: even now that my site has 700 articles and thousands of images, it does a full rebuild in under a second.

# Images and previews

While I'm drafting an article, I run the [Hugo server](https://gohugo.io/commands/hugo_server/) and preview the article locally. Whenever I save a change to the article, Hugo rebuilds it and auto-reloads it in the browser. For some reason, Hugo doesn't properly reload when I change an _image_, even though it's perfectly aware that the image has changed. I fixed this by creating [this template](https://github.com/ajdavis/emptysquare-hugo/blob/master/emptysquare/themes/hugo_theme_emptysquare/layouts/_default/_markup/render-image.html):

```go-html-template
{{/* This is layouts/_default/_markup/render-image.html */}}
{{- $img := .Page.Resources.GetMatch .Destination -}}
{{/* to make .IsBlock available see gohugo.io/render-hooks/images */}}
{{- if .IsBlock -}}<p>{{- end -}}
{{- if not $img -}}
  <img src="{{ .Destination | safeURL }}" alt="{{ .Text }}" title="{{ .Title }}">
{{- else -}}
  {{- $r := $img -}}
  {{- if hugo.IsServer -}}
    {{/* Make autoreload work for images with Hugo dev server */}}
    {{- $r = $img | resources.Fingerprint "sha256" -}}
  {{- end -}}
  <img src="{{ $r.RelPermalink }}" alt="{{ .Text }}" title="{{ .Title }}">
{{- end -}}
{{- if .IsBlock -}}</p>{{- end -}}
```

This template interprets Markdown images, like `![](foo.jpg)`. If it's running inside Hugo's development server, then it adds a cache-busting fingerprint to the image URL. Now whenever the contents of `foo.jpg` change, Hugo creates a copy of the file with its hash included in the filename, and updates the HTML page to point to the newly-named file. This shouldn't be necessary&mdash;[this is what ETags are for](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag)&mdash;but Hugo needs this kludge to properly refresh the preview when I change an image.

# Publishing an article

I manage a variety of tasks with some PyCharm custom shortcuts and [an ever-growing Python script called `blog`](https://github.com/ajdavis/emptysquare-hugo/blob/master/blog). Working together, PyCharm and my script can do some advanced tricks, like pasting an image from the macOS clipboard into a Markdown file, or [creating a photo gallery](https://emptysqua.re/blog/aerial-silks-millbrook/), or starting up the Hugo development server and opening the browser to a preview of the file I'm currently editing.

The `blog` script works especially hard when I finish a draft and publish it. I'll describe the publication pipeline below.

I include PNGs, JPEGs, and SVGs in my articles willy-nilly, without worrying about resolution or file size. I love to draw diagrams in [Excalidraw](https://excalidraw.com/) and export them as SVGs like this:

![](raft-states.svg)

_A typical intricate diagram. I drew this for [an article about knowledge](/review-common-knowledge-part-2/)._

When I publish an article, the `blog` script checks for JPEGs or PNGs that are too large, either in dimensions or bytes, and compresses them. If necessary to keep the file size reasonable, it converts a PNG to a JPEG and updates the image reference in the article's text. So far, nothing special here.

# SVGs

I've learned that mail readers (even web-based ones like GMail) won't show SVGs, so I need to give them a fallback. Remember, the article pipeline is HTML &rarr; Atom &rarr; email, so my Atom feed must provide that fallback, which is then passed through Kit to email subscribers.

When I publish a draft, my Python script converts every SVG in the article to a PNG (or a JPEG, if the PNG is too many bytes). I have [a template](https://github.com/ajdavis/emptysquare-hugo/blob/master/emptysquare/themes/hugo_theme_emptysquare/layouts/partials/svg_to_picture.html) that converts every SVG in the feed to a `<picture>` that prefers the SVG but falls back to the PNG or JPEG. This template is called from [the template that generates the whole Atom feed](https://github.com/ajdavis/emptysquare-hugo/blob/master/emptysquare/themes/hugo_theme_emptysquare/layouts/index.rss.xml).

![](svg-pipeline.svg)

# Block and inline images

On a webpage, block images and inline images both render as expected, but I found that by default, email readers either see block images expand to a monstrous width, or else inline images appear as block images, or some combination of the two deformities. [This template](https://github.com/ajdavis/emptysquare-hugo/blob/master/emptysquare/themes/hugo_theme_emptysquare/layouts/_default/_markup/render-image.rss.xml) adds CSS styles to images in the Atom feed to make them behave. It also transforms block images to inline images, wrapped in paragraphs. Somehow this seems to work. 

```go-html-template
{{/* this file is render-image.rss.xml, it's called rss but it makes
     email-safe output for Atom/Kit. Put a block image in a "p" and
     mark inline for proper fill in Atom-to-email campaign */}}
{{- if .IsBlock -}}
<p>
<img src="{{ .Destination | safeURL }}"
     style="display:inline;max-width:100%;
            width:100%;height:auto;margin:1em 0"
     alt="{{ .Text }}" title="{{ .Title }}">
</p>
{{- else -}}
<img src="{{ .Destination | safeURL }}"
     style="display:inline;width:auto;height:auto;
            vertical-align:middle"
     alt="{{ .Text }}" title="{{ .Title }}">
{{- end -}}
```

Besides this hack, I also switched from Mailchimp to Kit (formerly ConvertKit) for my Atom-to-email automation. Mailchimp did some funny business with image widths that I couldn't defeat, but Kit worked well from the start. I didn't experiment to check if the template above is actually necessary with Kit, but at this point I was getting tired of futzing with my blog.

(Note: this template is only executed for Markdown images like `![](foo.jpg)`, not handwritten HTML `<img>` tags in Markdown. I'll have to remember that as I write.)

# Math

A well-rendered formula is beautiful, like this [Riemann sum](https://en.wikipedia.org/wiki/Riemann_sum):

$$S = \sum_{i=1}^{n} f(x_i^*) \, \Delta x_i$$

I use both block formulas like the one above, and also inline formulas, like \(E = mc^2\). By default, [Hugo renders math with client-side Javascript](https://gohugo.io/content-management/mathematics/), but I want to show math on the web using the modern HTML `<math>` tag instead. I accomplish that override with [this template](https://github.com/ajdavis/emptysquare-hugo/blob/0b258f869e87163ea2f7c222f0cd8ad990764e39/emptysquare/themes/hugo_theme_emptysquare/layouts/_markup/render-passthrough.html). Hugo requires it to be called `render-passthrough.html`, but don't be fooled: it's for rendering math specifically. The template also sets a variable `hasMath` to true, so [this other template](https://github.com/ajdavis/emptysquare-hugo/blob/1a25e8c4e5c38cfc9d3e53718952bbecf3022ac5/emptysquare/themes/hugo_theme_emptysquare/layouts/_default/baseof.html#L32) knows to include special math CSS.  

HTML `<math>` tags may not display in Atom readers or email, so once again my Python publication script has a job to do.

![](math-pipeline.svg)

When I publish an article, the script searches it for formulae and converts each to both an SVG and a PNG. The filenames for those images include a hash of the formula itself. Imagine the "xxx" in the filenames above are 64-bit hashes. On the web, you see `<math>` tags rendered by your browser, but in Atom (and therefore in email), you see the SVG, or fall back to the PNG. [This template](https://github.com/ajdavis/emptysquare-hugo/blob/570dfd612b1ce56592f4bc3910c90e457e2e51bb/emptysquare/themes/hugo_theme_emptysquare/layouts/partials/math_to_picture.html) replaces `<math>` tags with `<picture>` tags in the Atom feed, using the hashes of the formulas to determine the correct image filenames.

# Conclusion

![](modern-times.png)

_The feeding machine in Charlie Chaplin's "Modern Times"_

What a [tzimmis](https://en.wikipedia.org/wiki/Tzimmes). What a kludge. Why is all this necessary in 2025? I guess the future is already here, it's [just not evenly distributed](https://www.goodreads.com/quotes/681-the-future-is-already-here-it-s-just-not-evenly): Atom readers are behind the curve, and email readers farther behind, because of security concerns or other issues I don't understand. So I have to build a complicated pipeline to transform math into SVGs, and SVGs into other formats, to ensure graceful degradation. Furthermore, Hugo is fast but hard to customize, and it takes a precarious stack of templates to (usually) produce the HTML that I want, where I want it.

I hope all this is useful to someone else. Maybe you don't need these hacks. Maybe a basic Hugo setup works fine for your blog, or you don't mind if your images don't appear exactly right in all channels. Good for you. But there may come a time when you need more. [I will friend you, if I may, in the dark and cloudy day](https://www.nku.edu/~longa/poems/housman9.html).

![](can-opener.png)

_A Simple Can Opener, Rube Goldberg 1929_
