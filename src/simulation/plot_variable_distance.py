import csv
import os
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data

# plot moving avg
def moving_average(interval, window_size):
    window = np.ones (int (window_size)) / float (window_size)
    return np.convolve (interval, window, 'same')

no_of_slices = 3
no_of_users_list = (10, 10, 10)

# region : Read simulation results
c_algo = 'rl_secondary'
parent_dir = 'baseline comparison data/variable_distance_01/'+c_algo
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]
results_list = []
for tmp_dir in subfolders:
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_list=no_of_users_list))
# endregion

# region : Plotting tp2 of users boxplot
fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(14)
for tick in axes.yaxis.get_major_ticks():
                tick.label.set_fontsize(14)
# get data
data_0 = []  # rr
data_1 = []  # mcqi
data_2 = []  # pf
user_no_cumsum = np.cumsum(no_of_users_list)
for tmp_result in results_list:
    for k in range(len(tmp_result.user_results)):
        tmp_tp2 = tmp_result.user_results[k].sim_avg.tp2
        if k<user_no_cumsum[0]:
            data_0.append (tmp_tp2)
        elif k<user_no_cumsum[1]:
            data_1.append (tmp_tp2)
        else:
            data_2.append (tmp_tp2)
data = [np.array(data_0), np.array(data_1), np.array(data_2)]

