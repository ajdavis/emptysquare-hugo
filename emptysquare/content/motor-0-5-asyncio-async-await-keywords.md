+++
type = "post"
title = "Announcing Motor 0.5 with asyncio, Python 3.5, and \"async\" / \"await\""
date = "2015-11-30T09:31:39"
description = "This version is compatible with Python 2.6 through 3.5, and it can use either Tornado or asyncio as its async framework."
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "motor-musho.png"
draft = false
disqus_identifier = "565c5ce21e31ec1d4936a7bb"
disqus_url = "https://emptysqua.re/blog/565c5ce21e31ec1d4936a7bb/"
+++

<p><img alt="Motor" border="0" src="motor-musho.png" style="display:block; margin-left:auto; margin-right:auto;" title="motor-musho.png"/></p>
<p>Welcome back, I hope you enjoyed Thanksgiving. I certainly did; among everything for which I give thanks this year, I am grateful for the contributions Rémi Jolin, Andrew Svetlov, and Nikolay Novik made to Motor's asyncio integration. Their help is the greatest gift any project of mine has received.</p>
<p>And now, it's official! Motor 0.5 is released. Install it with:</p>

{{<highlight plain>}}
python -m pip install motor
{{< / highlight >}}

<p>This version of Motor is compatible with Python 2.6 through 3.5, and it can use either Tornado or asyncio. This means pip no longer automatically installs Tornado.</p>
<p>For a detailed description of the changes, <a href="/motor-0-5-beta-asyncio-async-await/">read the beta announcement</a>.</p>
<p>Enjoy!</p>
