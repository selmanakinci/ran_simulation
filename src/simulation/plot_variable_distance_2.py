import csv
import os
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data
import matplotlib.patches as mpatches

# plot moving avg
def moving_average(interval, window_size):
    window = np.ones (int (window_size)) / float (window_size)
    return np.convolve (interval, window, 'same')

no_of_slices = 3
no_of_users_list = (10, 10, 10)

# region : Read simulation results
c_algo = 'mcqi'
parent_dir = 'baseline comparison data/final_results/variable_distance' #/'+c_algo

# region : Plot rb distributions
# s1 = np.random.randint(6,11,size=10000)
# s2 = np.random.randint(6,11,size=10000)
# s3 = 24- (s1+s2)
# s1 += np.random.randint(0,3,size=10000)
# s2 += np.random.randint(0,3,size=10000)
# s3 += np.random.randint(0,3,size=10000)
# c = np.array([s1,s2,s3])*4
# c1=c.reshape (3, 50, 200)
# c2 = np.mean(c1,axis=2)
# pyplot.plot(c2[0],'r--',label="x vs y1")
# pyplot.plot(c2[1],'g--',label="x vs y2")
# pyplot.plot(c2[2],'b--',label="x vs y3")
# filename = parent_dir + "/rb_dist.png"
# pyplot.savefig(filename)
# pyplot.show()
# endregion


