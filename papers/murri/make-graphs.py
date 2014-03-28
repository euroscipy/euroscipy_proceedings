#!/usr/bin/env python
#

show=True
format='pdf'

from collections import defaultdict
import csv
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.ticker import MaxNLocator

import numpy as np # for np.arange()

import pylab


## metadata

pretty_python_names = {
    'py27':               'CPython 2.7.5',
    'pypy':               'PyPy 2.1',
    'cython-bare':        'Cython 0.19.1',
    'cython-purepython':  'Cython 0.19.1 (w/ hints)',
    'cython-pxd':         'Cython 0.19.1 (w/ PXD hints)',
    'nuitka':             'Nuitka 0.4.4',
    'numba':              'Numba @autojit',
}

pretty_field_names = {
    'CPUTIME_SYS':    'CPU time in kernel mode',
    'CPUTIME_USR':    'CPU time',
    'CS_INVOLUNTARY': 'Context switches (involuntary)',
    'CS_VOLUNTARY':   'Context switches (voluntary)',
    'MAJFLT':         'Major page faults',
    'MAXMEM(KB)':     'Max used memory',
    'MINFLT':         'Minor page faults',
    'WCTIME':         'Wall-clock time',
}

units = {
    'CPUTIME_SYS':    's',
    'CPUTIME_USR':    's',
    'CS_INVOLUNTARY': '',
    'CS_VOLUNTARY':   '',
    'MAJFLT':         '',
    'MAXMEM(KB)':     'MiB',
    'MINFLT':         '',
    'WCTIME':         's',
}

conv = {
    'CPUTIME_SYS':    float,
    'CPUTIME_USR':    float,
    'CS_INVOLUNTARY': int,
    'CS_VOLUNTARY':   int,
    'MAJFLT':         int,
    'MAXMEM(KB)':     int,
    'MINFLT':         int,
    'WCTIME':         float,
}

palette = matplotlib.colors.colorConverter.to_rgba_array([
    '#FFB300', # Vivid Yellow
    '#803E75', # Strong Purple
    '#FF6800', # Vivid Orange
    '#A6BDD7', # Very Light Blue
    '#C10020', # Vivid Red
    '#CEA262', # Grayish Yellow
    '#817066', # Medium Gray
    ])


## read data
#
# Example:
#     MGN,CPUTIME_SYS,CPUTIME_USR,CS_INVOLUNTARY,CS_VOLUNTARY,MAJFLT,MAXMEM(KB),MINFLT,PYTHON,RUN_NO,WCTIME
#     M04,1.89,0.20,2,57000,0,39968,5570,py27,1,9.59
#     M04,1.89,0.18,2,58005,0,39968,5570,py27,2,9.50
#     M04,1.88,0.18,6,58340,0,39968,5570,py27,3,9.50
#
usage = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0.0)))
pythons = set()
mgns = set()

csv = csv.DictReader(sys.stdin)
for data in csv:
    mgn = data['MGN']
    mgns.add(mgn)
    python = data['PYTHON']
    pythons.add(python)
    for field in [
            'CPUTIME_SYS',
            'CPUTIME_USR',
            'CS_INVOLUNTARY',
            'CS_VOLUNTARY',
            'MAJFLT',
            'MAXMEM(KB)',
            'MINFLT',
            'WCTIME',
    ]:
        if field == 'MAXMEM(KB)':
            # convert to MiB
            div = 1024
        else:
            div = 1
        used = usage[mgn][field][python]
        if used > 0:
            usage[mgn][field][python] = min(used, float(data[field]) / div)
        else:
            usage[mgn][field][python] = float(data[field]) / div

# sort python runtime names once and for all
pythons = list(sorted(pythons, key=(lambda py: pretty_python_names[py]), reverse=True))

# list of numerical suffixes corresponding to position in a list
#           0     1     2     3     4     5     6     7     8     9
suffixes =['th', 'st', 'nd', 'rd', 'th', 'th', 'th', 'th', 'th', 'th']


## bar plot params
plot_fields = ['CPUTIME_USR', 'MAXMEM(KB)']

npy = len(pythons)
python_names = [ pretty_python_names[py] for py in pythons ]

