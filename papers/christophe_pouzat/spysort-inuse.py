# Do everything (that is all the figures) in one single file
import os
import numpy as np
import matplotlib.pylab as plt
from urllib import urlretrieve
from spysort.ReadData import import_data
from spysort.Events import spikes
from spysort.Events import events
from spysort.functions import mad, convolution
from spysort.Events import clusters
from spysort.Events import alignment


if __name__ == '__main__':
    # Donwload the data ############################
    data_names = ['Locust_' + str(i) + '.dat.gz'
                  for i in range(1, 5)]
    data_src = ['http://xtof.disque.math.cnrs.fr/data/'
                + n for n in data_names]
    [urlretrieve(data_src[i], data_names[i]) for i in range(4)]
    # End of Donwload the data ####################

    # Decompress the data #########################
    [os.system('gunzip ' + n) for n in data_names]
    # End of decompress the data ##################

    # Load the data ###############################

    # Create a list with the file names
    data_files_names = ['Locust_' + str(i) + '.dat' for i in range(1, 5)]
    # Get the lenght of the data in the files
    # data_len = np.unique(map(len, map(lambda n: np.fromfile(n, np.double),
    #                     data_files_names)))[0]
    # Load the data in a list of numpy arrays
    # data = [np.fromfile(n, np.double) for n in data_files_names]
    # End of load the data ########################

    # Class read_data instance
    freq = 1.5e4    # Sampling frequency
    data_inst = import_data.read_data(data_files_names, freq)
    # Raw data
    data = data_inst.data

    # Do Fig1 #####################################
    first_second = np.arange(15000)
    fig = plt.figure(figsize=(3, 5))
    plt.plot(data[0][first_second], color='black', lw=0.3)
    plt.plot(data[1][first_second]-15, color='black', lw=0.3)
    plt.plot(data[2][first_second]-30, color='black', lw=0.3)
    plt.plot(data[3][first_second]-45, color='black', lw=0.3)
    plt.axis('off')
    # plt.savefig('Fig1.png')
    # End of do Fig1 ##############################

    # Do Fig2 #####################################
    domain = np.arange(54350, 55851)
    fig = plt.figure(figsize=(3, 5))
    plt.plot(data[0][domain], color='black', lw=0.3)
    plt.plot(data[1][domain]-15, color='black', lw=0.3)
    plt.plot(data[2][domain]-30, color='black', lw=0.3)
    plt.plot(data[3][domain]-45, color='black', lw=0.3)
    plt.axis('off')
    # plt.savefig('Fig2.png')
    # End of do Fig2 ##############################

    # Normalise data and store them in timeseries attribute
    # Timeseries contains the data list and the timesteps
    data_inst.timeseries[0] = data_inst.renormalization()

    win = np.array([1., 1., 1., 1., 1.])/5.  # Boxcar filter
    # Data filtering and spike detection class instance
    s = spikes.spike_detection(data_inst.timeseries)
    # Filter data
    filtered = s.filtering(4.0, win)
    # Find peaks on the sum of the filtered data
    sp0 = s.peaks(filtered, kind='aggregate')

    # Cut data set in two parts
    sp0E = sp0[sp0 <= data_inst.data_len//2]
    sp0L = sp0[sp0 > data_inst.data_len//2]

    # Get events on early part of recording
    evts = events.build_events(data_inst.timeseries[0], sp0E, win, before=14,
                               after=30)
    evtsE = evts.mk_events()

    # define plot_events
    def plot_events(evts_matrix, n_plot=None, n_channels=4,
                    events_color='black', events_lw=0.1, show_median=True,
                    median_color='red', median_lw=0.5, show_mad=True,
                    mad_color='blue', mad_lw=0.5):
        """Plot events.
        Formal parameters:
            evts_matrix: a matrix of events. Rows are events. Cuts from
                         different recording sites are glued one after the
                         other on each row.

            n_plot: an integer, the number of events to plot (if 'None',
                    default, all are shown).

            n_channels: an integer, the number of recording channels.

            events_color: the color used to display events.

            events_lw: the line width used to display events.

            show_median: should the median event be displayed?

            median_color: color used to display the median event.

            median_lw: line width used to display the median event.

            show_mad: should the MAD be displayed?

            mad_color: color used to display the MAD.

            mad_lw: line width used to display the MAD.

            Returns:
                Nothing, the function is used for its side effect.
        """
        if n_plot is None:
            n_plot = evts_matrix.shape[0]
        cut_length = evts_matrix.shape[1] // n_channels
        for i in range(n_plot):
            plt.plot(evts_matrix[i, :], color=events_color, lw=events_lw)
        if show_median:
            MEDIAN = np.apply_along_axis(np.median, 0, evts_matrix)
            plt.plot(MEDIAN, color=median_color, lw=median_lw)
        if show_mad:
            MAD = np.apply_along_axis(mad, 0, evts_matrix)
            plt.plot(MAD, color=mad_color, lw=mad_lw)
        left_boundary = np.arange(cut_length, evts_matrix.shape[1],
                                  cut_length*2)
        for l in left_boundary:
            plt.axvspan(l, l+cut_length-1, facecolor='grey', alpha=0.5,
                        edgecolor='none')
        plt.xticks([])

    # Do Fig3 #####################################
    fig = plt.figure(figsize=(3, 5))
    plt.subplot(411)
    plot_events(evtsE[:200, :45], n_channels=1, show_median=False,
                show_mad=False)
    plt.ylim([-15, 20])
    plt.axis('off')
    plt.subplot(412)
    plot_events(evtsE[:200, 45:90], n_channels=1, show_median=False,
                show_mad=False)
    plt.ylim([-15, 20])
    plt.axis('off')
    plt.subplot(413)
    plot_events(evtsE[:200, 90:135], n_channels=1, show_median=False,
                show_mad=False)
    plt.ylim([-15, 20])
    plt.axis('off')
    plt.subplot(414)
    plot_events(evtsE[:200, 135:], n_channels=1, show_median=False,
                show_mad=False)
    plt.ylim([-15, 20])
    plt.axis('off')
    # plt.savefig('Fig3.png')
    # End of do Fig3 ##############################

    # Dimension reduction and clustering
    CSize = 10
    c = clusters.pca_clustering(data_inst.timeseries[0], sp0E, win, thr=8,
                                before=14, after=30)

    # Do Fig4 #####################################
    c.plot_pca_projections()
    # plt.savefig('Fig4.png')
    # End of do Fig4 ##############################

    # Do clustering with K-Means and 10 clusters
    c10b = c.KMeans(CSize)
    goodEvtsE = c.goodEvts

    # Do Fig5 #####################################
    fig = plt.figure(figsize=(6, 5))
    plt.subplot(421)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 0, :45], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(422)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 1, :45], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(423)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 0, 45:90], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(424)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 1, 45:90], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(425)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 0, 90:135], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(426)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 1, 90:135], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(427)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 0, 135:], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(428)
    plot_events(evtsE[goodEvtsE, :][np.array(c10b) == 1, 135:], n_channels=1,
                show_median=False, mad_color='red')
    plt.ylim([-20, 20])
    plt.axis('off')
    # plt.savefig('Fig5.png')
    # End of do Fig5 ##############################

    dataD = [convolution(x, np.array([1, 0, -1])/2.) for x in
             data_inst.timeseries[0]]
    evtsED = evts.mk_events(otherPos=True, x=np.array(dataD), pos=sp0)
    dataDD = [convolution(x, np.array([1, 0, -1])/2.) for x in dataD]
    evtsEDD = evts.mk_events(otherPos=True, x=np.array(dataDD), pos=sp0)
    c1_median = np.apply_along_axis(np.median, 0,
                                    evtsE[goodEvtsE, :][np.array(c10b) == 1, :],
                                    )
    c1D_median = np.apply_along_axis(np.median, 0,
                                     evtsED[goodEvtsE, :][np.array(c10b) == 1, :],
                                     )
    c1DD_median = np.apply_along_axis(np.median, 0,
                                      evtsEDD[goodEvtsE, :][np.array(c10b) == 1, :]
                                      )
    # First order jitter estimation
    delta_hat = np.dot(c1D_median, evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, :]
            - c1_median) / np.dot(c1D_median, c1D_median)

    align = alignment.align_events(data_inst.timeseries[0], sp0, goodEvtsE,
                                   c10b, CSize, win)

    rss_at_delta_0 = align.rss_for_alignment(delta_hat,
                                             evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],
                                             c1_median,
                                             c1D_median,
                                             c1DD_median)
    rssD_at_delta_0 = align.rssD_for_alignment(delta_hat,
                                               evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],
                                               c1_median,
                                               c1D_median,
                                               c1DD_median)
    rssDD_at_delta_0 = align.rssDD_for_alignment(delta_hat,
                                                 evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],
                                                 c1_median,
                                                 c1D_median,
                                                 c1DD_median)
    delta_1 = delta_hat - rssD_at_delta_0/rssDD_at_delta_0

    # Do Fig6 #####################################
    e1_50_pred = c1_median+delta_1*c1D_median+delta_1**2/2*c1DD_median

    fig = plt.figure(figsize=(6, 5))
    plt.subplot(421)
    plt.plot(c1_median[:45], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, :45],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, :45]-c1_median[:45],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(423)
    plt.plot(c1_median[45:90], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 45:90],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 45:90]-c1_median[45:90],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(425)
    plt.plot(c1_median[90:135], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 90:135],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 90:135]-c1_median[90:135],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(427)
    plt.plot(c1_median[135:], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 135:],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 135:]-c1_median[135:],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(422)
    plt.plot(e1_50_pred[:45], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, :45],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, :45]-e1_50_pred[:45],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(424)
    plt.plot(e1_50_pred[45:90], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 45:90],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 45:90]-e1_50_pred[45:90],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(426)
    plt.plot(e1_50_pred[90:135], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 90:135],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 90:135]-e1_50_pred[90:135],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    plt.subplot(428)
    plt.plot(e1_50_pred[135:], color='blue', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 135:],
             color='black', lw=2)
    plt.plot(evtsE[goodEvtsE, :][np.array(c10b) == 1, :][50, 135:]-e1_50_pred[135:],
             color='red', lw=2)
    plt.ylim([-20, 20])
    plt.axis('off')
    # plt.savefig('Fig6.png')
    # End of do Fig6 ##############################

    centers = {"Cluster " + str(i):
            align.mk_center_dictionary(sp0E[goodEvtsE][np.array(c10b) == i])
            for i in range(CSize)}

    # Apply it to every detected event
    # Warning do it like this
    round0 = [align.classify_and_align_evt(sp0[i], centers) for i in range(len(sp0))]

    print(len([x[1] for x in round0 if x[0] == '?']))

    # Apply it
    pred0 = align.predict_data(round0, centers)
    data1 = np.array(data_inst.timeseries[0]) - pred0
    data_filtered = np.apply_along_axis(lambda x: convolution(x, np.array([1, 1, 1])/3), 1, data1)
    data_filtered = (data_filtered.transpose() / np.apply_along_axis(mad, 1, data_filtered)).transpose()
    data_filtered[data_filtered < 4] = 0
    print data_filtered[0, :].shape
    sp1 = s.peaks(data_filtered[0, :], kind='simple')
    print(len(sp1))

    round1 = [align.classify_and_align_evt(sp1[i], centers,
                                           otherData=True,
                                           x=data1) for i in range(len(sp1))]
    print(len([x[1] for x in round1 if x[0] == '?']))

    pred1 = align.predict_data(round1, centers)
    data2 = data1 - pred1

    # Do Fig7 #####################################
    fig = plt.figure(figsize=(30, 10))
    zz = range(14250, 15000)
    plt.subplot(131)
    plt.plot(np.array(data)[0, zz], color='black')
    plt.plot(pred0[0, zz], color='red', lw=1)
    plt.plot(np.array(data)[1, zz]-25, color='black')
    plt.plot(pred0[1, zz]-25, color='red', lw=1)
    plt.plot(np.array(data)[2, zz]-50, color='black')
    plt.plot(pred0[2, zz]-50, color='red', lw=1)
    plt.plot(np.array(data)[3, zz]-75, color='black')
    plt.plot(pred0[3, zz]-75, color='red', lw=1)
    plt.axis('off')
    plt.ylim([-100, 20])

    plt.subplot(132)
    plt.plot(data1[0, zz], color='black')
    plt.plot(pred1[0, zz], color='red', lw=1)
    plt.plot(data1[1, zz]-25, color='black')
    plt.plot(pred1[1, zz]-25, color='red', lw=1)
    plt.plot(data1[2, zz]-50, color='black')
    plt.plot(pred1[2, zz]-50, color='red', lw=1)
    plt.plot(data1[3, zz]-75, color='black')
    plt.plot(pred1[3, zz]-75, color='red', lw=1)
    plt.axis('off')
    plt.ylim([-100, 20])

    plt.subplot(133)
    plt.plot(data2[0, zz], color='black')
    plt.plot(data2[1, zz]-25, color='black')
    plt.plot(data2[2, zz]-50, color='black')
    plt.plot(data2[3, zz]-75, color='black')
    plt.axis('off')
    plt.ylim([-100, 20])
    plt.subplots_adjust(wspace=0.01, left=0.05, right=0.95,
                        bottom=0.05, top=0.95)
    # plt.savefig('Fig7.png')
    # End of do Fig7 ##############################

    plt.show()
