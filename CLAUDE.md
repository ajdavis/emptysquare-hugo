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
