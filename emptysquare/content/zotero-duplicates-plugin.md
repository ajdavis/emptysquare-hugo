+++
type = "post"
title = "Deduplicate Your Zotero Library: A Plugin For The Forgetful Scholar"
description = ""
category = []
tag = []
draft = true
enable_lightbox = true
+++

{{% pic src="rembrandt.png" alt="" %}}
"Did I Already Save This Paper?" by Rembrandt
{{% /pic %}}

My usual research workflow is to stumble upon a paper I want to read, add it to Zotero with the Chrome extension, and mark it as "to-read" so it can join its hundreds of unread friends. Then a day or two later I'll stumble upon the same paper again, forget that I've added it, and add it again. (At least I assume it's a day or two later---if I forgot even quicker, how would I know?)

Over time my library acquires a vexing redundancy. Zotero has a built-in duplicate detector, but it only catches items with matching metadata. When I add the same PDF twice, Zotero makes two parent items, each with its own copy of the PDF. Its duplicate detector silently overlooks the Doppelgängers.

{{% pic src="aberdeen.png" alt="" %}}
[Lady Ishbel Aberdeen](https://garystockbridge617.getarchive.net/amp/media/lady-ishbel-aberdeen-1899-iiav-15541-8ad15e) wonders if she already saved this PDF
{{% /pic %}}

I had great success writing [a Zotero plugin for finding papers' metadata](/writing-related-work-section-zotero-overleaf/) a couple months ago, so I made a new plugin: a [Zotero Duplicate Finder](https://github.com/ajdavis/zotero-duplicates-plugin) to clean up after myself. It finds duplicates by title matches or PDFs' MD5 hashes. The first time I ran it, it found several dozen papers that I'd added at least twice. I won't tell you the exact number, for shame. (Reader, it was 63 duplicates. Some were triplets.)

Here's a screenshot from a less embarrassing cleanup:

{{% pic src="dupes-found.png" alt="" / %}}

To use it, install the plugin from [the latest release](https://github.com/ajdavis/zotero-duplicates-plugin/releases/latest), then go to Tools → Find Duplicate Items. The plugin scans your library and shows you groups of duplicates. Uncheck any groups you want to spare, then click "Tag Duplicates." The plugin tags the parent items with "duplicate"---it doesn't delete anything, because I don't trust the plugin and neither should you. The plugin then shows you your duplicate-tagged items.

{{% pic src="filter-by-dupes.png" alt="" / %}}

Deal with them as you see fit. Repeat on occasion, whenever you can't remember the last time you did it, you bunny-brained fool.

{{% pic src="young-woman-reading.png" alt="" %}}
[Osman Hamdi Bey, Young Woman Reading](https://www.bonhams.com/auction/25444/lot/62/osman-hamdi-bey-turkish-1842-1910-young-woman-reading/)
{{% /pic %}}
