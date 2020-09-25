import csv
import os
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data

no_of_slices=3
user_list_list = []
for i in range(6):      # no or runs and user list conditions
    if i < 2:          user_list_list.append((5, 5, 5))
    elif i < 4:        user_list_list.append((10, 5, 5))
    else:              user_list_list.append ((5, 5, 5))

# Read slice results for plotting comparison
parent_dir = "baseline comparison data/user_no_adaptation_S4_01/rl_02"
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]

results_list = []
for i in range(len(subfolders)):
    no_of_users_list=user_list_list[i]
    tmp_dir = subfolders[i]
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_list=no_of_users_list))


# Plotting results comparison
fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(50,10))
#pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'RR'])    # Set the ticks and ticklabels for all axes
for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(14)
for tick in axes.yaxis.get_major_ticks():
                tick.label.set_fontsize(14)
# tp2
data_rr = []
data_mcqi = []
data_pf = []
for tmp_result in results_list:
    data_rr.append(list(tmp_result.slice_results[0].round_avg.tp2 ))
    data_mcqi.append (list(tmp_result.slice_results[1].round_avg.tp2 ))
    data_pf.append (list(tmp_result.slice_results[2].round_avg.tp2 ))

# # region : plot moving avg
def moving_average(interval, window_size):
    window = np.ones (int (window_size)) / float (window_size)
    return np.convolve (interval, window, 'same')

window_size = 10
axes.plot( moving_average(np.array(data_rr).flatten(), window_size), linestyle='-', marker='o')
axes.plot( moving_average(np.array(data_mcqi).flatten(), window_size), linestyle='-', marker='o')
axes.plot( moving_average(np.array(data_pf).flatten(), window_size), linestyle='-', marker='o')
axes.legend(['RR','MCQI','PF'], title="Controller")
# # endregion
# region : plot cumsum
# axes.plot( np.array(data_rr).flatten().cumsum(), linestyle='-')
# axes.plot( np.array(data_mcqi).flatten().cumsum(), linestyle='-')
# axes.plot( np.array(data_pf).flatten().cumsum(), linestyle='-')
# axes.legend(['RR','MCQI','PF'], title="Controller")
# endregion

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
fig.suptitle('Controller Algorithm: RL', fontsize=18)
axes.set_xlabel('Slice Scheduler', fontsize=18)
axes.set_ylabel('Throughput [kbps]', fontsize=18)
#axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
# axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
# axes[1].set_title('Mean Queue Length'), axes[1].set_xlabel('Slice Manager')
# axes[2].set_title('Dropping Probability'), axes[2].set_xlabel('Slice Manager')
#axes[3].set_title('Mean Delay'), axes[3].set_xlabel('Slice Manager')


filename = parent_dir + "/plot_comparison.png"
pyplot.savefig(filename)
pyplot.close(fig)

pyplot.show()