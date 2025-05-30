+++
type = "post"
title = "Review of \"The Little Book Of Semaphores\" by Allen B. Downey"
date = "2012-05-03T00:23:33"
description = "The Little Book of Semaphores is a free PDF. Whenever I write code to synchronize multiple threads, I always think, \"There must be some method to this.\" I've been warned by the popular adage, \"Any non-trivial multithreaded program has [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
draft = false
+++

<p><a href="http://www.greenteapress.com/semaphores/downey08semaphores.pdf">The Little Book of
Semaphores</a>
is a free PDF.</p>
<p>Whenever I write code to synchronize multiple threads, I always think,
"There must be some method to this." I've been warned by the popular
adage, "Any non-trivial multithreaded program has bugs," which I believe
first appeared in Poor Richard's Almanac. But I have no systematic way
to think about synchronization that assures me I've handled all the
cases. This book does not provide that method. What it <strong>does</strong> provide
is exercises, with solutions, that have developed my facility with
thinking about synchronization, and have shown common synchronization
patterns that should be applicable to almost any real-world problem.</p>
<p>Starting from the most basic cases, the book leads the reader
step-by-step through a series of increasingly complex synchronization
problems, each followed by hints and finally a solution written in a
Python-like pseudocode. Appendices show how to "clean up" Python's and
C's threading libraries to better suit the author's tastes, and to
better match the pseudocode solutions.</p>
<p>The classic synchronization problems included in most Computer Science
curricula tend to use real-world objects to describe their constraints:
E.g., philosophers are dining at a round table, and each needs two
forks. Or, men and women form two lines and they must dance in pairs. In
fact, synchronization problems don't arise on dance floors but in
operating systems and software applications, so the classic descriptions
confuse more than clarify. The author promises to present both the
classic description and the actual software system it arose from, but in
fact only the first few problems are presented this way. The more
advanced problems (such as the dining philosophers) are not tied to
software applications at all. I can't think of any use for the solutions
so I skimmed the later sections.</p>
<p>If you thoroughly absorb the first 10 problems or so, thinking hard and
working out your own solutions, you'll gain some confidence and
familiarity with synchronization which will serve you in nearly all
software challenges you'll actually face. In fact, a few weeks ago I had
to implement a "rendezvous", a pattern in which many threads all reach
the same point at the same time before proceding, and I was surprised to
find I could implement it correctly in Python some years after reading
the book. So invest your time in the first few chapters of the book and
you'll be rewarded. The book's long tail of theoretical puzzles is best
left to grad students.</p>
