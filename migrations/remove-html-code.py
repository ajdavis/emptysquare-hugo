"""
2021-06-05. In a past migration I took all the code blocks in my posts and
saved them in Git as raw HTML. This script turns them into Markdown fenced
blocks.
"""
import os
import re
import sys
from os.path import join

from bs4 import BeautifulSoup
from guesslang import Guess

guess = Guess()
content_dir = 'emptysquare/content'
warning_files = []
for root, dirs, files in os.walk(content_dir):
    for fname in files:
        if not fname.endswith('.md'):
            continue

        fpath = join(root, fname)
        print(fpath)
        contents = open(fpath).read()
        match = re.match(r'\+\+\+\n(.*?)\n\+\+\+\n(.*)', contents, re.S)
        if not match:
            print(f'WARNING: {fpath} does not match format')
            warning_files.append(fpath)
            continue

        front = match.group(1)
        body = match.group(2)
        if 'class="codehilite"' not in body:
            continue

        soup = BeautifulSoup(body, 'html.parser')
        for code_div in soup.find_all("div", class_="codehilite"):
            code_text = code_div.get_text().strip()
            if code_text.startswith('>>> '):
                # Guesslang fails this.
                language = 'python'
            else:
                language = guess.language_name(code_text)
                if language == 'SQL':
                    # If this is the guess, it's probably wrong.
                    language = None

                if not language:
                    print(f'WARNING: cannot guess lang for {fpath}')
                    warning_files.append(fpath)
                    language = 'plain'
                elif language == 'C++':
                    language = 'cpp'

            code_div.insert_before('''
{{<highlight %s>}}
%s
{{< / highlight >}}
''' % (language.lower(), code_text))
            code_div.extract()

        with open(fpath, 'wb') as f:
            f.write('+++\n'.encode())
            f.write(front.encode())
            f.write('\n+++\n'.encode())
            f.write(soup.encode(formatter=None))

print('')
print('Files with warnings:')
for fpath in warning_files:
    print(fpath)
