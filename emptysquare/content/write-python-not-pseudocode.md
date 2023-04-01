+++
category = ["Programming"]
date = "2023-04-01T17:06:47.743480"
description = "Use Python: it's less ambiguous, well-known, and concise enough."
draft = false
enable_lightbox = false
tag = []
thumbnail = "92997562_l.jpg"
title = "Pseudocode Is Not Durable"
type = "post"
+++

![](92997562_l.jpg)

My friend Andrew Helwer [argues](https://ahelwer.ca/post/2023-03-30-pseudocode/) that the best way to communicate an algorithm is with [PlusCal](https://en.wikipedia.org/wiki/PlusCal) or Python. He has "come to believe that both are superior to an ad-hoc unspecified pseudo-math language," of the sort that researchers often invent for their papers. He recommends a subset of Python that avoids "fancy features" like list comprehensions, and avoids the standard library. He shows an apt example: a 43-year-old algorithm that was specified in pseudocode and has therefore been plagued with bugs and ambiguities ever since.

I agree with Andrew, and I think Python specifically is the best option for most situations.

* It is the most widely used programming language, and it probably has the largest population of people who can mostly read it, especially a non-fancy subset of the language.
* It is concise enough: nearly as concise as most pseudocode examples and (as Andrew shows) much shorter than PlusCal.
* A Python algorithm can be tested as thoroughly as you want with [property-based testing](https://zhd.dev/sufficiently/), fuzzing, or exhaustive testing, just like a PlusCal algorithm. If you want to formally **prove** its correctness then you'll need PlusCal or another spec language; you should still write the algorithm in Python for the common reader's sake, and test it in Python too!

But whichever language you choose, use an actual executable language. That's the only way to avoid ambiguity and bugs.

(I include PlusCal among the "executable" languages, although "machine-evaluable" is more accurate.)

Andrew proposes one argument **for** pseudocode:

> I do feel that tying algorithms&mdash;these immortal mathematical objects&mdash;to languages relevant within a half-century sliding window cheapens their presentation somehow. I'm old enough to have lived through the waning of several once-popular languages. Pseudocode is timeless!

Here I disagree. Pseudocode is not timeless: authors write pseudocode to resemble the languages with which they're familiar. Pseudocode in old papers looks like COBOL, in middle-aged papers like Pascal, and in recent papers like Python. Authors write pseudocode assuming that all readers have approximately the same cultural context as their own&mdash;they know the same programming languages, the same standard libraries, the same mathematical notations. This is false. To readers familiar with modern languages, old pseudocode is illegible or ambiguous, and there's no way to disambiguate the author's intent. Math notation changes more slowly, but it also does not stand still.

If you publish an algorithm in an executable language today, and specify its version, readers decades from now will have some way to run it or infer how it would run. Again, I recommend Python since it's concise and widely known, but **any** real language is more durable than pseudocode.
