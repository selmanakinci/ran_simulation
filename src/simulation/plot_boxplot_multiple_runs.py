import csv
import os
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data

no_of_slices=3
# no_of_users_per_slice=10
no_of_users_list = (10, 5, 10)

# Read slice results for plotting comparison
# parent_dir = "baseline comparison data/New folder"
# parent_dir = "baseline comparison data/100 sim run RR"
parent_dir = "baseline comparison data/01/MCQI"
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]

results_list = []
for tmp_dir in subfolders:
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_list=no_of_users_list))


# Plotting results comparison
fig, axes = pyplot.subplots(nrows=1, ncols=1, figsize=(7,20))
pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'RR'])    # Set the ticks and ticklabels for all axes
for tick in axes.xaxis.get_major_ticks():
                tick.label.set_fontsize(14)
for tick in axes.yaxis.get_major_ticks():
                tick.label.set_fontsize(14)
# tp2
data_rr = []
data_mcqi = []
data_pf = []
for tmp_result in results_list:
    data_rr.append([tmp_result.user_results[i].sim_avg.tp2 for i in range(0, no_of_users_list[0])])
    data_mcqi.append ([tmp_result.user_results[i].sim_avg.tp2 for i in range(no_of_users_list[0], no_of_users_list[0]+no_of_users_list[1])])
    data_pf.append ([tmp_result.user_results[i].sim_avg.tp2 for i in range(no_of_users_list[0]+no_of_users_list[1], no_of_users_list[0]+no_of_users_list[1]+no_of_users_list[2])])
data = [np.array(data_rr).flatten() ,np.array(data_mcqi).flatten() ,np.array(data_pf).flatten()  ]
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