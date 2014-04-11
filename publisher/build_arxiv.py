#!/usr/bin/env python

import os
import sys
import shlex, subprocess

import tempita
from conf import bib_dir, build_dir, template_dir, html_dir, arxiv_dir
from options import get_config

def arxiv_html(config):
    dest_fn = os.path.join(arxiv_dir, 'arxiv_index.html')
    template = tempita.HTMLTemplate(open(os.path.join(template_dir, 'arxiv_index.html.tmpl'), 'r').read())
    content = template.substitute(config)
    with open(dest_fn, mode='w') as f:
        f.write(content)

if __name__ == "__main__":

    config = get_config()
    arxiv_html(config)

