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

no_of_slices=3
user_list_list = []
for i in range(6):      # no or runs and user list conditions
    if i < 2:          user_list_list.append((5, 5, 5))
    elif i < 4:        user_list_list.append((10, 5, 5))
    else:              user_list_list.append ((5, 5, 5))

# region : Read simulation results
parent_dir = "baseline comparison data/user_no_adaptation_S4_01/rl_highreq"
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]

results_list = []
for i in range(len(subfolders)):
    no_of_users_list=user_list_list[i]
    tmp_dir = subfolders[i]
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_list=no_of_users_list))
# endregion


# Plotting results comparison
#fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
#pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'RR'])    # Set the ticks and ticklabels for all axes
# for tick in axes.xaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)
# for tick in axes.yaxis.get_major_ticks():
#                 tick.label.set_fontsize(14)

# region : reward,slice and score data
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
pyplot.show()
# plot moving average: slice scores
pyplot.plot( moving_average(np.array(data_slice_scores_rr).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_slice_scores_mcqi).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_slice_scores_pf).flatten(), window_size), linestyle='-')

pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.title('Slice Costs')
filename = parent_dir + "/slice_scores.png"
pyplot.savefig(filename)
pyplot.show()
# endregion


# region : tp
# get tp2 data for slices each round
data_rr = []
data_mcqi = []
data_pf = []
for tmp_result in results_list:
    data_rr.append (list (tmp_result.slice_results[0].round_avg.tp2))
    data_mcqi.append (list (tmp_result.slice_results[1].round_avg.tp2))
    data_pf.append (list (tmp_result.slice_results[2].round_avg.tp2))

# plot moving average: tp
window_size = 10
pyplot.plot( moving_average(np.array(data_rr).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_mcqi).flatten(), window_size), linestyle='-')
pyplot.plot( moving_average(np.array(data_pf).flatten(), window_size), linestyle='-')

pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.title('Mov Avg Slice tp')
filename = parent_dir + "/tp_mov_avg.png"
pyplot.savefig(filename)
pyplot.show()

# plot cumsum: tp
pyplot.plot( np.array(data_rr).flatten().cumsum(), linestyle='-')
pyplot.plot( np.array(data_mcqi).flatten().cumsum(), linestyle='-')
pyplot.plot( np.array(data_pf).flatten().cumsum(), linestyle='-')

pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.title('Cumulative Slice tp')
filename = parent_dir + "/tp_cumsum.png"
pyplot.savefig(filename)
pyplot.show()

# endregion