+++
type = "post"
title = "Review of \"Version Control with Git\" by Jon Loeliger"
date = "2012-04-19T07:36:55"
description = "Git is the most powerful and conceptually elegant source code management system I've used. (Perhaps Mercurial rivals it? I haven't used Mercurial.) But it seems to be in a state of arrested development. Many commands commonly used in [ ... ]"
category = ["Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "version-control-with-git.jpg"
draft = false
+++

<p><img style="display:block; margin-left:auto; margin-right:auto;" src="version-control-with-git.jpg" title="Version control with git" /></p>
<p>Git is the most powerful and conceptually elegant source code management
system I've used. (Perhaps Mercurial rivals it? I haven't used
Mercurial.) But it seems to be in a state of arrested development. Many
commands commonly used in ordinary development are basically
unimplemented, and have to be performed with a set of lower-level
commands. For example, publishing a local branch so remote developers
can use it, and then setting up the branch so the remote copy continues
to get updates, is a hard-to-memorize set of 3 commands, whereas it's a
no-brainer in Subversion.</p>
<p>My theory is that Linus Torvalds built the initial git as a set of
low-level commands for managing versioned data in general, and intended
higher-level, more convenient SCMs to be built on top of it. Since Linus
had scratched his own itch, he left the higher-level implementation to
others, but no one rose to the challenge. Now it's too late—git is the
default SCM for open-source projects, and so we're stuck using low-level
commands, or writing custom scripts for common tasks. (Or you can use
<a href="http://www.git-tower.com/">Tower</a>, like me.)</p>
<p>It's as if we had reverted to programming in C. The newfound power is
liberating, but it comes at a price. Whereas I have learned all previous
SCMs casually (CVS, SVN, Perforce), learning git is like learning C. You
won't just pick it up. I've used it professionally for 4 years and I
still flounder occasionally. To use it well, you have to understand it.
You probably have to read a book.</p>
<p>Version Control with Git, by Jon Loeliger from 2009, is a good remedy.
It introduces the reader to git's object model (objects, trees, commits,
refs, tags), and shows how git's everyday commands use its "plumbing"
commands to manipulate these basic materials. The book walks through
detailed examples, including some pathologically-complex merges, and
describes distributed development thoroughly.</p>
<p>If I have a nit to pick, it's that the book's discussion of distributed
development is obsolete. In 2009, it may have been appropriate to spend
a long chapter discussing how to email patches, and how to apply patches
from an email. But these days, GitHub has obviated this process. In my
experience, open-source developers, who need to review each other's
changes before applying them, use GitHub pull requests instead of git's
commands for managing patches over email. I hope a new edition will
drastically cut the section on patches and add a discussion of GitHub's
collaborative features.</p>
<p>If you're not ready to read a whole book, "<a href="http://ftp.newartisans.com/pub/git.from.bottom.up.pdf">Git from the bottom
up</a>" by John
Wiegley provides some of the core concepts.</p>
