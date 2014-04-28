#!/usr/bin/env python

import os
import sys
import shlex, subprocess

import tempita
from conf import bib_dir, build_dir, template_dir, html_dir, arxiv_dir
from options import get_config, mkdir_p

from html_writer import Writer
from conf import papers_dir, output_dir
import options
import glob
import docutils.core as dc

def rst2html(in_path):

    try:
        rst, = glob.glob(os.path.join(in_path, '*.rst'))
    except ValueError:
        raise RuntimeError("Found more than one input .rst--not sure which "
                           "one to use.")

    content = open(rst, 'r').read()

    settings = {
    }

    html_parts = dc.publish_parts(source=content, writer=Writer(), settings_overrides=settings)
    print html_parts['docinfo']

    return tempita.html(html_parts['html_body'].encode('utf-8'))

def arxiv_html(config):
    mkdir_p(arxiv_dir)
    for name in ['index', 'submissions']:
        dest_fn = os.path.join(arxiv_dir, 'arxiv_%s.html' % name)
        template = tempita.HTMLTemplate(open(os.path.join(template_dir, 'arxiv_%s.html.tmpl' % name), 'r').read())
        content = template.substitute(config)
        with open(dest_fn, mode='w') as f:
            f.write(content)

if __name__ == "__main__":

    config = get_config()
    config.update({'preface': rst2html(os.path.join(papers_dir, '01_preface'))})
    arxiv_html(config)

