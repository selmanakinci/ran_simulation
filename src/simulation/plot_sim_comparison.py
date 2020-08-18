import csv
import numpy as np
from matplotlib import pyplot

no_of_slices=3
no_of_users_per_slice=2

# Read slice results for plotting comparison
path = "baseline comparison data"


def read_sim_result(filename):
    with open(filename, 'rt')as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'mean_queue_length':
                mean_ql = float(row[1])
            elif row[0] == 'mean_system_time':
                mean_delay = float(row[1])
            elif row[0] == 'mean_throughput':
                mean_tp = float(row[1])
            elif row[0] == 'packets_dropped':
                packets_dropped = float(row[1])
            elif row[0] == 'packets_served':
                packets_served = float(row[1])
            elif row[0] == 'packets_total':
                packets_arrived = float(row[1])
            elif row[0] == 'blocking_probability':
                bp = float(row[1])

    return [mean_ql, mean_tp, mean_delay, bp]

try:
    RR_results = []
    for i in range(no_of_slices):
        RR_results.append(read_sim_result(path + "/C_RR/slice_results/average_results/sim_average_slice%d.csv" %i))  # Controller RR Slice RR
except:
    pass
try:
    MCQI_results = []
    for i in range(no_of_slices):
        MCQI_results.append(read_sim_result(path + "/C_MCQI/slice_results/average_results/sim_average_slice%d.csv" %i))  # Controller MCQI Slice RR
except:
    pass
try:
    PF_results = []
    for i in range(no_of_slices):
        PF_results.append(read_sim_result(path + "/C_PF/slice_results/average_results/sim_average_slice%d.csv" %i))  # Controller PF Slice RR
except:
    pass

