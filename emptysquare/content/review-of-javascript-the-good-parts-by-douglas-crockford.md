+++
type = "post"
title = "Review of \"JavaScript: The Good Parts\" by Douglas Crockford"
date = "2012-06-11T20:44:43"
description = "An obsessive and eccentric book, but well worth reading."
category = ["Programming", "Review"]
tag = ["javascript"]
enable_lightbox = false
thumbnail = "floating-point.png"
draft = false
+++

<p><img src="javascript-the-good-parts.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Javascript the good parts"/></p>
<p>A short, dense book with a pretty butterfly on it, describing a subset
of Javascript and distinguishing which parts of the language "should" be
used and which not. The author is a renowned sage, and he wrote
<a href="https://github.com/douglascrockford/JSLint">JSLint</a>, a widely-used tool
for enforcing his preferences on your scripts. Those preferences are
reflected here.</p>
<p>Some of his opinions seem obsessive and eccentric (it's not OK to write
<code>i++</code>?), but others are invaluable. For example, you should make a habit
of following the Kernighan & Ritchie style of braces: that is, you
should write opening braces ("{") at the end of a line rather than the
beginning of the next line, because if you ever write this:</p>

{{<highlight javascript>}}
return
{
    a: 1
};
{{< / highlight >}}

<p>... it will silently return <code>undefined</code> and ignore your actual return
value. Such precautions, which defend against dangers the novice hasn't
imagined, are born of years of deep Javascript experience. They're this
book's primary worth.</p>
<p>The book claims to be for developers new to Javascript, but some basic
concepts are not very well explained. For example, the book provides a
brief and incomprehensible description of the relationship among
Javascript objects, prototypes, and functions, which will not enlighten
someone not already familiar with Javascript. It then shows workarounds
for implementing a cleaner object model, which is welcome; but if you
don't immediately understand the need for the workaround, read a
different Javascript book than this one.</p>
<p>A large portion of the book is occupied by flowcharts describing the
syntax of the language. For example, half a page is a flowchart
describing how to format floating-point numbers:</p>
<p><img src="floating-point.png" style="display:block; margin-left:auto; margin-right:auto;" title="Floating point"/></p>
<p>If I were a finite-state automaton who wanted to know how to recognize
floating-point numbers, this would be useful for me. Since I am a human
being who can already read and write floating-point numbers, it's an
inexplicable waste of space. I'm baffled that the author thought such
diagrams served any purpose, and that O'Reilly allowed him to include
them and assigned someone to lay them out for publication. If anyone can
explain this to me I'd be grateful.</p>
<p>In all, a useful 30-page paper whining to be released from a 200-page
book. Worth the read, but skip the flowcharts. Evaluate the author's
recommendations for yourself. Use his JSLint tool, but take its output
with a grain of salt.</p>