bp1 = axes.boxplot(data, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
for line in bp1['means']:
    # get position data for median line
    x, y = line.get_xydata()[1] # top of median line
    # overlay median value
    pyplot.text(x+0.25, y, '%.1f' % y,
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

filename = parent_dir + "/tp_boxplot.png"
pyplot.savefig(filename)
pyplot.close(fig)
pyplot.show()
# endregion

# region : Plotting delay of users boxplot
fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(14)
for tick in axes.yaxis.get_major_ticks():
                tick.label.set_fontsize(14)
# get data
data_0 = []  # rr
data_1 = []  # mcqi
data_2 = []  # pf
user_no_cumsum = np.cumsum(no_of_users_list)
for tmp_result in results_list:
    for k in range(len(tmp_result.user_results)):
        tmp_delay = tmp_result.user_results[k].sim_avg.delay
        if k<user_no_cumsum[0]:
            data_0.append (tmp_delay)
        elif k<user_no_cumsum[1]:
            data_1.append (tmp_delay)
        else:
            data_2.append (tmp_delay)
# filter nan values
data_0 = np.array(data_0)[~np.isnan(np.array(data_0))]
data_1 = np.array(data_1)[~np.isnan(np.array(data_1))]
data_2 = np.array(data_2)[~np.isnan(np.array(data_2))]
data = [np.array(data_0), np.array(data_1), np.array(data_2)]

bp1 = axes.boxplot(data, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
for line in bp1['means']:
    # get position data for median line
    x, y = line.get_xydata()[1] # top of median line
    # overlay median value
    pyplot.text(x+0.25, y, '%.1f' % y,
         horizontalalignment='center', fontsize=14) # draw above, centered
for line in bp1['whiskers']:
    # get position data for median line
    x, y = line.get_xydata()[1] # top of median line
    # overlay median value
    pyplot.text(x+0.3, y, '%.1f' % y,
         horizontalalignment='center', fontsize=14) # draw above, centered
fig.suptitle('Controller Algorithm: ' + c_algo, fontsize=18)
axes.set_xlabel('Slice Scheduler', fontsize=18)
axes.set_ylabel('Delay [ms]', fontsize=18)

filename = parent_dir + "/delay_boxplot.png"
pyplot.savefig(filename)
pyplot.close(fig)
pyplot.show()
# endregion

# # region : Plotting tp2 boxplot  old
# fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
# pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
# for tick in axes.xaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)
# for tick in axes.yaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)
# # get data
# data_rr = []
# data_mcqi = []
# data_pf = []
# for tmp_result in results_list:
#     data_rr.append(list(tmp_result.slice_results[0].round_avg.tp2 ))
#     data_mcqi.append (list(tmp_result.slice_results[1].round_avg.tp2 ))
#     data_pf.append (list(tmp_result.slice_results[2].round_avg.tp2 ))
#
# # axes.plot( np.array(data_rr).flatten(), linestyle='-', marker='o')
# # axes.plot( np.array(data_mcqi).flatten(), linestyle='-', marker='o')
# # axes.plot( np.array(data_pf).flatten(), linestyle='-', marker='o')
#
# data = [np.array(data_rr).flatten() ,np.array(data_mcqi).flatten() ,np.array(data_pf).flatten()  ]
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
# axes.set_ylabel('Throughput [kbps]', fontsize=18)
#
# filename = parent_dir + "/tp_boxplot_old.png"
# pyplot.savefig(filename)
# pyplot.close(fig)
# pyplot.show()
# # endregion

# region : packet_served_SLA/packet_arrived  avg boxplot
fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(14)
for tick in axes.yaxis.get_major_ticks():
                tick.label.set_fontsize(14)
# get data
data_0 = []  # rr
data_1 = []  # mcqi
data_2 = []  # pf
user_no_cumsum = np.cumsum(no_of_users_list)
for tmp_result in results_list:
    for k in range(len(tmp_result.user_results)):
        # tmp_packet_SLA = tmp_result.user_results[k].sim_avg.packets_served_SLA* 100 # Tsim/Tc = 100
        #tmp_packet_SLA_ratio = tmp_result.user_results[k].sim_avg.packets_served_SLA/tmp_result.user_results[k].sim_avg.packets_total
        tmp_packet_SLA_ratio = tmp_result.user_results[k].sim_avg.packets_served_SLA / (tmp_result.user_results[k].sim_avg.packets_served + tmp_result.user_results[k].sim_avg.packets_dropped )

        if k<user_no_cumsum[0]:
            data_0.append (tmp_packet_SLA_ratio)
        elif k<user_no_cumsum[1]:
            data_1.append (tmp_packet_SLA_ratio)
        else:
            data_2.append (tmp_packet_SLA_ratio)
data = [np.array(data_0), np.array(data_1), np.array(data_2)]

# boxplot
bp1 = axes.boxplot(data, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
for line in bp1['means']:
    # get position data for median line
    x, y = line.get_xydata()[1] # top of median line
    # overlay median value
    pyplot.text(x+0.25, y, '%.2f' % y,
         horizontalalignment='center', fontsize=14) # draw above, centered
for line in bp1['whiskers']:
    # get position data for median line
    x, y = line.get_xydata()[1] # top of median line
    # overlay median value
    pyplot.text(x+0.3, y, '%.2f' % y,
         horizontalalignment='center', fontsize=14) # draw above, centered
fig.suptitle('Controller Algorithm: ' + c_algo, fontsize=18)
axes.set_xlabel('Slice Scheduler', fontsize=18)
axes.set_ylabel('Packet SLA_satisfied', fontsize=18)
filename = parent_dir + "/packets_SLA_ratio_boxplot.png"
pyplot.savefig(filename)
pyplot.close(fig)
pyplot.show()
# endregion

# region : reward,slice and score data moving avg
# get data
data_rewards = []
data_slice_scores_rr = []
data_slice_scores_mcqi = []
data_slice_scores_pf = []
for tmp_result in results_list:
    data_rewards.append(tmp_result.reward_arr)
    data_slice_scores_rr.append(tmp_result.slice_scores[0] )
    data_slice_scores_mcqi.append(tmp_result.slice_scores[1] )
    data_slice_scores_pf.append (tmp_result.slice_scores[2])
# plot moving average: rewards
window_size = 10
pyplot.plot( moving_average(np.array(data_rewards).flatten(), window_size), linestyle='-')
pyplot.title('Rewards')
filename = parent_dir + "/rewards.png"
pyplot.savefig(filename)
# pyplot.show()
# plot moving average: slice scores
pyplot.plot( moving_average(np.array(data_slice_scores_rr).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_slice_scores_mcqi).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_slice_scores_pf).flatten(), window_size), linestyle='-')

pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.title('Slice Costs')
filename = parent_dir + "/slice_scores.png"
pyplot.savefig(filename)
# pyplot.show()
# endregion