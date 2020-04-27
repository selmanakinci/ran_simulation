from matplotlib import pyplot
import matplotlib.patches as mpatches
import numpy as np
from countercollection import CounterCollection
from server import Server
import os
import re
import csv
from statistics import mean
from simparam import SimParam


def plot_results(parent_dir, no_of_slices=2, no_of_users_per_slice=2, sim_param=SimParam(), slices = []):

    # choose plots
    plot_controller = True
    plot_slice_manager = True
    plot_user_results = False
    plot_user_results_avg = False
    plot_slice_results = False
    export_sim_avg = True
    export_user_avg = True

    # parameters
    t_c = sim_param.T_C
    t_sm = sim_param.T_SM
    t_final = sim_param.T_FINAL

    # Controller
    if plot_controller:
        path = parent_dir + "/controller/data"
        for i in range(int(t_final/t_c)):
            t_tmp = i*t_c

            # plotting RB mapping
            fig, axes = pyplot.subplots(1, no_of_slices, figsize=(12, 3))
            if no_of_slices == 1:
                filename = path + "/RB_list_t_%d_slice_%d.csv" % (t_tmp, 0)
                data = np.loadtxt(filename, delimiter=',')
                if len(data.shape) == 1:
                    data = np.expand_dims(data, axis=0)
                axes.imshow(data, aspect='auto')
            else:
                for j in range(no_of_slices):
                    filename = path + "/RB_list_t_%d_slice_%d.csv" % (t_tmp, j)
                    data = np.loadtxt(filename, delimiter=',')
                    if len(data.shape) == 1:
                        data = np.expand_dims(data, axis=0)
                    axes[j].imshow(data, aspect='auto')

            filename = parent_dir + "/controller/plot_t_%d.png" % t_tmp
            pyplot.savefig(filename)
            pyplot.close(fig)

    # SLICE MANAGER
    # plotting RB matching
    if plot_slice_manager:
        path = parent_dir + "/sm/data/"
        for i in range(int(t_final/t_c)):
            t_tmp = i*t_c
            t_arr = np.arange(t_tmp,t_tmp+t_c,t_sm)
            for j in range(no_of_slices):
                data_list = []
                for t in t_arr:
                    filename = path + "RB_matching_t_%d_slice_%d.csv" % (t, j)
                    data = np.loadtxt(filename, delimiter=',')
                    data_list.append(data)
                if len(data_list[0].shape)>1:
                    RB_matching_sm = np.concatenate(data_list, axis=1)
                else:
                    RB_matching_sm = data_list
                if not np.isnan(RB_matching_sm).all():
                    fig = pyplot.figure(figsize=(12, 3))
                    im = pyplot.imshow(RB_matching_sm, aspect='auto')
                    if no_of_users_per_slice != 1:
                        colors = [im.cmap(float(value/(no_of_users_per_slice-1))) for value in range(no_of_users_per_slice)]  # get the colors of the values, according to the colormap used by imshow
                        patches = [mpatches.Patch(color=colors[k], label="User id {l}".format(l=k)) for k in
                                   range(no_of_users_per_slice)]  # create a patch (proxy artist) for every color

                    else:
                        colors = im.cmap(0.)
                        patches = [mpatches.Patch( label="User id {l}".format(l=k)) for k in
                                   range(no_of_users_per_slice)]  # create a patch (proxy artist) for every color

                    pyplot.legend(handles=patches, bbox_to_anchor=(1.005, 1), loc=2, borderaxespad=0.)  # put those patched as legend-handles into the legend
                    filename = parent_dir + "/sm/plot_t_%d_slice_%d.png" % (t_tmp,j)
                    pyplot.savefig(filename)
                    pyplot.close(fig)
                else:
                    print("ERROR: Slice Manager Plotting: t_%d_slice_%d is empty. " % (t_tmp,j))


    # Server Results
    pseudo_server = Server(0,0,0)
    tmp_counter_collection = CounterCollection(pseudo_server)
    if plot_user_results:
        path = parent_dir + "/user_results"
        for j in range(no_of_slices):
            for k in range(no_of_users_per_slice):
                user_id = j*no_of_users_per_slice + k
                # tp
                filename = path + "/tp" + "/slice%d_user%d_sum_power_two.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp.sum_power_two = np.loadtxt(filename, delimiter=',')
                filename = path + "/tp" + "/slice%d_user%d_values.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp.values = np.loadtxt(filename, delimiter=',')
                filename = path + "/tp" + "/slice%d_user%d_timestamps.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp.timestamps = np.loadtxt(filename, delimiter=',')
                plotname = path + "/tp" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_tp.timestamps.size ==0:
                    print("Warning: Throughput data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_tp.plot(plotname, one_round=False)


                # tp2
                filename = path + "/tp2" + "/slice%d_user%d_sum_power_two.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp2.sum_power_two = np.loadtxt(filename, delimiter=',')
                filename = path + "/tp2" + "/slice%d_user%d_values.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp2.values = np.loadtxt(filename, delimiter=',')
                filename = path + "/tp2" + "/slice%d_user%d_timestamps.csv" % (j, user_id)
                tmp_counter_collection.cnt_tp2.timestamps = np.loadtxt(filename, delimiter=',')
                plotname = path + "/tp2" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_tp2.timestamps.size ==0:
                    print("Warning: Throughput data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_tp2.plot(plotname, one_round=False)

                # ql
                filename = path + "/ql" + "/slice%d_user%d_sum_power_two.csv" % (j, user_id)
                tmp_counter_collection.cnt_ql.sum_power_two = np.loadtxt(filename, delimiter=',')
                filename = path + "/ql" + "/slice%d_user%d_values.csv" % (j, user_id)
                tmp_counter_collection.cnt_ql.values = np.loadtxt(filename, delimiter=',')
                filename = path + "/ql" + "/slice%d_user%d_timestamps.csv" % (j, user_id)
                tmp_counter_collection.cnt_ql.timestamps = np.loadtxt(filename, delimiter=',')
                plotname = path + "/ql" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_ql.timestamps.size ==0:
                    print("Warning: Queue length data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_ql.plot(plotname, one_round=False)

                # syst (delay)
                filename = path + "/delay" + "/slice%d_user%d_values.csv" % (j, user_id)
                tmp_counter_collection.cnt_syst.values = np.loadtxt(filename, delimiter=',')
                filename = path + "/delay" + "/slice%d_user%d_timestamps.csv" % (j, user_id)
                tmp_counter_collection.cnt_syst.timestamps = np.loadtxt(filename, delimiter=',')
                plotname = path + "/delay" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_syst.timestamps.size == 0:
                    print("Warning: System Time for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_syst.plot(plotname, one_round=False)


    # use below to plot average results
    ####### average results can be plotted by batching normal results(histogram)
    if plot_user_results_avg:
        path = parent_dir + "/user_results/average_results/data"
        #for i in range(int(t_final/t_c)):
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        for j in range(no_of_slices):
            for k in range(no_of_users_per_slice):
                user_id = j * no_of_users_per_slice + k
                tmp_mean_queue_length = []
                tmp_mean_system_time = []
                tmp_mean_throughput = []
                tmp_packets_dropped = []
                tmp_packets_served = []
                tmp_packets_total = []
                tmp_blocking_probability = []
                for t in t_arr:
                    filename = path + "/%d_slice%d_user%d_average_values.csv" % (t, j, user_id)
                    with open(filename, 'rt')as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[0] == 'mean_queue_length': tmp_mean_queue_length.append(round(float(row[1]),2))
                            elif row[0] == 'mean_system_time': tmp_mean_system_time.append(round(float(row[1]),2))
                            elif row[0] == 'mean_throughput': tmp_mean_throughput.append(round(float(row[1]),2))
                            elif row[0] == 'packets_dropped': tmp_packets_dropped.append(round(float(row[1]),2))
                            elif row[0] == 'packets_served': tmp_packets_served.append(round(float(row[1]),2))
                            elif row[0] == 'packets_total': tmp_packets_total.append(round(float(row[1]),2))
                            elif row[0] == 'blocking_probability': tmp_blocking_probability.append(round(float(row[1]),2))

                fig, axes = pyplot.subplots(4, 2, figsize=(12, 20))
                tmp_data = tmp_mean_queue_length
                tmp_plot = axes[0, 0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [mean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_mean_system_time
                tmp_plot = axes[1, 0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center', transform=tmp_plot.transAxes)
                tmp_data = tmp_mean_throughput
                tmp_plot = axes[2, 0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), np.nanmean(tmp_data) * 1.001, 'mean:%.2f' % (np.nanmean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_total
                tmp_plot = axes[0, 1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_served
                tmp_plot = axes[1, 1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_dropped
                tmp_plot = axes[2, 1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_blocking_probability
                tmp_plot = axes[3, 1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)

                # without mean version
                # axes[0,0].plot(t_arr, tmp_mean_queue_length, linestyle='-', marker='o')
                # axes[1,0].plot(t_arr, tmp_mean_system_time, linestyle='-', marker='o')
                # axes[2,0].plot(t_arr, tmp_mean_throughput, linestyle='-', marker='o')
                # axes[0,1].plot(t_arr, tmp_packets_total, linestyle='-', marker='o')
                # axes[1,1].plot(t_arr, tmp_packets_served, linestyle='-', marker='o')
                # axes[2,1].plot(t_arr, tmp_packets_dropped, linestyle='-', marker='o')
                # axes[3,1].plot(t_arr, tmp_blocking_probability, linestyle='-', marker='o')

                fig.suptitle('User Results')
                axes[0,0].set_ylabel('mean_queue_length')
                axes[1,0].set_ylabel('mean_system_time')
                axes[2,0].set_ylabel('mean_throughput')
                axes[0,1].set_ylabel('packets_total')
                axes[1,1].set_ylabel('packets_served')
                axes[2,1].set_ylabel('packets_dropped')
                axes[3,1].set_ylabel('blocking_probability')
                axes[3,1].set_xlabel('time')
                axes[0,0].set_xlabel('time')
                filename = parent_dir + "/user_results/average_results/plot_slice%d_user%d_average_values.png" % (j, user_id)
                pyplot.savefig(filename)
                pyplot.close(fig)


    # export simulation average results for each user
    if export_user_avg:
        path = parent_dir + "/user_results/average_results/data"
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        for j in range(no_of_slices):
            for k in range(no_of_users_per_slice):
                try:
                    user_id = j * no_of_users_per_slice + k
                    tmp_mean_queue_length = []
                    tmp_mean_system_time = []
                    tmp_mean_throughput = []
                    tmp_packets_dropped = []
                    tmp_packets_served = []
                    tmp_packets_total = []
                    tmp_blocking_probability = []
                    for t in t_arr:
                        filename = path + "/%d_slice%d_user%d_average_values.csv" % (t, j, user_id)
                        with open(filename, 'rt')as f:
                            reader = csv.reader(f)
                            for row in reader:
                                if row[0] == 'mean_queue_length': tmp_mean_queue_length.append(round(float(row[1]),2))
                                elif row[0] == 'mean_system_time': tmp_mean_system_time.append(round(float(row[1]),2))
                                elif row[0] == 'mean_throughput': tmp_mean_throughput.append(round(float(row[1]),2))
                                elif row[0] == 'packets_dropped': tmp_packets_dropped.append(round(float(row[1]),2))
                                elif row[0] == 'packets_served': tmp_packets_served.append(round(float(row[1]),2))
                                elif row[0] == 'packets_total': tmp_packets_total.append(round(float(row[1]),2))
                                elif row[0] == 'blocking_probability': tmp_blocking_probability.append(round(float(row[1]),2))

                    #  Storing average data
                    row_list = [["mean_queue_length", np.nanmean(tmp_mean_queue_length)],
                                ["mean_system_time", np.nanmean(tmp_mean_system_time)],
                                ["mean_throughput", np.nanmean(tmp_mean_throughput)],
                                ["packets_dropped", np.nanmean(tmp_packets_dropped)],
                                ["packets_served", np.nanmean(tmp_packets_served)],
                                ["packets_total", np.nanmean(tmp_packets_total)],
                                ["blocking_probability", np.nanmean(tmp_blocking_probability)]]
                    filename = parent_dir + "/user_results/average_results/sim_average_slice%d_user%d.csv" % (j, user_id)
                    with open(filename, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerows(row_list)

                    print("slice%d user%d  tp: %d" % (j, user_id, np.nanmean(tmp_mean_throughput) ))

                except:
                    print("ERROR: in exporting average results for slice %d user %d " % (j, user_id))


    # plot average slice results
    if plot_slice_results:
        path = parent_dir + "/slice_results/average_results/data"
        #for i in range(int(t_final/t_c)):
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        for j in range(no_of_slices):
            try:

                tmp_mean_queue_length = []
                tmp_mean_system_time = []
                tmp_mean_throughput = []
                tmp_packets_dropped = []
                tmp_packets_served = []
                tmp_packets_total = []
                tmp_blocking_probability = []
                for t in t_arr:
                    filename = path + "/%d_slice%d_average_values.csv" % (t, j)
                    with open(filename, 'rt')as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[0] == 'mean_queue_length': tmp_mean_queue_length.append(round(float(row[1]),2))
                            elif row[0] == 'mean_system_time': tmp_mean_system_time.append(round(float(row[1]),2))
                            elif row[0] == 'mean_throughput': tmp_mean_throughput.append(round(float(row[1]),2))
                            elif row[0] == 'packets_dropped': tmp_packets_dropped.append(round(float(row[1]),2))
                            elif row[0] == 'packets_served': tmp_packets_served.append(round(float(row[1]),2))
                            elif row[0] == 'packets_total': tmp_packets_total.append(round(float(row[1]),2))
                            elif row[0] == 'blocking_probability': tmp_blocking_probability.append(round(float(row[1]),2))


                fig, axes = pyplot.subplots(4, 2, figsize=(12, 20))
                tmp_data = tmp_mean_queue_length
                tmp_plot = axes[0,0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_mean_system_time
                tmp_plot = axes[1,0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_mean_throughput
                tmp_plot = axes[2,0]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), np.nanmean(tmp_data)*1.001, 'mean:%.2f' % (np.nanmean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_total
                tmp_plot = axes[0,1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_served
                tmp_plot = axes[1,1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_packets_dropped
                tmp_plot = axes[2,1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [np.nanmean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)
                tmp_data = tmp_blocking_probability
                tmp_plot = axes[3,1]
                tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                tmp_plot.plot(t_arr, [mean(tmp_data)]*len(tmp_data), linestyle='--', color='r')
                #tmp_plot.text(t_arr.min(), mean(tmp_data)*1.001, 'mean:%.2f' % (mean(tmp_data)))
                tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                              transform=tmp_plot.transAxes)

                # without mean version
                #axes[1,0].plot(t_arr, tmp_mean_system_time, linestyle='-', marker='o')
                #axes[2,0].plot(t_arr, tmp_mean_throughput, linestyle='-', marker='o')
                #axes[0,1].plot(t_arr, tmp_packets_total, linestyle='-', marker='o')
                #axes[1,1].plot(t_arr, tmp_packets_served, linestyle='-', marker='o')
                #axes[2,1].plot(t_arr, tmp_packets_dropped, linestyle='-', marker='o')
                #axes[3,1].plot(t_arr, tmp_blocking_probability, linestyle='-', marker='o')

                fig.suptitle('Slice Results for Controller: %s  Slice Manager: %s' % (sim_param.C_ALGO, slices[j].slice_param.SM_ALGO))
                axes[0,0].set_ylabel('mean_queue_length')
                axes[1,0].set_ylabel('mean_system_time')
                axes[2,0].set_ylabel('mean_throughput')
                axes[0,1].set_ylabel('packets_total')
                axes[1,1].set_ylabel('packets_served')
                axes[2,1].set_ylabel('packets_dropped')
                axes[3,1].set_ylabel('blocking_probability')
                axes[3,1].set_xlabel('time')
                axes[0,0].set_xlabel('time')
                filename = parent_dir + "/slice_results/average_results/plot_slice%d_average_values.png" % j
                pyplot.savefig(filename)
                pyplot.close(fig)

            except:
                print("ERROR: in plotting average results for slice %d " % j)

    # export simulation average results for each slices
    if export_sim_avg:
        path = parent_dir + "/slice_results/average_results/data"
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        for j in range(no_of_slices):
            try:
                tmp_mean_queue_length = []
                tmp_mean_system_time = []
                tmp_mean_throughput = []
                tmp_packets_dropped = []
                tmp_packets_served = []
                tmp_packets_total = []
                tmp_blocking_probability = []
                for t in t_arr:
                    filename = path + "/%d_slice%d_average_values.csv" % (t, j)
                    with open(filename, 'rt')as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if row[0] == 'mean_queue_length': tmp_mean_queue_length.append(round(float(row[1]),2))
                            elif row[0] == 'mean_system_time': tmp_mean_system_time.append(round(float(row[1]),2))
                            elif row[0] == 'mean_throughput': tmp_mean_throughput.append(round(float(row[1]),2))
                            elif row[0] == 'packets_dropped': tmp_packets_dropped.append(round(float(row[1]),2))
                            elif row[0] == 'packets_served': tmp_packets_served.append(round(float(row[1]),2))
                            elif row[0] == 'packets_total': tmp_packets_total.append(round(float(row[1]),2))
                            elif row[0] == 'blocking_probability': tmp_blocking_probability.append(round(float(row[1]),2))

                #  Storing average data
                row_list = [["mean_queue_length", np.nanmean(tmp_mean_queue_length)],
                            ["mean_system_time", np.nanmean(tmp_mean_system_time)],
                            ["mean_throughput", np.nanmean(tmp_mean_throughput)],
                            ["packets_dropped", np.nanmean(tmp_packets_dropped)],
                            ["packets_served", np.nanmean(tmp_packets_served)],
                            ["packets_total", np.nanmean(tmp_packets_total)],
                            ["blocking_probability", np.nanmean(tmp_blocking_probability)]]
                filename = parent_dir + "/slice_results/average_results/sim_average_slice%d.csv" % j
                with open(filename, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(row_list)

            except:
                print("ERROR: in exporting average results for slice %d " % j)