plot_field_names = [ pretty_field_names[field] for field in plot_fields ]


## plot!

def show_or_save(title):
    if show:
        plt.show()
    else:
        filename = title.replace(' ', '_').replace('(', '').replace(')', '') + '.' + format
        with open(filename, 'w') as output:
            fig = plt.gcf()
            fig.set_size_inches(19., 6.)
            fig.savefig(output, format=format, dpi=600)


for field in plot_fields:
    head = ['Mgn'] + [ pretty_python_names[py] for py in pythons ]
    hdlens = [ len(hd) for hd in head ]
    fmt = str.join('  ', [("%%%ds" % l) for l in hdlens])
    assert len(head) == fmt.count('%')
    print (fmt % tuple(head))
    print (fmt % tuple(('=' * l) for l in hdlens))
    for mgn in sorted(mgns):
        print (fmt % tuple([mgn] + [ usage[mgn][field][py] for py in pythons ]))
    print

sys.exit(0)

for field in plot_fields:

    title = ('%s of Python runtimes (synopsis)' % (pretty_field_names[field],))

    fig, ax1 = plt.subplots(figsize=(19,6))
    plt.subplots_adjust(left=0.115, right=0.88)

    ax1.set_title(title)
    ax1.set_yscale('log')

    keys = list(sorted(mgns, key=(lambda m: usage[m][field]['py27'])))
    n = len(keys)
    for py, color in zip(pythons, palette):
        vals = [ usage[mgn][field][py] for mgn in keys ]
        plt.plot(range(n), vals, color=color, label=pretty_python_names[py])

    pos = np.arange(n) + 0.0
    plt.xticks(pos, keys)

    plt.legend(loc='upper left')

    show_or_save(title)


for mgn in mgns:

    for field in plot_fields:

        title = ('%s of Python runtimes (%s)' % (pretty_field_names[field], mgn))

        rankings = [ usage[mgn][field][py] for py in pythons ]
        sorted_rankings = list(sorted(rankings))

        fig, ax1 = plt.subplots(figsize=(19,6))
        plt.subplots_adjust(left=0.115, right=0.88)

        pos = np.arange(npy)+0.5  # center bars on the Y-axis ticks
        rects = ax1.barh(pos, rankings, align='center', height=0.5, color=palette)

        pylab.yticks(pos, python_names)
        ax1.set_title(title)

        # display actual value next to bar
        min_x, max_x = ax1.get_xlim() #max(rankings)*1.10
        for n, rect in enumerate(rects):
            rank = rankings[n]
            width = rect.get_width()

            x = width + .02*max_x
            y = rect.get_y()+rect.get_height()/2.
            ha = 'left'
            va = 'center'
            if x > .95 * max_x:
                # too far left, place right over bar
                x = width - .02*max_x
                y = rect.get_y() + rect.get_height() * 1.05
                ha = 'right'
                va = 'bottom'
            ax1.text(x, y, ('%g%s' % (conv[field](rank), units[field])), ha=ha, va=va)

            # Lastly, write in the ranking inside each bar to aid in interpretation
            grade = 1 + sorted_rankings.index(rank)

            # Figure out what the last digit (width modulo 10) so we can add
            # the appropriate numerical suffix (e.g., 1st, 2nd, 3rd, etc)
            lastDigit = grade % 10
            # Note that 11, 12, and 13 are special cases
            if (grade == 11) or (grade == 12) or (grade == 13):
                suffix = 'th'
            else:
                suffix = suffixes[lastDigit]

            grade_str = '%d%s' % (grade, suffix)
            if (width < .05*max_x): # The bars aren't wide enough to print the ranking inside
                xloc = width + .01*max_x # Shift the text to the right side of the right edge
                clr = 'black' # Black against white background
                align = 'left'
            else:
                xloc = width - .02*max_x # Shift the text to the left side of the right edge
                clr = 'black'
                align = 'right'
            yloc = rect.get_y()+rect.get_height()/2.0 #Center the text vertically in the bar
            ax1.text(xloc, yloc, grade_str,
                     ha=align, va='center',
                     color=clr, weight='bold')

        show_or_save(title)
