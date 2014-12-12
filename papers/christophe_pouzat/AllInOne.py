# Do everything (that is all the figures) in one single file

# Donwload the data ############################
from urllib import urlretrieve
data_names = ['Locust_' + str(i) + '.dat.gz'
              for i in range(1,5)]
data_src = ['http://xtof.disque.math.cnrs.fr/data/'
            + n for n in data_names]
[urlretrieve(data_src[i],data_names[i])
 for i in range(4)]
# End of Donwload the data ####################

# Decompress the data #########################
import os
[os.system('gunzip ' + n) for n in data_names]
# End of decompress the data ##################

# Load the data ###############################
import numpy as np
import matplotlib.pylab as plt

# Create a list with the file names
data_files_names = ['Locust_' + str(i) + '.dat' for i in range(1,5)]
# Get the lenght of the data in the files
data_len = np.unique(map(len, map(lambda n: np.fromfile(n,np.double), data_files_names)))[0]
# Load the data in a list of numpy arrays
data = [np.fromfile(n,np.double) for n in data_files_names]
# End of load the data ########################

# Do Fig1 #####################################
# first_second = np.arange(15000)
# fig = plt.figure(figsize=(3,5))
# plt.plot(data[0][first_second],color='black',lw=0.3)
# plt.plot(data[1][first_second]-15,color='black',lw=0.3)
# plt.plot(data[2][first_second]-30,color='black',lw=0.3)
# plt.plot(data[3][first_second]-45,color='black',lw=0.3)
# plt.axis('off')
# plt.savefig('Fig1.png')
# End of do Fig1 ##############################

# Do Fig2 #####################################
# domain = np.arange(54350,55851)
# fig = plt.figure(figsize=(3,5))
# plt.plot(data[0][domain],color='black',lw=0.3)
# plt.plot(data[1][domain]-15,color='black',lw=0.3)
# plt.plot(data[2][domain]-30,color='black',lw=0.3)
# plt.plot(data[3][domain]-45,color='black',lw=0.3)
# plt.axis('off')
# plt.savefig('Fig2.png')
# End of do Fig2 ##############################

# define mad function
def mad(x):
    return np.median(np.absolute(x - np.median(x)))*1.4826

# get mad
data_mad = [mad(x) for x in data]
# get median
data_median = [np.median(x) for x in data]
# normalise data
data = [(data[i]-data_median[i])/data_mad[i] for i in range(4)]
# filter data
import scipy.signal
data_filtered = [scipy.signal.fftconvolve(x,np.array([1,1,1,1,1])/5.,'same') for x in data]
# rectify filtered data
data_filtered = [(x-np.median(x))/mad(x) for x in data_filtered]
for x in data_filtered:
    x[x < 4] = 0

# define peak
def peak(x, minimalDist=15, notZero=1e-3):
    dx = scipy.signal.fftconvolve(x,np.array([1,0,-1])/2.,'same') ## first derivative
    dx[np.abs(dx) < notZero] = 0
    dx = np.diff(np.sign(dx))
    pos = np.arange(len(dx))[dx < 0]
    return pos[:-1][np.diff(pos) > minimalDist]

# find peaks on the sum of the filtered and rectified traces
import functools
import operator
sp0 = peak(functools.reduce(operator.add,data_filtered))

# cut data set in two parts
sp0E = sp0[sp0 <= data_len/2.]
sp0L = sp0[sp0 > data_len/2.]

# define cut_sgl_evt
def cut_sgl_evt(evtPos,data,before=14, after=30):
    ns = data.shape[0] ## Number of recording sites
    dl = data.shape[1] ## Number of sampling points
    cl = before+after+1 ## The length of the cut
    cs = cl*ns ## The 'size' of a cut
    cut = np.zeros((ns,cl))
    idx = np.arange(-before,after+1)
    keep = idx + evtPos
    within = np.bitwise_and(0 <= keep, keep < dl)
    kw = keep[within]
    cut[:,within] = data[:,kw].copy()
    return cut.reshape(cs) 

# define mk_events 
def mk_events(positions, data, before=14, after=30):
    """Make events matrix out of data and events positions."""
    res = np.zeros((len(positions),(before+after+1)*data.shape[0]))
    for i,p in enumerate(positions): res[i,:] = cut_sgl_evt(p,data,before,after)
    return res 

# get events on early part
evtsE = mk_events(sp0E,np.array(data),14,30)