# READING USERS throughput to calculate Jain's fairess index
try:
    RR_RR_results = []
    RR_MCQI_results = []
    RR_PF_results = []
    for i in range(no_of_slices):
        if i==0:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                RR_RR_results.append(
                    read_sim_result((path + "/C_RR/user_results/average_results/data/slice%d_user%d_sim_avg_data.csv" % (i, user_id ))))
        if i==1:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                RR_MCQI_results.append(
                    read_sim_result((path + "/C_RR/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id ))))
        if i==2:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                RR_PF_results.append(
                    read_sim_result((path + "/C_RR/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id ))))

except:
    pass
try:
    MCQI_RR_results = []
    MCQI_MCQI_results = []
    MCQI_PF_results = []
    for i in range(no_of_slices):
        if i==0:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                MCQI_RR_results.append(
                    read_sim_result((path + "/C_MCQI/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id ))))
        if i==1:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                MCQI_MCQI_results.append(
                    read_sim_result((path + "/C_MCQI/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id ))))
        if i==2:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                MCQI_PF_results.append(
                    read_sim_result((path + "/C_MCQI/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id ))))
except:
    pass
try:
    PF_RR_results = []
    PF_MCQI_results = []
    PF_PF_results = []
    for i in range(no_of_slices):
        if i == 0:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                PF_RR_results.append(
                    read_sim_result(
                        (path + "/C_PF/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id))))
        if i == 1:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                PF_MCQI_results.append(
                    read_sim_result(
                        (path + "/C_PF/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id))))
        if i == 2:
            for j in range(no_of_users_per_slice):
                user_id = i * no_of_users_per_slice + j
                PF_PF_results.append(
                    read_sim_result(
                        (path + "/C_PF/user_results/average_results/sim_average_slice%d_user%d.csv" % (i, user_id))))

except:
    pass

# CALCULATE JAINS FAIRNESS INDEX
def calculate_Jains_fairness_index(tp_list):
    if len(tp_list)==0:
        return np.NAN
    tp_arr = np.array(tp_list)
    return pow(np.nansum(tp_arr),2) / (tp_arr.size * np.nansum(np.square(tp_arr)))

# find tp of results and calculate index
if len(RR_results)!=0:
    tp_temp = []
    for i in RR_RR_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_RR_RR = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in RR_PF_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_RR_PF = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in RR_MCQI_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_RR_MCQI = calculate_Jains_fairness_index(tp_temp)
if len(MCQI_results) != 0:
    tp_temp = []
    for i in MCQI_RR_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_MCQI_RR = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in MCQI_PF_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_MCQI_PF = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in MCQI_MCQI_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_MCQI_MCQI = calculate_Jains_fairness_index(tp_temp)
if len(PF_results) != 0:
    tp_temp = []
    for i in PF_RR_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_PF_RR = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in PF_PF_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_PF_PF = calculate_Jains_fairness_index(tp_temp)
    tp_temp = []
    for i in PF_MCQI_results: tp_temp.append(i[1])    # indexing i.[1] refers to tp
    J_PF_MCQI = calculate_Jains_fairness_index(tp_temp)

# Plotting RR results comparison

fig, axes = pyplot.subplots(nrows=4, ncols=1, figsize=(8, 20))
pyplot.setp(axes, xticks=[0, 1, 2], xticklabels=['RR', 'MCQI', 'PF'])    # Set the ticks and ticklabels for all axes
if len(RR_results)!=0:
    data_temp = []
    for i in RR_results: data_temp.append(i[0])    # indexing i.[0] refers to mean ql
    axes[0].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in RR_results: data_temp.append(i[1])    # indexing i.[1] refers to mean tp
    axes[1].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in RR_results: data_temp.append(i[2])    # indexing i.[2] refers to mean delay
    axes[2].plot( data_temp, linestyle='-', marker='o')
    data_temp = [J_RR_RR, J_RR_MCQI, J_RR_PF]
    axes[3].plot( data_temp, linestyle='-', marker='o')
if len(MCQI_results) != 0:
    data_temp = []
    for i in MCQI_results: data_temp.append(i[0])    # indexing i.[0] refers to mean ql
    axes[0].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in MCQI_results: data_temp.append(i[1])    # indexing i.[1] refers to mean tp
    axes[1].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in MCQI_results: data_temp.append(i[2])    # indexing i.[2] refers to mean delay
    axes[2].plot( data_temp, linestyle='-', marker='o')
    data_temp = [J_MCQI_RR, J_MCQI_MCQI, J_MCQI_PF]
    axes[3].plot( data_temp, linestyle='-', marker='o')
if len(PF_results) != 0:
    data_temp = []
    for i in PF_results: data_temp.append(i[0])    # indexing i.[0] refers to mean ql
    axes[0].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in PF_results: data_temp.append(i[1])    # indexing i.[1] refers to mean tp
    axes[1].plot( data_temp, linestyle='-', marker='o')
    data_temp = []
    for i in PF_results: data_temp.append(i[2])    # indexing i.[2] refers to mean delay
    axes[2].plot( data_temp, linestyle='-', marker='o')
    data_temp = [J_PF_RR, J_PF_MCQI, J_PF_PF]
    axes[3].plot( data_temp, linestyle='-', marker='o')

fig.suptitle('Scheduling Algorithm Comparison')
axes[0].set_title('mean_queue_length'), axes[0].legend(['RR','MCQI','PF'], title="Controller"), axes[0].set_xlabel('Slice Manager')
axes[1].set_title('mean_throughput'), axes[1].legend(['RR','MCQI','PF'], title="Controller"), axes[1].set_xlabel('Slice Manager')
axes[2].set_title('mean_delay'), axes[2].legend(['RR','MCQI','PF'], title="Controller"), axes[2].set_xlabel('Slice Manager')
axes[3].set_title('Jain''s Index'), axes[3].legend(['RR','MCQI','PF'], title="Controller"), axes[3].set_xlabel('Slice Manager')

filename = path + "/plot_comparison.png"
pyplot.savefig(filename)
pyplot.close(fig)


pyplot.show()




