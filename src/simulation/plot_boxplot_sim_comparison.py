import csv
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon

no_of_slices=3
no_of_users_per_slice=10

# Read slice results for plotting comparison
parent_dir = "baseline comparison data/New folder"
dir_MCQI = parent_dir + "/MCQI"
dir_PF = parent_dir + "/PF"
dir_RR = parent_dir + "/RR"
dir_RL = parent_dir + "/RL"

def read_sim_data(parent_dir):
    class SimAvgResult(object):
        def __init__(self):
            self.tp = None
            self.tp2 = None
            self.ql = None
            self.delay = None
            self.packets_total = None
            self.packets_served = None
            self.packets_dropped = None
            self.bp = None

    class SliceResult(object):
        def __init__(self):
            self.round_avg = None
            self.sim_avg = None

        def get_sim_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()[0]
            tmp.delay = df.loc['mean_system_time'].to_numpy ()[0]
            tmp.tp = df.loc['mean_rate'].to_numpy ()[0]
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()[0]
            tmp.packets_total = df.loc['packets_total'].to_numpy ()[0]
            tmp.packets_served = df.loc['packets_served'].to_numpy ()[0]
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()[0]
            tmp.bp = df.loc['blocking_probability'].to_numpy ()[0]
            self.sim_avg = tmp

    class UserResult(object):
        def __init__(self):
            self.tp = None
            self.tp2 = None
            self.ql = None
            self.delay = None
            self.round_avg = None
            self.sim_avg = None

        def get_sim_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()[0]
            tmp.delay = df.loc['mean_system_time'].to_numpy ()[0]
            tmp.tp = df.loc['mean_rate'].to_numpy ()[0]
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()[0]
            tmp.packets_total = df.loc['packets_total'].to_numpy ()[0]
            tmp.packets_served = df.loc['packets_served'].to_numpy ()[0]
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()[0]
            tmp.bp = df.loc['blocking_probability'].to_numpy ()[0]
            self.sim_avg = tmp

        def get_round_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()
            tmp.delay = df.loc['mean_system_time'].to_numpy ()
            tmp.tp = df.loc['mean_rate'].to_numpy ()
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()
            tmp.packets_total = df.loc['packets_total'].to_numpy ()
            tmp.packets_served = df.loc['packets_served'].to_numpy ()
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()
            tmp.bp = df.loc['blocking_probability'].to_numpy ()
            self.round_avg = tmp

    class SimResult(object):
        def __init__(self):
            self.controller = None
            self.sm = []
            self.user_results = [UserResult()] * no_of_slices * no_of_users_per_slice
            self.slice_results = [SliceResult()] * no_of_slices

        def add_sm_data(self, sm_data):
            self.sm.append(sm_data)

    result = SimResult()

    # Controller
    path = parent_dir + "/controller/"
    filename = path + "data/rb_allocation.csv"
    result.controller = pd.read_csv(filename)

    # SLICE MANAGER
    path = parent_dir + "/sm/"
    for i in range(no_of_slices):
        filename = path + "data/slice%d_rb_allocation.csv" % i
        result.add_sm_data(sm_data=pd.read_csv(filename))

    # Server(user) Results
    path = parent_dir + "/user_results"
    for j in range(no_of_slices):
        for k in range(no_of_users_per_slice):
            tmp_user_result = UserResult()
            user_id = j * no_of_users_per_slice + k

            # tp
            filename = path + "/tp" + "/slice%d_user%d_tp_data.csv" % (j, user_id)
            tmp_user_result.tp = pd.read_csv (filename, header=None, index_col=0)

            # tp2
            filename = path + "/tp2" + "/slice%d_user%d_tp2_data.csv" % (j, user_id)
            tmp_user_result.tp2 = pd.read_csv (filename, header=None, index_col=0)

            # ql
            filename = path + "/ql" + "/slice%d_user%d_ql_data.csv" % (j, user_id)
            tmp_user_result.ql = pd.read_csv (filename, header=None, index_col=0)

            # syst (delay)
            filename = path + "/delay" + "/slice%d_user%d_delay_data.csv" % (j, user_id)
            tmp_user_result.delay = pd.read_csv (filename, header=None, index_col=0)

            # round average results
            filename = path + "/average_results/data" + "/slice%d_user%d_avg_data.csv" % (j, user_id)
            tmp_user_result.get_round_avg (pd.read_csv (filename, header=0, index_col=0))

            # sim average results
            filename = path + "/average_results/data" + "/slice%d_user%d_sim_avg_data.csv" % (j, user_id)
            tmp_user_result.get_sim_avg(pd.read_csv (filename, header=0, index_col=0))

            # assign tmp user result
            result.user_results[user_id] = tmp_user_result

    # Slice Results
    path = parent_dir + "/slice_results/average_results/data"
    for j in range(no_of_slices):
        try:
            filename = path + "/slice%d_sim_avg_data.csv" % j
            tmp_slice_result = SliceResult()
            tmp_slice_result.get_sim_avg(pd.read_csv(filename, header=0, index_col=0))
            result.slice_results[j] = tmp_slice_result

        except:
            print ("ERROR: in reading average results for slice %d " % j)

    return result