# define plot_events
def plot_events(evts_matrix, 
                n_plot=None,
                n_channels=4,
                events_color='black', 
                events_lw=0.1,
                show_median=True,
                median_color='red',
                median_lw=0.5,
                show_mad=True,
                mad_color='blue',
                mad_lw=0.5):
    """Plot events.
    Formal parameters:
      evts_matrix: a matrix of events. Rows are events. Cuts from different recording sites are glued
                   one after the other on each row.
      n_plot: an integer, the number of events to plot (if 'None', default, all are shown).
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
    for i in range(n_plot): plt.plot(evts_matrix[i,:], color=events_color, lw=events_lw)
    if show_median:
        MEDIAN = np.apply_along_axis(np.median,0,evts_matrix)
        plt.plot(MEDIAN, color=median_color, lw=median_lw)
    if show_mad:
        MAD = np.apply_along_axis(mad,0,evts_matrix)
        plt.plot(MAD, color=mad_color, lw=mad_lw)
    left_boundary = np.arange(cut_length,evts_matrix.shape[1],cut_length*2)
    for l in left_boundary:
        plt.axvspan(l,l+cut_length-1,facecolor='grey',alpha=0.5,edgecolor='none')
    plt.xticks([])
    return

# define good_evts_fct
def good_evts_fct(samp, thr=3):
    """Returns a boolean vector with as many elements as events in 
    events' matrix samp.

    Formal parameters:
      samp: an events' matrix with as many rows as events.
      thr: a factor by which the MAD is mutiplied in order to build the
           tolerance region.
    Returns:
      A boolean vector with value 'True' if the event is within the tolerance
      region and 'False' otherwise.
    Details: the pointwise median and MAD (median absolute deviation) are first
    calculated from the events' matrix samp. A 'time' region where extra extrema
    are looked for is then defined as the set of indices where the median is negative.
    A tolerance region is constructed as the median +/- thres * MAD in this time 
    region.
    """
    samp_med = np.apply_along_axis(np.median,0,samp)
    samp_mad = np.apply_along_axis(mad,0,samp)
    above = samp_med > 0
    samp_r = samp.copy()
    for i in range(samp.shape[0]): samp_r[i,above] = 0
    samp_med[above] = 0
    res = np.apply_along_axis(lambda x: np.ndarray.all(abs((x-samp_med)/samp_mad) < thr),1,samp_r)
    return res

# use it
goodEvtsE = good_evts_fct(evtsE,8)

# Do Fig3 #####################################
fig = plt.figure(figsize=(3,5))
plt.subplot(411)
plot_events(evtsE[:200,:45][goodEvtsE[:200]==False, :],n_channels=1,
            show_median=False,show_mad=False,events_color='red')
plot_events(evtsE[:200,:45][goodEvtsE[:200]==True, :],n_channels=1,
            show_median=False,show_mad=False)
plt.ylim([-15,20])
plt.axis('off')
plt.subplot(412)
plot_events(evtsE[:200,45:90][goodEvtsE[:200]==False, :],n_channels=1,
            show_median=False,show_mad=False,events_color='red')
plot_events(evtsE[:200,45:90][goodEvtsE[:200]==True, :],n_channels=1,
            show_median=False,show_mad=False)
plt.ylim([-15,20])
plt.axis('off')
plt.subplot(413)
plot_events(evtsE[:200,90:135][goodEvtsE[:200]==False, :],n_channels=1,
            show_median=False,show_mad=False,events_color='red')
plot_events(evtsE[:200,90:135][goodEvtsE[:200]==True, :],n_channels=1,
            show_median=False,show_mad=False)
plt.ylim([-15,20])
plt.axis('off')
plt.subplot(414)
plot_events(evtsE[:200,135:][goodEvtsE[:200]==False, :],n_channels=1,
            show_median=False,show_mad=False,events_color='red')
plot_events(evtsE[:200,135:][goodEvtsE[:200]==True, :],n_channels=1,
            show_median=False,show_mad=False)
plt.ylim([-15,20])
plt.axis('off')
plt.savefig('Fig3.png')
# End of do Fig3 ##############################


# dimension reduction
from numpy.linalg import svd
varcovmat = np.cov(evtsE[goodEvtsE,:].T)
u, s, v = svd(varcovmat)
evtsE_good_P0_to_P3 = np.dot(evtsE[goodEvtsE,:],u[:,0:4])
from pandas.tools.plotting import scatter_matrix
import pandas as pd

# Do Fig4 #####################################
df = pd.DataFrame(evtsE_good_P0_to_P3)
scatter_matrix(df,alpha=0.2,s=4,c='k',figsize=(5,5),diagonal='kde',marker=".")
plt.savefig('Fig4.png')
# End of do Fig4 ##############################

# do clustering with K-Means and 10 clusters
from sklearn.cluster import KMeans
km10 = KMeans(n_clusters=10, init='k-means++', n_init=100, max_iter=100)
km10.fit(np.dot(evtsE[goodEvtsE,:],u[:,0:3]))
c10 = km10.fit_predict(np.dot(evtsE[goodEvtsE,:],u[:,0:3]))
cluster_median = list([(i,np.apply_along_axis(np.median,0,evtsE[goodEvtsE,:][c10 == i,:])) for i in range(10) if sum(c10 == i) > 0])
cluster_size = list([np.sum(np.abs(x[1])) for x in cluster_median])
new_order = list(reversed(np.argsort(cluster_size)))
new_order_reverse = sorted(range(len(new_order)), key=new_order.__getitem__)
c10b = [new_order_reverse[i] for i in c10]

# Do Fig5 #####################################
fig = plt.figure(figsize=(6,5))
plt.subplot(421)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 0,:45],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(422)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 1,:45],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(423)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 0,45:90],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(424)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 1,45:90],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(425)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 0,90:135],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(426)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 1,90:135],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(427)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 0,135:],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(428)
plot_events(evtsE[goodEvtsE,:][np.array(c10b) == 1,135:],n_channels=1,show_median=False,mad_color='red')
plt.ylim([-20,20])
plt.axis('off')
plt.savefig('Fig5.png')
# End of do Fig5 ##############################

# prepare data for jitter illustration
dataD = [scipy.signal.fftconvolve(x,np.array([1,0,-1])/2.,'same') for x in data]
evtsED = mk_events(sp0,np.array(dataD),14,30)
dataDD = [scipy.signal.fftconvolve(x,np.array([1,0,-1])/2.,'same') for x in dataD]
evtsEDD = mk_events(sp0,np.array(dataDD),14,30)
c1_median = np.apply_along_axis(np.median,0,evtsE[goodEvtsE,:][np.array(c10b)==1,:])
c1D_median = np.apply_along_axis(np.median,0,evtsED[goodEvtsE,:][np.array(c10b)==1,:])
c1DD_median = np.apply_along_axis(np.median,0,evtsEDD[goodEvtsE,:][np.array(c10b)==1,:])

# First order jitter estimation
delta_hat = np.dot(c1D_median,evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:]-c1_median)/np.dot(c1D_median,c1D_median)

# Second order jitter estimation
def rss_for_alignment(delta,evt,center,centerD,centerDD):
    return sum((evt - center - delta*centerD - delta**2/2*centerDD)**2)

def rssD_for_alignment(delta,evt,center,centerD,centerDD):
    h = evt - center
    return -2*np.dot(h,centerD) + 2*delta*(np.dot(centerD,centerD) - np.dot(h,centerDD)) + 3*delta**2*np.dot(centerD,centerDD) + delta**3*np.dot(centerDD,centerDD)

def rssDD_for_alignment(delta,evt,center,centerD,centerDD):
    h = evt - center
    return 2*(np.dot(centerD,centerD) - np.dot(h,centerDD)) + 6*delta*np.dot(centerD,centerDD) + 3*delta**2*np.dot(centerDD,centerDD)

rss_at_delta_0 = rss_for_alignment(delta_hat,evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],c1_median,c1D_median,c1DD_median)
rssD_at_delta_0 = rssD_for_alignment(delta_hat,evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],c1_median,c1D_median,c1DD_median)
rssDD_at_delta_0 = rssDD_for_alignment(delta_hat,evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:],c1_median,c1D_median,c1DD_median)
delta_1 = delta_hat - rssD_at_delta_0/rssDD_at_delta_0

# Do Fig6 #####################################
e1_50_pred = c1_median+delta_1*c1D_median+delta_1**2/2*c1DD_median

fig = plt.figure(figsize=(6,5))
plt.subplot(421)
plt.plot(c1_median[:45],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:45],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:45]-c1_median[:45],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(423)
plt.plot(c1_median[45:90],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,45:90],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,45:90]-c1_median[45:90],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(425)
plt.plot(c1_median[90:135],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,90:135],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,90:135]-c1_median[90:135],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(427)
plt.plot(c1_median[135:],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,135:],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,135:]-c1_median[135:],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(422)
plt.plot(e1_50_pred[:45],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:45],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,:45]-e1_50_pred[:45],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(424)
plt.plot(e1_50_pred[45:90],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,45:90],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,45:90]-e1_50_pred[45:90],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(426)
plt.plot(e1_50_pred[90:135],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,90:135],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,90:135]-e1_50_pred[90:135],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.subplot(428)
plt.plot(e1_50_pred[135:],color='blue',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,135:],color='black',lw=2)
plt.plot(evtsE[goodEvtsE,:][np.array(c10b)==1,:][50,135:]-e1_50_pred[135:],color='red',lw=2)
plt.ylim([-20,20])
plt.axis('off')
plt.savefig('Fig6.png')
# End of do Fig6 ##############################

# define mk_center_dictionary
def mk_center_dictionary(positions, data, before=49, after=80):
    from scipy.signal import fftconvolve
    dataD = [fftconvolve(x,np.array([1,0,-1])/2.,'same') for x in data]
    dataDD = [fftconvolve(x,np.array([1,0,-1])/2.,'same') for x in dataD]
    evts = mk_events(positions, np.array(data), before, after)
    evtsD = mk_events(positions, np.array(dataD), before, after)
    evtsDD = mk_events(positions, np.array(dataDD), before, after)
    evts_median = np.apply_along_axis(np.median,0,evts)
    evtsD_median = np.apply_along_axis(np.median,0,evtsD)
    evtsDD_median = np.apply_along_axis(np.median,0,evtsDD)
    return {"center" : evts_median, 
            "centerD" : evtsD_median, 
            "centerDD" : evtsDD_median, 
            "centerD_norm2" : np.dot(evtsD_median,evtsD_median),
            "centerDD_norm2" : np.dot(evtsDD_median,evtsDD_median),
            "centerD_dot_centerDD" : np.dot(evtsD_median,evtsDD_median), 
            "center_idx" : np.arange(-before,after+1)}

# get centers
centers = { "Cluster " + str(i) : mk_center_dictionary(sp0E[goodEvtsE][np.array(c10b)==i],data) for i in range(10)}

# define classify_and_align_evt
def classify_and_align_evt(evt_pos, data, centers, before=14, after=30):
    cluster_names = np.sort(list(centers))
    n_sites = data.shape[0]
    centersM = np.array([centers[c_name]["center"][np.tile((-before <= centers[c_name]["center_idx"]).__and__(centers[c_name]["center_idx"] <= after),n_sites)] \
                         for c_name in cluster_names])
    evt = cut_sgl_evt(evt_pos,data=data,before=before, after=after)
    delta = -(centersM - evt)
    cluster_idx = np.argmin(np.sum(delta**2,axis=1))
    good_cluster_name = cluster_names[cluster_idx]
    good_cluster_idx = np.tile((-before <= centers[good_cluster_name]["center_idx"]).__and__(centers[good_cluster_name]["center_idx"] <= after),n_sites)
    centerD = centers[good_cluster_name]["centerD"][good_cluster_idx]
    centerD_norm2 = np.dot(centerD,centerD)
    centerDD = centers[good_cluster_name]["centerDD"][good_cluster_idx]
    centerDD_norm2 = np.dot(centerDD,centerDD)
    centerD_dot_centerDD = np.dot(centerD,centerDD)
    h = delta[cluster_idx,:]
    h_order0_norm2 = np.sum(h**2)
    h_dot_centerD = np.dot(h,centerD)
    jitter0 = h_dot_centerD/centerD_norm2
    h_order1_norm2 = np.sum((h-jitter0*centerD)**2) 
    if h_order0_norm2 > h_order1_norm2:
        h_dot_centerDD = np.dot(h,centerDD)
        first = -2*h_dot_centerD + 2*jitter0*(centerD_norm2 - h_dot_centerDD) + \
                3*jitter0**2*centerD_dot_centerDD + jitter0**3*centerDD_norm2
        second = 2*(centerD_norm2 - h_dot_centerDD) + 6*jitter0*centerD_dot_centerDD + \
                 3*jitter0**2*centerDD_norm2
        jitter1 = jitter0 - first/second
        h_order2_norm2 = np.sum((h-jitter1*centerD-jitter1**2/2*centerDD)**2)
        if h_order1_norm2 <= h_order2_norm2:
            jitter1 = jitter0
    else:
        jitter1 = 0
    if abs(round(jitter1)) > 0:
        evt_pos -= int(round(jitter1))
        evt = cut_sgl_evt(evt_pos,data=data,before=before, after=after)
        h = evt - centers[good_cluster_name]["center"][good_cluster_idx]
        h_order0_norm2 = np.sum(h**2)
        h_dot_centerD = np.dot(h,centerD)
        jitter0 = h_dot_centerD/centerD_norm2
        h_order1_norm2 = np.sum((h-jitter0*centerD)**2) 
        if h_order0_norm2 > h_order1_norm2:
            h_dot_centerDD = np.dot(h,centerDD)
            first = -2*h_dot_centerD + 2*jitter0*(centerD_norm2 - h_dot_centerDD) + \
                    3*jitter0**2*centerD_dot_centerDD + jitter0**3*centerDD_norm2
            second = 2*(centerD_norm2 - h_dot_centerDD) + 6*jitter0*centerD_dot_centerDD + \
                     3*jitter0**2*centerDD_norm2
            jitter1 = jitter0 - first/second
            h_order2_norm2 = np.sum((h-jitter1*centerD-jitter1**2/2*centerDD)**2)
            if h_order1_norm2 <= h_order2_norm2:
                jitter1 = jitter0
        else:
            jitter1 = 0
    if np.sum(evt**2) > np.sum((h-jitter1*centerD-jitter1**2/2*centerDD)**2):
        return [cluster_names[cluster_idx], evt_pos, jitter1]
    else:
        return ['?',evt_pos, jitter1]

# Apply it to every detected event
# Warning do it like this
data0 = np.array(data)
round0 = [classify_and_align_evt(sp0[i],data0,centers) for i in range(len(sp0))]
# instead of like that
# round0 = [classify_and_align_evt(sp0[i],np.array(data),centers) for i in range(len(sp0))]
# With this second way the code spends all the time converting again and again (1785 times)
# the list data into a matrix... 
print(len([x[1] for x in round0 if x[0] == '?']))

# define predict_data
def predict_data(class_pos_jitter_list, centers_dictionary, nb_channels=4, data_length=300000):
    res = np.zeros((nb_channels,data_length))
    for class_pos_jitter in class_pos_jitter_list:
        cluster_name = class_pos_jitter[0]
        if cluster_name != '?':
            center = centers_dictionary[cluster_name]["center"]
            centerD = centers_dictionary[cluster_name]["centerD"]
            centerDD = centers_dictionary[cluster_name]["centerDD"]
            jitter = class_pos_jitter[2]
            pred = center + jitter*centerD + jitter**2/2*centerDD
            pred = pred.reshape((nb_channels,len(center)//nb_channels))
            idx = centers_dictionary[cluster_name]["center_idx"] + class_pos_jitter[1]
            within = np.bitwise_and(0 <= idx, idx < data_length)
            kw = idx[within]
            res[:,kw] += pred[:,within]
    return res

# Apply it
from scipy.signal import fftconvolve
pred0 = predict_data(round0,centers)
data1 = np.array(data) - pred0
data_filtered = np.apply_along_axis(lambda x:
        fftconvolve(x,np.array([1,1,1])/3.,'same'),1,data1)
data_filtered = (data_filtered.transpose() / np.apply_along_axis(mad,1,data_filtered)).transpose()
data_filtered[data_filtered < 4] = 0
sp1 = peak(data_filtered[0,:])
print(len(sp1))

round1 = [classify_and_align_evt(sp1[i],data1,centers) for i in range(len(sp1))]
print(len([x[1] for x in round1 if x[0] == '?']))

pred1 = predict_data(round1,centers)
data2 = data1 - pred1

# Do Fig7 #####################################
fig = plt.figure(figsize=(30,10))
zz = range(14250,15000)
plt.subplot(131)
plt.plot(np.array(data)[0,zz], color='black')
plt.plot(pred0[0,zz], color='red',lw=1)
plt.plot(np.array(data)[1,zz]-25, color='black')
plt.plot(pred0[1,zz]-25, color='red',lw=1)
plt.plot(np.array(data)[2,zz]-50, color='black')
plt.plot(pred0[2,zz]-50, color='red',lw=1)
plt.plot(np.array(data)[3,zz]-75, color='black')
plt.plot(pred0[3,zz]-75, color='red',lw=1)
plt.axis('off')
plt.ylim([-100,20])

plt.subplot(132)
plt.plot(data1[0,zz], color='black')
plt.plot(pred1[0,zz], color='red',lw=1)
plt.plot(data1[1,zz]-25, color='black')
plt.plot(pred1[1,zz]-25, color='red',lw=1)
plt.plot(data1[2,zz]-50, color='black')
plt.plot(pred1[2,zz]-50, color='red',lw=1)
plt.plot(data1[3,zz]-75, color='black')
plt.plot(pred1[3,zz]-75, color='red',lw=1)
plt.axis('off')
plt.ylim([-100,20])

plt.subplot(133)
plt.plot(data2[0,zz], color='black')
plt.plot(data2[1,zz]-25, color='black')
plt.plot(data2[2,zz]-50, color='black')
plt.plot(data2[3,zz]-75, color='black')
plt.axis('off')
plt.ylim([-100,20])
plt.subplots_adjust(wspace=0.01,left=0.05,right=0.95,bottom=0.05,top=0.95)
plt.savefig('Fig7.png')
# End of do Fig7 ##############################
