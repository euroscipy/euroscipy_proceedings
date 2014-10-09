# Do everything (that is all the figures) in one single file

# Donwload the data ############################
from urllib import urlretrieve
data_names = ['Locust_' + str(i) + '.dat.gz'
              for i in range(1, 5)]
data_src = ['http://xtof.disque.math.cnrs.fr/data/'
            + n for n in data_names]
[urlretrieve(data_src[i], data_names[i])
 for i in range(4)]
# End of Donwload the data ####################

# Decompress the data #########################
import os
[os.system('gunzip ' + n) for n in data_names]
# End of decompress the data ##################

# Load the data ###############################
import numpy as np
import matplotlib.pylab as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

# Create a list with the file names
data_files_names = ['Locust_' + str(i) + '.dat' for i in range(1, 5)]
# Get the lenght of the data in the files
data_len = np.unique(map(len, map(lambda n: np.fromfile(n, np.double),
                                  data_files_names)))[0]
# Load the data in a list of numpy arrays
data = [np.fromfile(n, np.double) for n in data_files_names]
# End of load the data ########################

if 0:
    first_second = np.arange(15000)

    fig = plt.figure(figsize=(3, 5))
    ax = fig.add_subplot(111)

    line1 = [(13000, -52), (14500, -52)]
    (line1_xs, line1_ys) = zip(*line1)
    ax.add_line(mlines.Line2D(line1_xs, line1_ys, lw=2, c='k'))
    ax.text(12800, -56, r'$100 ms$')

    ax.plot(data[0][first_second], color='black', lw=0.3)
    ax.plot(data[1][first_second]-15, color='black', lw=0.3)
    ax.plot(data[2][first_second]-30, color='black', lw=0.3)
    ax.plot(data[3][first_second]-45, color='black', lw=0.3)
    plt.axis('off')
    plt.savefig('Fig1.png')

if 1:
    domain = np.arange(54350, 55851)
    fig = plt.figure(figsize=(3, 5))
    ax = fig.add_subplot(111)

    arrow1 = [(13000, -58), (14500, -58)]
    (arrow1_x, arrow1_y) = zip(*arrow1)
    arrow1 = mpatches.Arrow(207.5, -53, 0., 1.5, width=50., fc='k', ec='k')
    arrow2 = mpatches.Arrow(472.8, -53, 0., 1.5, width=50., fc='r', ec='r')
    arrow3 = mpatches.Arrow(1026.8, -53, 0., 1.5, width=50., fc='b', ec='b')
    arrow4 = mpatches.Arrow(1399.4, -53, 0., 1.5, width=50., fc='y', ec='y')
    ax.add_patch(arrow1)
    ax.add_patch(arrow2)
    ax.add_patch(arrow3)
    ax.add_patch(arrow4)

    ax.plot(data[0][domain], color='black', lw=0.3)
    ax.plot(data[1][domain]-15, color='black', lw=0.3)
    ax.plot(data[2][domain]-30, color='black', lw=0.3)
    ax.plot(data[3][domain]-45, color='black', lw=0.3)
    ax.axis('off')
    plt.savefig('Fig2.png')

plt.show()
