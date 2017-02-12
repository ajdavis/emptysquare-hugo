#!/bin/bash

set -o errexit

~/.virtualenvs/emptysquare-hugo/bin/supervisorctl stop all || true
kill $(cat supervisord.pid) || true
killall hugo || true

~/gocode/bin/hugo --theme=hugo_theme_emptysquare -d public/blog
cp -f static/* public/
netlify deploy -s emptysquare -p public
