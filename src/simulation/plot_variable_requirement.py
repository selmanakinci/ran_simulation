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
no_of_users_list = (10, 10, 10)

# region : Read simulation results
parent_dir = "baseline comparison data/variable_requirement_01/rl6_psla"
subfolders = [ f.path for f in os.scandir(parent_dir) if f.is_dir() ]
results_list = []
for i in range(len(subfolders)):
    tmp_dir = subfolders[i]
    results_list.append(read_sim_data(tmp_dir, no_of_slices=3, no_of_users_list=no_of_users_list))
# endregion

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

# region : User tp continuous boxplots
# get tp2 data for users each round
t_custom_avg = 1000  # in ms
data = []
t_group_list = []
s_group_list = []
positions = []
t0 = 0
tmp_pos = 0
for i in range(len(results_list)):
    tmp_result = results_list[i]

    #tmp_user_results = tmp_result.user_results

    # custom_avg each user tp
    for tmp_user_result in tmp_result.user_results:
        tmp_custom_avg_tp = np.mean(tmp_user_result.round_avg.tp2.reshape (-1, int(t_custom_avg/10)), axis=1) # t_custom_avg divided by 10ms(step duration)
        data.extend(tmp_custom_avg_tp)

        # generate t list
        tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
        t_group_list.extend(tmp_t_list)

    # generate s list, append data
    # no_of_users_list = user_list_list[i]
    for j in range(no_of_slices):
        s_group_list.extend(list(np.repeat (j, len(tmp_t_list)*no_of_users_list[j])))

    positions.extend(np.arange(tmp_pos,tmp_pos+no_of_slices*len(tmp_t_list),1))
    tmp_pos+=no_of_slices*len(tmp_t_list)

    t0 += len(tmp_user_result.round_avg.tp2)*10 # increase 1 sim run: 1000 ms

# plot boxplots
#data = np.array([0,1,2,3,4,5,6,7,8,9])
df = pd.DataFrame(data, columns=['Col1'])
df['t'] = pd.Series(t_group_list)
df['S'] = pd.Series(s_group_list)
boxplot = df.boxplot(column=['Col1'], by=['t', 'S'], grid=False, positions=positions, return_type='both', patch_artist = True )

for row_key, (ax,row) in boxplot.iteritems():
    ax.set_xlabel('')
    for i,box in enumerate(row['boxes']):
        if i%no_of_slices==0:
            box.set_facecolor('b')
        if  i%no_of_slices==1:
            box.set_facecolor ('r')
        if  i%no_of_slices==2:
            box.set_facecolor ('g')

pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.title('Boxplot user tp')
filename = parent_dir + "/tp_boxplot_vs_time_users.png"
pyplot.savefig(filename)
pyplot.show()

# endregion

# region : User SLA continuous boxplots different columns
# get SLA data for users each round
t_custom_avg = 1000  # in ms
data_0_1 = np.empty(shape=[10, 0])
data_1_1 = np.empty(shape=[10, 0])
data_2_1 = np.empty(shape=[10, 0])
user_no_cumsum = np.cumsum(no_of_users_list)
for tmp_result in results_list:
    data_0 = []  # rr
    data_1 = []  # mcqi
    data_2 = []  # pf
    for k in range (len (tmp_result.user_results)):
        tmp_packet_SLA = tmp_result.user_results[k].round_avg.packets_served_SLA
        tmp_grouped_served_SLA = np.nansum(tmp_packet_SLA.reshape (-1, int (t_custom_avg / 10)),axis=1)  # t_custom_avg divided by 10ms(step duration)
        tmp_packet_served = tmp_result.user_results[k].round_avg.packets_served
        tmp_grouped_served = np.nansum(tmp_packet_served.reshape (-1, int (t_custom_avg / 10)),axis=1)  # t_custom_avg divided by 10ms(step duration)
        tmp_packets_dropped = tmp_result.user_results[k].round_avg.packets_dropped
        tmp_grouped_dropped = np.nansum(tmp_packets_dropped.reshape (-1, int (t_custom_avg / 10)),axis=1)  # t_custom_avg divided by 10ms(step duration)

        tmp_grouped_SLA_ratio = tmp_grouped_served_SLA / (tmp_grouped_served + tmp_grouped_dropped)
        if k < user_no_cumsum[0]:
            data_0.extend (tmp_grouped_SLA_ratio)
        elif k < user_no_cumsum[1]:
            data_1.append (tmp_grouped_SLA_ratio)
        else:
            data_2.append (tmp_grouped_SLA_ratio)
    data_0_1 = np.concatenate ((data_0_1, np.array(data_0).reshape(-1, int (1000/t_custom_avg))), axis=1)
    data_1_1 = np.concatenate ((data_1_1, np.array(data_1).reshape(-1, int (1000/t_custom_avg))), axis=1)
    data_2_1 = np.concatenate ((data_2_1, np.array(data_2).reshape(-1, int (1000/t_custom_avg))), axis=1)
