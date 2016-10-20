+++
type = "post"
title = "Unittests' code coverage in PyCharm"
date = "2011-11-14T22:29:31"
description = "PyCharm's my favorite IDE in years. Granted, learning how to use it can be like the first few minutes of Flight of the Navigator, but whenever I begin a new kind of task, PyCharm surprises me with the depth of its feature set. Today was my first [ ... ]"
category = ["Programming"]
tag = []
enable_lightbox = false
thumbnail = "coverage-rollup.png"
draft = false
disqus_identifier = "155 http://emptysquare.net/blog/?p=155"
disqus_url = "https://emptysqua.re/blog/155 http://emptysquare.net/blog/?p=155/"
+++

<p><a href="http://www.jetbrains.com/pycharm/">PyCharm</a>'s my favorite IDE in years.
Granted, learning how to use it can be like the <a href="http://www.youtube.com/watch?v=wyXAVTf1Rsc">first few minutes of
Flight of the Navigator</a>,
but whenever I begin a new kind of task, PyCharm surprises me with the
depth of its feature set.</p>
<p>Today was my first day at 10gen. One of my first tasks is to assess the
Mongo Python driver's unittesting coverage. (Summary: coverage is pretty
good, but not great.) Nosetests and
<a href="http://nedbatchelder.com/code/coverage/">coverage.py</a> can give me an
overview, but how awesome would it be if I could see which lines of code
are exercised by the unittests <strong>in my IDE</strong>?</p>
<p>PyCharm, as of the <a href="http://blog.jetbrains.com/pycharm/2011/10/new-pycharm-2-0-eap-build-cython-coffeescript-code-coverage/">October 4 Early Access
Preview</a>,
can run unittests with code coverage analysis within the IDE. Here's
how.</p>
<p><a href="https://github.com/mongodb/mongo-python-driver/">pymongo</a>'s unittests
are all in the tests/ directory, as they ought to be, so in PyCharm you
can simply open the Project pane and right-click the tests/ directory
and choose "Run with Coverage":</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="run-tests.png" title="Run tests" /></p>
<p>PyCharm will show you your tests' outcomes in a nice tree diagram:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="test-results.png" title="Test Results" /></p>
<p>It also displays which lines were exercised by your unittests, and which
were not, in two places. First, in your source files themselves, by
adding a green (exercised) or red (omitted) bar to the left of the
source lines:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="source-coverage.png" title="Source coverage" /></p>
<p>You can see here that I started my local Mongo server without IPv6
support, so the IPv6 unittest was skipped.</p>
<p>You can also see test coverage in your Project pane, neatly rolling up
coverage statistics by file and by directory:</p>
<p><img style="display:block; margin-left:auto; margin-right:auto;" src="coverage-rollup.png" title="Code coverage rollup" /></p>
<p>If you close the project and re-open it, you'll lose your code-coverage
display, but you can redisplay it with Tools->Show Code Coverage Data.
PyCharm will show you coverage data from recent runs and let you
re-display it.</p>
<p>As always with PyCharm, it takes a little fiddling and Googling to get
all this to work, but the result is simply brilliant. I hope this post
helps you find your way through a valuable feature.</p>