# region : Plotting tp2 of users boxplot
for c_algo in ['rr','mcqi','pf','rl']:
    fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(10,10))
    pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
    for tick in axes.xaxis.get_major_ticks():
                    tick.label.set_fontsize(14)
    for tick in axes.yaxis.get_major_ticks():
                    tick.label.set_fontsize(14)
    if c_algo == 'rr':
        # data = [np.array([1241,1445,1700,1785]), np.array([446,1445,2700,4725]), np.array([1372,1445,1700,1890])] # rr
        data = [np.array ([1795, 1976, 1995, 2200]), np.array ([705, 1250, 1700, 2215]),
                np.array ([1765, 1850, 2005, 2170])]  # rr
    elif c_algo == 'mcqi':
        #data = [np.array([426,525,775,1718,2718,3354]), np.array([146,250,1445,3700,4725,6718]), np.array([486,725,975,1718,2718,3754])] # mcqi
        data = [np.array ([360, 720, 880, 1200, 1900, 2176, 2125, 2200]), np.array ([1350, 1600, 2016, 2125, 2215]),
                np.array ([640, 1380, 1500, 2100, 2125, 2170])]  # mcqi
    elif c_algo == 'pf':
        data = [np.array ([1822, 1990, 1955, 2200]), np.array ([751, 1260, 1740, 2215]),
                np.array ([1826, 1990, 2004, 2170])]  # pf
    elif c_algo == 'rl':
        data = [np.array ([1610, 1746, 1985, 2050]), np.array ([1225, 1450, 1800, 2215]),
                np.array ([1665, 1750, 1955, 2084])]  # rl

    bp1 = axes.boxplot(data, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
    axes.plot([np.nan]+[1500]*3, linestyle='--', color='r',marker='')

    for line in bp1['means']:
        # get position data for median line
        x, y = line.get_xydata()[1] # top of median line
        # overlay median value
        pyplot.text(x+0.30, y, '%.1f' % y,
             horizontalalignment='center', fontsize=14) # draw above, centered
    for line in bp1['whiskers']:
        # get position data for median line
        x, y = line.get_xydata()[1] # top of median line
        # overlay median value
        pyplot.text(x+0.3, y, '%.1f' % y,
             horizontalalignment='center', fontsize=14) # draw above, centered
    fig.suptitle('Controller Algorithm: ' + c_algo, fontsize=18)
    axes.set_xlabel('Slice Scheduler', fontsize=18)
    axes.set_ylabel('Throughput [kbps]', fontsize=18)

    filename = parent_dir + "/tp_boxplot_" + c_algo + ".png"
    pyplot.grid ()
    pyplot.savefig(filename)
    pyplot.close(fig)
    pyplot.show()
# endregion

# region : packet_served_SLA/packet_arrived  avg boxplot
fig, axes = pyplot.subplots (nrows=1, ncols=1, figsize=(17, 12))
pyplot.setp (axes, xticklabels=['RR', 'MCQI', 'PF', 'RL'] * 3)  # Set the ticks and ticklabels for all axes

positions = [0, 0.5, 1, 1.5, 3, 3.5, 4, 4.5, 6, 6.5, 7, 7.5]
for tick in axes.xaxis.get_major_ticks ():
    tick.label.set_fontsize (14)
for tick in axes.yaxis.get_major_ticks ():
    tick.label.set_fontsize (14)


# if c_algo == 'rr':
data_rr = [np.array ([1795, 1976, 1995, 2200]), np.array ([705, 1250, 1700, 2215]),
                np.array ([1765, 1850, 2005, 2170])] # rr
# elif c_algo == 'mcqi':
data_mcqi = [np.array ([360, 720, 880, 1200, 1900, 2176, 2125, 2200]), np.array ([1350, 1600, 2016, 2125, 2215]),
                np.array ([640, 1380, 1500, 2100, 2125, 2170])] # mcqi
# elif c_algo == 'rl':
data_rl = [np.array ([1610, 1746, 1985, 2050]), np.array ([1225, 1450, 1800, 2215]),
                np.array ([1665, 1750, 1955, 2084])]  # rl
# elif c_algo == 'pf':
data_pf = [np.array ([1822, 1990, 1955, 2200]), np.array ([751, 1260, 1740, 2215]),
                np.array ([1826, 1990, 2004, 2170])]  # pf
data = [data_rr[0], data_mcqi[0], data_pf[0], data_rl[0], data_rr[1], data_mcqi[1], data_pf[1], data_rl[1], data_rr[2],
        data_mcqi[2], data_pf[2], data_rl[2]]
colors = ['forestgreen', 'firebrick', 'gold', 'royalblue'] * 3
# boxplot
bp1 = axes.boxplot (data, notch=False, widths=0.25, patch_artist=True, manage_ticks=True, showmeans=True, meanline=True,
                    positions=positions)
axes.plot([1500]*9, linestyle='--', color='r')
for patch, color in zip (bp1['boxes'], colors):
    patch.set_facecolor (color)
for line in bp1['means']:
    # get position data for median line
    x, y = line.get_xydata ()[1]  # top of median line
    # overlay median value
    #pyplot.text (x + 0.15, y, '%.2f' % y,
    #             horizontalalignment='center', fontsize=14)  # draw above, centered
# for line in bp1['whiskers']:
#     # get position data for median line
#     x, y = line.get_xydata()[1] # top of median line
#     # overlay median value
#     pyplot.text(x+0.2, y, '%.2f' % y,
#          horizontalalignment='center', fontsize=14) # draw above, centered
rr_patch = mpatches.Patch (color='forestgreen', label='RR')
mcqi_patch = mpatches.Patch (color='firebrick', label='MCQI')
pf_patch = mpatches.Patch (color='gold', label='PF')
a2c_patch = mpatches.Patch (color='royalblue', label='A2C')
axes.legend (handles=[rr_patch, mcqi_patch, pf_patch, a2c_patch], title="Controller Algorithm", fontsize=15,
             title_fontsize=15)
# fig.suptitle('Packet Success Ratio Comparison', fontsize=18)
axes.set_xlabel ('Controller Algorithm', fontsize=18)
axes.set_ylabel ('Throughput [kbps]', fontsize=18)
filename = parent_dir + "/tp_boxplot.png"
# pyplot.grid ()
pyplot.savefig (filename)
pyplot.show ()
# endregion

# region : Plotting delay of users boxplot
# fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
# pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
# for tick in axes.xaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)
# for tick in axes.yaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)
#
# data = [np.array([1,2,4]), np.array([1,2,4]), np.array([1,2,4])]
#
# bp1 = axes.boxplot(data, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
# for line in bp1['means']:
#     # get position data for median line
#     x, y = line.get_xydata()[1] # top of median line
#     # overlay median value
#     pyplot.text(x+0.25, y, '%.1f' % y,
#          horizontalalignment='center', fontsize=14) # draw above, centered
# for line in bp1['whiskers']:
#     # get position data for median line
#     x, y = line.get_xydata()[1] # top of median line
#     # overlay median value
#     pyplot.text(x+0.3, y, '%.1f' % y,
#          horizontalalignment='center', fontsize=14) # draw above, centered
# fig.suptitle('Controller Algorithm: ' + c_algo, fontsize=18)
# axes.set_xlabel('Slice Scheduler', fontsize=18)
# axes.set_ylabel('Delay [ms]', fontsize=18)
#
# filename = parent_dir + "/delay_boxplot.png"
# pyplot.savefig(filename)
# pyplot.close(fig)
# pyplot.show()
# endregion

# region : packet_served_SLA/packet_arrived  avg boxplot
fig, axes = pyplot.subplots (nrows=1, ncols=1, figsize=(17, 12))
pyplot.setp (axes, xticklabels=['RR', 'MCQI', 'PF', 'RL'] * 3)  # Set the ticks and ticklabels for all axes

positions = [0, 0.5, 1, 1.5, 3, 3.5, 4, 4.5, 6, 6.5, 7, 7.5]
for tick in axes.xaxis.get_major_ticks ():
    tick.label.set_fontsize (14)
for tick in axes.yaxis.get_major_ticks ():
    tick.label.set_fontsize (14)


# if c_algo == 'rr':
data_rr = [np.array ([1, 1, 1]), np.array ([0.35, 0.71, 1]), np.array ([1, 1, 1])]  # rr
# elif c_algo == 'mcqi':
data_mcqi = [np.array ([0.17, 0.3, 0.7, 0.85, 0.91, 1]), np.array ([0.7, 0.9, 1]),
             np.array ([0.4, 0.6, 0.85, 0.91, 1])]  # mcqi
# elif c_algo == 'rl':
data_rl = [np.array ([0.9, 1, 1]), np.array ([0.65, 0.85, 1]), np.array ([0.95, 1, 1])]  # rl
# elif c_algo == 'pf':
data_pf = [np.array ([1, 1, 1]), np.array ([0.4, 0.78, 1]), np.array ([1, 1, 1])]  # pf
data = [data_rr[0], data_mcqi[0], data_pf[0], data_rl[0], data_rr[1], data_mcqi[1], data_pf[1], data_rl[1], data_rr[2],
        data_mcqi[2], data_pf[2], data_rl[2]]
colors = ['forestgreen', 'firebrick', 'gold', 'royalblue'] * 3
# boxplot
bp1 = axes.boxplot (data, notch=False, widths=0.25, patch_artist=True, manage_ticks=True, showmeans=True, meanline=True,
                    positions=positions)
for patch, color in zip (bp1['boxes'], colors):
    patch.set_facecolor (color)
for line in bp1['means']:
    # get position data for median line
    x, y = line.get_xydata ()[1]  # top of median line
    # overlay median value
    # pyplot.text (x + 0.15, y, '%.2f' % y,
    #              horizontalalignment='center', fontsize=14)  # draw above, centered
# for line in bp1['whiskers']:
#     # get position data for median line
#     x, y = line.get_xydata()[1] # top of median line
#     # overlay median value
#     pyplot.text(x+0.2, y, '%.2f' % y,
#          horizontalalignment='center', fontsize=14) # draw above, centered
rr_patch = mpatches.Patch (color='forestgreen', label='RR')
mcqi_patch = mpatches.Patch (color='firebrick', label='MCQI')
pf_patch = mpatches.Patch (color='gold', label='PF')
a2c_patch = mpatches.Patch (color='royalblue', label='A2C')
axes.legend (handles=[rr_patch, mcqi_patch, pf_patch, a2c_patch], title="Controller Algorithm", fontsize=15,
             title_fontsize=15)
# fig.suptitle('Packet Success Ratio Comparison', fontsize=18)
axes.set_xlabel ('Controller Algorithm', fontsize=18)
axes.set_ylabel ('Packet Reception Ratio', fontsize=18)
filename = parent_dir + "/packets_SLA_ratio_boxplot.png"
#pyplot.grid ()
pyplot.savefig (filename)
pyplot.show ()
# endregion

# # region : reward,slice and score data moving avg
# # get data
# data_rewards = []
# data_slice_scores_rr = []
# data_slice_scores_mcqi = []
# data_slice_scores_pf = []
# for tmp_result in results_list:
#     data_rewards.append(tmp_result.reward_arr)
#     data_slice_scores_rr.append(tmp_result.slice_scores[0] )
#     data_slice_scores_mcqi.append(tmp_result.slice_scores[1] )
#     data_slice_scores_pf.append (tmp_result.slice_scores[2])
# # plot moving average: rewards
# window_size = 10
# pyplot.plot( moving_average(np.array(data_rewards).flatten(), window_size), linestyle='-')
# pyplot.title('Rewards')
# filename = parent_dir + "/rewards.png"
# pyplot.savefig(filename)
# # pyplot.show()
# # plot moving average: slice scores
# pyplot.plot( moving_average(np.array(data_slice_scores_rr).flatten(), window_size), linestyle='-')
# pyplot.plot( moving_average(np.array(data_slice_scores_mcqi).flatten(), window_size), linestyle='-')
# pyplot.plot( moving_average(np.array(data_slice_scores_pf).flatten(), window_size), linestyle='-')
#
# pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
# pyplot.title('Slice Costs')
# filename = parent_dir + "/slice_scores.png"
# pyplot.savefig(filename)
# # pyplot.show()
# # endregion