# filter nan values
#data_0 = np.array(data_0)[~np.isnan(np.array(data_0))]
#data_1 = np.array(data_1)[~np.isnan(np.array(data_1))]
#data_2 = np.array(data_2)[~np.isnan(np.array(data_2))]

# plot boxplots
fig, axes = pyplot.subplots(nrows=3, ncols=1)
bp1 = axes[0].boxplot(data_0_1, notch=False, patch_artist=True, manage_ticks=True, showmeans= True, meanline=True)
bp2 = axes[1].boxplot(data_1_1, notch=False, patch_artist=True, manage_ticks=True, showmeans= True, meanline=True)
bp3 = axes[2].boxplot(data_2_1, notch=False, patch_artist=True, manage_ticks=True, showmeans= True, meanline=True)

#pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
pyplot.suptitle('Boxplot user SLA ratio')
filename = parent_dir + "/SLA_boxplot_vs_time_users.png"
pyplot.savefig(filename)
pyplot.show()

# endregion

# region : User SLA continuous boxplots   not implemented well
# # get SLA data for users each round
# t_custom_avg = 100  # in ms
# data = []
# t_group_list = []
# s_group_list = []
# positions = []
# t0 = 0
# tmp_pos = 0
# for i in range(len(results_list)):
#     tmp_result = results_list[i]
#     #tmp_user_results = tmp_result.user_results
#
#     # custom_avg each user tp
#     for tmp_user_result in tmp_result.user_results:
#         tmp_packet_SLA_ratio = tmp_user_result.round_avg.packets_served_SLA / (tmp_user_result.round_avg.packets_served + tmp_user_result.round_avg.packets_dropped)
#         tmp_custom_avg_SLA_ratio = np.mean(tmp_packet_SLA_ratio.reshape (-1, int(t_custom_avg/10)), axis=1) # t_custom_avg divided by 10ms(step duration)
#         data.extend(tmp_custom_avg_tp)
#         # generate t list
#         tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
#         t_group_list.extend(tmp_t_list)
#     # generate s list, append data
#     # no_of_users_list = user_list_list[i]
#     for j in range(no_of_slices):
#         s_group_list.extend(list(np.repeat(j, len(tmp_t_list)*no_of_users_list[j])))
#     positions.extend(np.arange(tmp_pos, tmp_pos+no_of_slices*len(tmp_t_list), 1))
#     tmp_pos += no_of_slices*len(tmp_t_list)
#     t0 += len(tmp_user_result.round_avg.tp2)*10  # increase 1 sim run: 1000 ms
#
# # plot boxplots
# df = pd.DataFrame(data, columns=['Col1'])
# df['t'] = pd.Series(t_group_list)
# df['S'] = pd.Series(s_group_list)
# boxplot = df.boxplot(column=['Col1'], by=['t', 'S'], grid=False, positions=positions, return_type='both', patch_artist = True )
#
# for row_key, (ax,row) in boxplot.iteritems():
#     ax.set_xlabel('')
#     for i,box in enumerate(row['boxes']):
#         if i%no_of_slices==0:
#             box.set_facecolor('b')
#         if  i%no_of_slices==1:
#             box.set_facecolor ('r')
#         if  i%no_of_slices==2:
#             box.set_facecolor ('g')
#
# pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
# pyplot.title('Boxplot user SLA ratio')
# filename = parent_dir + "/SLA_boxplot_vs_time_users.png"
# pyplot.savefig(filename)
# pyplot.show()
#
# endregion


