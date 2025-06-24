+++
category = ["Programming"]
date = "2025-06-23T17:09:48.279404"
description = "Instead of a daily deluge, get a weekly summary."
draft = false
enable_lightbox = true
tag = ["research"]
thumbnail = "edward-bird.jpg"
title = "Taming Google Scholar Alerts"
type = "post"
+++

![A grayscale ink drawing of a bearded old man writing with fountain pen and ink pot, wearing .](edward-bird.jpg)

Since I joined [MongoDB's Distributed Systems Research Group](https://www.mongodb.com/company/research/distributed-systems-research-group) a few years ago, I've relied on Google Scholar alerts to tell me when an author in my specialty publishes a new paper, or (much more often) when a new paper cites an author I'm interested in. Google Scholar can send me email alerts, but their frequency isn't configurable: daily only. And if the same new paper is included in multiple alerts (e.g., it cites several authors I follow), Google Scholar won't deduplicate it. It's common for me to get a half-dozen emails in the morning about overlapping sets of papers.

[I've made a little Google Apps Script automation that solves these problems for me](https://github.com/ajdavis/google-scholar-alert-summary/). Now, I've configured a GMail filter so my daily Google Scholar alerts skip my inbox and don't bother me. Once a week, my script summarizes and deduplicates all the alerts, then deletes them from my GMail archive. This turned a daily chore of cleaning up my inbox into a much easier weekly chore: skimming the titles of this week's papers, in a single email.

***

[Image by Edward Bird](https://www.artic.edu/artworks/82683/bearded-scholar-writing).
