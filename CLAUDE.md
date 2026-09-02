# emptysquare-hugo

Personal blog of A. Jesse Jiryu Davis, built with Hugo.

## Python environment

Use the venv at `./venv` for all Python commands. Do not use system Python.

## Blog script

The `./blog` script is a Click CLI for managing blog posts. Run it with the local venv:

```
./venv/bin/python ./blog <command> <args>
```

Useful commands:

- `blog draft <slug>` --- create a new draft post
- `blog publish <slug>` --- publish a draft
- `blog fix-images <slug>` --- convert Markdown `![alt](path)` images to `{{% pic %}}` shortcodes
- `blog replace-quotes <slug>` --- replace smart quotes with straight quotes
- `blog categories` --- list all categories with counts
- `blog tags` --- list all tags with counts
- `blog preview <slug>` --- open a draft in the browser
- `blog server (start|stop|restart)` -- manage local Hugo server

## Writing blog posts

Posts live in `emptysquare/content/<slug>.md` with associated media in `emptysquare/content/<slug>/`.

When drafting a post, run `blog categories` and `blog tags` to check existing values. Use existing categories and tags; do not create new ones unless explicitly asked.

Insert images with the `{{% pic %}}` shortcode, never with Markdown `![](filename.jpg)`. The `alt` attribute describes the image; anything between the opening and closing tags becomes a caption, and the closing tag is required even with no caption:

```
{{% pic src="filename.jpg" alt="Description of the image" %}}
Optional caption
{{% /pic %}}
```

## Dharma talk posts

Turning a YouTube-recorded dharma talk into a blog post. Ask me for all three inputs before starting:

1. The YouTube link.
2. The transcript, pasted from YouTube.
3. A link to the Google Doc where I wrote the talk before delivering it.

Take the title, summary, and delivery date from the video. Make the slug from the title, then `blog draft <slug>`.

Front matter: `category = ["Zen"]`, `tag = ["dharmatalk"]`, `enable_lightbox = true`, `title`, and `description` set to the summary, shortened to 150 characters if necessary.

Body structure:

```
<summary> This is a dharma talk I gave at the [New Paltz Zen Center](https://npzc.org/) on Month DD, YYYY. Watch the video below, or read the transcript below that.

<youtube embed iframe, with style="margin-bottom: 1em" added to the iframe tag>

{{< subscribe-podcast >}}

***

<transcript>
```

The summary appears twice: in the front matter `description` and at the start of that first paragraph.

Clean up the transcript using the Google Doc as context. Fix mistranscriptions and misspellings, remove "um" and "uh" and other hesitations, and make it grammatical and flowing. Reproduce in the transcript any links that appear in the Google Doc. The result should be properly written but still read as a transcript of somewhat extemporaneous speech, not as an essay. Where the Google Doc and the transcript differ, follow what I actually said when I delivered the talk, not what I wrote beforehand.

Also, when cleaning up the transcript:

- Where the Google Doc has an obvious quotation from a text, copy it verbatim --- including line ends and punctuation --- as a Markdown `>`-prefixed quote block, replacing whatever I was transcribed as saying there.
- Use the paragraph breaks in the Google Doc as a guide for where to break paragraphs in the transcript.
- Use the horizontal lines in the Google Doc as `***` section breaks in the post.
- Remove "like" where it's a 90s-kid spoken tic.
- Remove stage directions such as `[laughter]` unless one seems essential to the talk.
- I start too many sentences with "And". Reduce that where it detracts from the text.
- Don't capitalize "dharma", and fix other capitalizations throughout.

## Publishing blog posts

Do not simply set "draft" to false in the frontmatter. Always use "blog publish": that script does a bunch of image optimization and checks. If "blog publish" fails with an obvious error message, correct the thing it complains about, otherwise ask me what to do.

## Upgrading Hugo

Periodic chore to keep the local Homebrew Hugo, the theme's required version, and Netlify's build version in sync.

1. `hugo version` --- record the current version (e.g. `0.157.0`).
2. From `emptysquare/`, build the current site into a backup dir: `hugo build -d /tmp/hugo-backup-old`.
3. `brew upgrade hugo`, then `hugo version` again. If unchanged, stop.
4. Edit `emptysquare/themes/hugo_theme_emptysquare/layouts/_default/baseof.html`: update the `$hugoVersion` prefix (e.g. `"0.157."` → `"0.161."`, matching `major.minor.`).
5. From `emptysquare/`, build with the new Hugo into a different dir: `hugo build -d /tmp/hugo-backup-new`.
6. `diff -rq /tmp/hugo-backup-old /tmp/hugo-backup-new`. If anything differs, stop and warn me --- do not commit. Deprecation warnings on stderr are fine as long as the diff is empty.
7. If the diff is clean, update `HUGO_VERSION` in `netlify.toml` to the new full version (e.g. `0.161.1`), commit `baseof.html` + `netlify.toml` together, and push to GitHub.
