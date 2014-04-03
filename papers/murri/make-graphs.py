#!/usr/bin/env python
#

show=False
format='pdf'
figsize=(8.9,3)
synopsis_figsize=(14, 4)

from collections import defaultdict
import csv
import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors
plt.rcParams['figure.figsize'] = figsize
plt.rcParams['legend.fontsize'] = 12

import numpy as np # for np.arange()

import pylab

#import texttable as tt


## metadata

pretty_python_names = {
    'py27':               'CPython 2.7.5',
    'pypy':               'PyPy 2.1',
    'cython-bare':        'Cython 0.19.1',
    'cython-purepython':  'Cython 0.19.1\n(w/ hints)',
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

pretty_mgn_names = {
    'M04': '$M_{0,4}$',
    'M21': '$M_{2,1}$',
    'M05': '$M_{0,5}$',
    'M13': '$M_{1,3}$',
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

# enlarge default font size
plt.rc('font', size=16.)

def show_or_save(title, figsize=figsize):
    if show:
        plt.show()
    else:
        filename = title.replace(' ', '_').replace('(', '').replace(')', '') + '.' + format
        with open(filename, 'w') as output:
            fig = plt.gcf()
            fig.set_size_inches(figsize[0],figsize[1])
            fig.savefig(output, format=format, dpi=600)


# text tables with numeric results
# for field in plot_fields:
if False:
    table = tt.Texttable()
    head = ['Mgn'] + [ pretty_python_names[py] for py in pythons ]
    hdlens = [ len(hd) for hd in head ]
    fmt = str.join('  ', [("%%%ds" % l) for l in hdlens])
    assert len(head) == fmt.count('%')
    table.header(head)
    for mgn in sorted(mgns):
        table.add_row(tuple([mgn] + [ usage[mgn][field][py] for py in pythons ]))
    print table.draw()


# figures 1 and 2
n = len(mgns)
m = len(pythons)
for field in plot_fields:
    title = ('%s of Python runtimes (synopsis)' % (pretty_field_names[field],))

    fig, ax = plt.subplots(figsize=synopsis_figsize)
    plt.subplots_adjust(left=0.115, right=0.88)

    ax.set_title(title)

    keys = list(sorted(mgns, key=(lambda m: usage[m][field]['py27'])))
    pos = np.arange(n) + 0.0
    barwidth = fig.get_figwidth() / (n * (1 + m)) / 5
    for i, (py, color) in enumerate(zip(pythons, palette)):
        vals = np.array([ usage[mgn][field][py] for mgn in keys ])
        rects = ax.bar((pos + i*barwidth), (np.log(vals + 1) / np.log(10)), barwidth,
                       color=color, label=pretty_python_names[py])

        # display actual value over bar
        min_y, max_y = ax.get_ylim()
        for j, rect in enumerate(rects):
            h = rect.get_height()
            x = rect.get_x()+rect.get_width()/10.
            y = h - .04*max_y
            ha = 'left'
            va = 'top'
            if y < .10 * max_y:
                # too far up, place right over bar
                y = h + .04*max_y
                va = 'bottom'
            ax.text(x, y, ('%.2f%s' % (vals[j], units[field])),
                    ha=ha, va=va, rotation=-90)

    plt.xticks(pos + (n*barwidth/2),
               [ pretty_mgn_names[k] for k in keys ])
    plt.yticks(ax.get_yticks(),
               [ ("%d%s" % ((10**y if y != 0 else 0), units[field]))
                 for y in ax.get_yticks() ])

    if field != 'MAXMEM(KB)':
        plt.legend(loc='upper left')

    show_or_save(title, synopsis_figsize)


# remaining figures
for mgn in mgns:

    for field in plot_fields:
        title = ('%s of Python runtimes (%s)' % (pretty_field_names[field], mgn))

        rankings = [ usage[mgn][field][py] for py in pythons ]
        sorted_rankings = list(sorted(rankings))

        fig, ax = plt.subplots(figsize=figsize)
        plt.subplots_adjust(left=0.190, right=0.92)

        pos = np.arange(npy)+0.5  # center bars on the Y-axis ticks
        rects = ax.barh(pos, rankings, align='center', height=0.5, color=palette)

        pylab.yticks(pos, python_names)
        ax.set_title(title)

        # display actual value next to bar
        min_x, max_x = ax.get_xlim() #max(rankings)*1.10
        if mgn=='M13':
            ax.set_xlim(min_x, max_x*1.2)
        else:
            ax.set_xlim(min_x, max_x*1.1)
        min_x, max_x = ax.get_xlim() #max(rankings)*1.10
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
            ax.text(x, y, ('%g%s' % (conv[field](rank), units[field])), ha=ha, va=va)

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
            ax.text(xloc, yloc, grade_str,
                     ha=align, va='center',
                     color=clr, weight='bold')

        show_or_save(title)
