#!/usr/bin/python

import markdown

open('tutorial.html', 'w').write(
    markdown.markdown(open('tutorial.md').read())
    .replace('<h2>', '</article><article><h2>') + '</article>')