result_MCQI = read_sim_data(dir_MCQI)
result_PF = read_sim_data(dir_PF)
result_RR = read_sim_data(dir_RR)
result_RL = read_sim_data(dir_RL)

# Plotting results comparison
fig, axes = pyplot.subplots(nrows=3, ncols=1, figsize=(8,20))
d1 = 3
d2 = 0.25
x_positions = [np.arange(3) * d1 - 3*d2, np.arange(3) * d1 - d2, np.arange(3) * d1 + d2, np.arange(3) * d1 + 3*d2]
label_positions = [0, d1, 2*d1]
pyplot.setp(axes, xticks=label_positions, xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
# # tp
# data_rr = []
# for u in result_RR.user_results: data_rr.append (u.sim_avg.tp)
# data_mcqi = []
# for u in result_MCQI.user_results: data_mcqi.append (u.sim_avg.tp)
# data_pf = []
# for u in result_PF.user_results: data_pf.append (u.sim_avg.tp)
# data_rl = []
# for u in result_RL.user_results: data_rl.append (u.sim_avg.tp)
# data1 = (np.array(data_rr)).reshape(3,no_of_users_per_slice).transpose()
# data2 = (np.array(data_mcqi)).reshape(3,no_of_users_per_slice).transpose()
# data3 = (np.array(data_pf)).reshape(3,no_of_users_per_slice).transpose()
# data4 = (np.array(data_rl)).reshape(3,no_of_users_per_slice).transpose()
# bp1 = axes[0].boxplot(data1, positions=x_positions[0], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=False)
# bp2 = axes[0].boxplot(data2, positions=x_positions[1], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="lightsteelblue"), manage_ticks=False)
# bp3 = axes[0].boxplot(data3, positions=x_positions[2], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="cornflowerblue"), manage_ticks=False)
# bp4 = axes[0].boxplot(data4, positions=x_positions[3], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="royalblue"), manage_ticks=False)
# axes[0].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')

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
bp1 = axes[0].boxplot(data1, positions=x_positions[0], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=False)
bp2 = axes[0].boxplot(data2, positions=x_positions[1], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="lightsteelblue"), manage_ticks=False)
bp3 = axes[0].boxplot(data3, positions=x_positions[2], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="cornflowerblue"), manage_ticks=False)
bp4 = axes[0].boxplot(data4, positions=x_positions[3], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="royalblue"), manage_ticks=False)
axes[0].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')


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
p1 = axes[1].plot(data1, linestyle='', marker='o')
p2 = axes[1].plot(data2, linestyle='', marker='o')
p3 = axes[1].plot(data3, linestyle='', marker='o')
#p4 = axes[1].plot(data4, linestyle='-', marker='o')
axes[1].legend (['RR', 'MCQI', 'PF'])


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
bp1 = axes[2].boxplot(data1, positions=x_positions[0], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="slategrey"), manage_ticks=False)
bp2 = axes[2].boxplot(data2, positions=x_positions[1], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="lightsteelblue"), manage_ticks=False)
bp3 = axes[2].boxplot(data3, positions=x_positions[2], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="cornflowerblue"), manage_ticks=False)
bp4 = axes[2].boxplot(data4, positions=x_positions[3], notch=False, widths=0.35, patch_artist=True, boxprops=dict(facecolor="royalblue"), manage_ticks=False)
axes[2].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0], bp4["boxes"][0]], ['RR', 'MCQI', 'PF', 'RL'], loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize='small', title="Controller", title_fontsize='small')

# fig.suptitle('Scheduling Algorithm Comparison')
#axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
axes[0].set_title('Mean Throughput'), axes[0].set_xlabel('Slice Manager')
axes[1].set_title('Mean Queue Length'), axes[1].set_xlabel('Slice Manager')
axes[2].set_title('Dropping Probability'), axes[2].set_xlabel('Slice Manager')
#axes[3].set_title('Mean Delay'), axes[3].set_xlabel('Slice Manager')


filename = parent_dir + "/plot_comparison.png"
pyplot.savefig(filename)
pyplot.close(fig)

pyplot.show()