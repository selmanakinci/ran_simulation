import csv
import os
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data

no_of_slices=3
no_of_users_per_slice=10

# Read slice results for plotting comparison
parent_dir = "baseline comparison data/New folder (3)"
dir_MCQI = parent_dir + "/MCQI"
dir_PF = parent_dir + "/PF"
dir_RR = parent_dir + "/RR"
dir_RL = parent_dir + "/RL"

result_MCQI = read_sim_data(dir_MCQI, no_of_slices=3, no_of_users_per_slice=10)
result_PF = read_sim_data(dir_PF, no_of_slices=3, no_of_users_per_slice=10)
result_RR = read_sim_data(dir_RR, no_of_slices=3, no_of_users_per_slice=10)
result_RL = read_sim_data(dir_RL, no_of_slices=3, no_of_users_per_slice=10)

parent_dir = "baseline comparison data/New folder (3)"
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]

results_list = []
for tmp_dir in subfolders:
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_per_slice=10))
result_MCQI = results_list[0]
result_PF = results_list[1]
result_RR = results_list[2]
result_RL = results_list[3]

# Plotting results comparison
fig, axes = pyplot.subplots(nrows=3, ncols=3, figsize=(8,20))
pyplot.setp(axes, xticklabels=['RR', 'MCQI', 'PF', 'RL'])    # Set the ticks and ticklabels for all axes
# tp2
data_rr = []
for u in result_RR.user_results: data_rr.append (u.sim_avg.tp2)
data_mcqi = []
for u in result_MCQI.user_results: data_mcqi.append (u.sim_avg.tp2)
data_pf = []
for u in result_PF.user_results: data_pf.append (u.sim_avg.tp2)
data_rl = []
for u in result_RL.user_results: data_rl.append (u.sim_avg.tp2)
data1 = (np.array(data_rr)).reshape(3,no_of_users_per_slice).transpose()
data2 = (np.array(data_mcqi)).reshape(3,no_of_users_per_slice).transpose()
data3 = (np.array(data_pf)).reshape(3,no_of_users_per_slice).transpose()
data4 = (np.array(data_rl)).reshape(3,no_of_users_per_slice).transpose()
bp1 = axes[0,0].boxplot(np.array([data1[:,0],data2[:,0],data3[:,0],data4[:,0]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
bp2 = axes[0,1].boxplot(np.array([data1[:,1],data2[:,1],data3[:,1],data4[:,1]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
bp3 = axes[0,2].boxplot(np.array([data1[:,2],data2[:,2],data3[:,2],data4[:,2]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
# fill with colors
colors = ['slategrey', 'cornflowerblue','ghostwhite', 'midnightblue']
for bplot in (bp1, bp2, bp3):
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
#axes[0].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')


# # delay
# data_rr = []
# for u in result_RR.user_results: data_rr.append (u.sim_avg.delay)
# data_mcqi = []
# for u in result_MCQI.user_results: data_mcqi.append (u.sim_avg.delay)
# data_pf = []
# for u in result_PF.user_results: data_pf.append (u.sim_avg.delay)
# data_rl = []
# for u in result_RL.user_results: data_rl.append (u.sim_avg.delay)
# data1 = (np.array(data_rr)).reshape(3,no_of_users_per_slice).transpose()
# data2 = (np.array(data_mcqi)).reshape(3,no_of_users_per_slice).transpose()
# data3 = (np.array(data_pf)).reshape(3,no_of_users_per_slice).transpose()
# data4 = (np.array(data_rl)).reshape(3,no_of_users_per_slice).transpose()
# bp1 = axes[3].boxplot(data1, positions=x_positions[0], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=False)
# bp2 = axes[3].boxplot(data2, positions=x_positions[1], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="lightsteelblue"), manage_ticks=False)
# bp3 = axes[3].boxplot(data3, positions=x_positions[2], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="cornflowerblue"), manage_ticks=False)
# bp4 = axes[3].boxplot(data4, positions=x_positions[3], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="royalblue"), manage_ticks=False)
# axes[3].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')

# # ql
# data_rr = []
# for u in result_RR.user_results: data_rr.append (u.sim_avg.ql)
# data_mcqi = []
# for u in result_MCQI.user_results: data_mcqi.append (u.sim_avg.ql)
# data_pf = []
# for u in result_PF.user_results: data_pf.append (u.sim_avg.ql)
# data_rl = []
# for u in result_RL.user_results: data_rl.append (u.sim_avg.ql)
# data1 = (np.array(data_rr)).reshape(3,no_of_users_per_slice).transpose()
# data2 = (np.array(data_mcqi)).reshape(3,no_of_users_per_slice).transpose()
# data3 = (np.array(data_pf)).reshape(3,no_of_users_per_slice).transpose()
# data4 = (np.array(data_rl)).reshape(3,no_of_users_per_slice).transpose()
# bp1 = axes[1].boxplot(data1, positions=x_positions[0], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=False)
# bp2 = axes[1].boxplot(data2, positions=x_positions[1], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="lightsteelblue"), manage_ticks=False)
# bp3 = axes[1].boxplot(data3, positions=x_positions[2], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="cornflowerblue"), manage_ticks=False)
# bp4 = axes[1].boxplot(data4, positions=x_positions[3], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="royalblue"), manage_ticks=False)
# axes[1].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')

# CALCULATE JAINS FAIRNESS INDEX
def calculate_Jains_fairness_index(tp_list):
    if len (tp_list) == 0:
        return np.NAN
    data1 = np.array (tp_list[0:no_of_users_per_slice])
    data2 = np.array (tp_list[no_of_users_per_slice:2 * no_of_users_per_slice])
    data3 = np.array (tp_list[2 * no_of_users_per_slice:3 * no_of_users_per_slice])
    J1= pow (np.nansum (data1), 2) / (data1.size * np.nansum (np.square (data1)))
    J2 = pow (np.nansum (data2), 2) / (data2.size * np.nansum (np.square (data2)))
    J3 = pow (np.nansum (data3), 2) / (data3.size * np.nansum (np.square (data3)))
    return [J1, J2, J3]
# Jains Fairness Index
data_rr = []
for u in result_RR.user_results: data_rr.append (u.sim_avg.tp2)
data_mcqi = []
for u in result_MCQI.user_results: data_mcqi.append (u.sim_avg.tp2)
data_pf = []
for u in result_PF.user_results: data_pf.append (u.sim_avg.tp2)
data_rl = []
for u in result_RL.user_results: data_rl.append (u.sim_avg.tp2)
data1 = calculate_Jains_fairness_index(data_rr)
data2 = calculate_Jains_fairness_index(data_mcqi)
data3 = calculate_Jains_fairness_index(data_pf)
data4 = calculate_Jains_fairness_index(data_rl)
p1 = axes[1,0].plot([data1[0],data2[0],data3[0],data4[0]], linestyle='', marker='o')
p2 = axes[1,1].plot([data1[1],data2[1],data3[1],data4[1]], linestyle='', marker='o')
p3 = axes[1,2].plot([data1[2],data2[2],data3[2],data4[2]], linestyle='', marker='o')
#p4 = axes[1].plot(data4, linestyle='-', marker='o')
#axes[1].legend (['RR', 'MCQI', 'PF'])


# bp
data_rr = []
for u in result_RR.user_results: data_rr.append (u.round_avg.bp[-1])  #data_rr.append (u.sim_avg.bp)
data_mcqi = []
for u in result_MCQI.user_results: data_mcqi.append (u.round_avg.bp[-1])
data_pf = []
for u in result_PF.user_results: data_pf.append (u.round_avg.bp[-1])
data_rl = []
for u in result_RL.user_results: data_rl.append (u.round_avg.bp[-1])
data1 = (np.array(data_rr)).reshape(3,no_of_users_per_slice).transpose()
data2 = (np.array(data_mcqi)).reshape(3,no_of_users_per_slice).transpose()
data3 = (np.array(data_pf)).reshape(3,no_of_users_per_slice).transpose()
data4 = (np.array(data_rl)).reshape(3,no_of_users_per_slice).transpose()
bp1 = axes[2,0].boxplot(np.array([data1[:,0],data2[:,0],data3[:,0],data4[:,0]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
bp2 = axes[2,1].boxplot(np.array([data1[:,1],data2[:,1],data3[:,1],data4[:,1]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
bp3 = axes[2,2].boxplot(np.array([data1[:,2],data2[:,2],data3[:,2],data4[:,2]]).transpose(), notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True)
# fill with colors
colors = ['slategrey', 'cornflowerblue','ghostwhite', 'midnightblue']
for bplot in (bp1, bp2, bp3):
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
#axes[2].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')

# fig.suptitle('Scheduling Algorithm Comparison')
#axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
# axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
# axes[1].set_title('Mean Queue Length'), axes[1].set_xlabel('Slice Manager')
# axes[2].set_title('Dropping Probability'), axes[2].set_xlabel('Slice Manager')
#axes[3].set_title('Mean Delay'), axes[3].set_xlabel('Slice Manager')


filename = parent_dir + "/plot_comparison.png"
pyplot.savefig(filename)
pyplot.close(fig)

pyplot.show()