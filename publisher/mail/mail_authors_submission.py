#!/usr/bin/env python

import _mailer as mailer

args = mailer.parse_args()
config = mailer.load_config('email.json')

infile = open("data/esp2015_speakers.csv")
authors = []

for line in infile:
    authors.append({"email": line.split(";")[1],
                    "name": line.split(";")[0].decode("utf8"),
                    "title": line.split(";")[2].strip()})

config["authors"] = authors

for author_info in config['authors']:
    author_config = config.copy()
    author_config.update(author_info)
    author = author_info['email']

    to = mailer.email_addr_from(author_info)
    mailer.send_template(config['sender'], to + ', ' +
                         config['cced'],
                         'invite_authors_submission.txt',
                         author_config)


print "Mail for %d authors." % len(config['authors'])
