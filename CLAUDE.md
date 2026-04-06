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