# # Plotting in different axes boxplots, not implemented!!!
# # region : User tp   ?????
# # get tp2 data for users each round
# t_custom_avg = 1000  # in ms
# # data = []
# data_0 = []
# data_1 = []
# data_2 = []
# t_group_list_0 = []
# t_group_list_1 = []
# t_group_list_2 = []
# s_group_list = []
# positions = []
# t0 = 0
# tmp_pos = 0
# for i in range(len(results_list)):
#     tmp_result = results_list[i]
#
#     # generate s list, append data
#     user_no_cumsum = np.cumsum(user_list_list[i])
#
#     # custom_avg each user tp
#     for k in range(len(tmp_result.user_results)):
#         tmp_user_result = tmp_result.user_results[k]
#         tmp_custom_avg_tp = np.mean(tmp_user_result.round_avg.tp2.reshape (-1, int(t_custom_avg/10)), axis=1) # t_custom_avg divided by 10ms(step duration)
#         if k<user_no_cumsum[0]:
#             data_0.extend (tmp_custom_avg_tp)
#             tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
#             t_group_list_0.extend(tmp_t_list)
#         elif k<user_no_cumsum[1]:
#             data_1.extend (tmp_custom_avg_tp)
#             tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
#             t_group_list_1.extend(tmp_t_list)
#         else:
#             data_2.extend (tmp_custom_avg_tp)
#             tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
#             t_group_list_2.extend(tmp_t_list)
#         #data.extend(tmp_custom_avg_tp)
#         # # generate t list
#         # tmp_t_list = np.arange(t0,t0 + len(tmp_user_result.round_avg.tp2)*10,t_custom_avg )
#         # t_group_list.extend(tmp_t_list)
#
#     # # generate s list, append data
#     # no_of_users_list = user_list_list[i]
#     # for j in range(no_of_slices):
#     #     s_group_list.extend(list(np.repeat (j, len(tmp_t_list)*no_of_users_list[j])))
#     #     positions.append(tmp_pos)
#     #     tmp_pos+=1
#     # tmp_pos += 3
#     t0 += len(tmp_user_result.round_avg.tp2)*10 # increase 1 sim run: 1000 ms
#
#
#
#
#
# fig, axes = pyplot.subplots(nrows=3, ncols=1, figsize=(7,20))
# df['t'] = pd.Series(t_group_list)
# bp1 = axes[0].boxplot(data_0, notch=False, widths=0.20, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=True, showmeans= True, meanline=True)
#
#
#
#
#
#
#
#
# # plot boxplots
# #data = np.array([0,1,2,3,4,5,6,7,8,9])
# df = pd.DataFrame(data, columns=['Col1'])
# df['t'] = pd.Series(t_group_list)
# df['S'] = pd.Series(s_group_list)
# boxplot = df.boxplot(column=['Col1'], by=['t', 'S'], grid=False, positions=positions)  # positions=[0,1,3,4,6,7,9,10,12,13]
#
# pyplot.legend(['RR','MCQI','PF'], title="Slice Manager")
# pyplot.title('Boxplot user tp')
# filename = parent_dir + "/tp_boxplot_vs_time_users.png"
# pyplot.savefig(filename)
# pyplot.show()
#
# # endregion