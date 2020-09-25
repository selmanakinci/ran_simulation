import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from countercollection import CounterCollection
from server import Server
import os
import re
import csv
from statistics import mean
from simparam import SimParam
import pandas as pd


def plot_results(parent_dir, sim_param=SimParam(), slices = []):


    # choose plots
    plot_controller = True
    plot_slice_manager = True
    plot_user_results = True
    plot_user_results_avg = True
    plot_slice_results = True

    # parameters
    t_c = sim_param.T_C
    t_sm = sim_param.T_SM
    t_final = sim_param.T_FINAL
    no_of_slices = sim_param.no_of_slices
    #no_of_users_per_slice = sim_param.no_of_users_per_slice

    # Controller
    if plot_controller:
        path = parent_dir + "/controller/"
        filename = path + "data/rb_allocation.csv"
        df = pd.read_csv(filename)

        fig = plt.figure(figsize=(sim_param.T_FINAL/100, 5), dpi=100)
        im = plt.imshow(df.values, origin='lower', aspect='auto', interpolation='none')
        ax = plt.gca()
        xticks = np.arange(0, sim_param.T_FINAL, 50)
        yticks = np.arange(0, len(sim_param.RB_pool), 2)
        ax.set_xticks(xticks)
        ax.set_yticks(yticks)

        if no_of_slices != 1:
            colors = [im.cmap(float(value / (no_of_slices - 1))) for value in range(
                no_of_slices)]  # get the colors of the values, according to the colormap used by imshow
            patches = [mpatches.Patch(color=colors[k], label="Slice id {l}".format(l=k)) for k in
                       range(no_of_slices)]  # create a patch (proxy artist) for every color
        else:
            colors = im.cmap(0.)
            patches = [mpatches.Patch(label="Slice id {l}".format(l=k)) for k in
                       range(no_of_slices)]  # create a patch (proxy artist) for every color

        plt.legend(handles=patches, bbox_to_anchor=(1, 1), loc='upper left')
        filename = path + "plot_RB_allocation.png"
        plt.savefig(filename)
        plt.close(fig)


    # SLICE MANAGER
    # plotting RB matching
    if plot_slice_manager:
        path = parent_dir + "/sm/"
        for i in range(no_of_slices):
            filename = path + "data/slice%d_rb_allocation.csv" % (i)
            df = pd.read_csv(filename)

            fig = plt.figure(figsize=(sim_param.T_FINAL/100, 5), dpi=100)
            im = plt.imshow(df.values,origin='lower' , aspect='auto',interpolation='none')
            ax = plt.gca()
            xticks = np.arange(0,sim_param.T_FINAL,50)
            yticks = np.arange(0,len(sim_param.RB_pool),5)
            ax.set_xticks(xticks)
            ax.set_yticks(yticks)

            no_of_users_in_slice = sim_param.no_of_users_list[i]
            if no_of_users_in_slice != 1:
                colors = [im.cmap(float(value / (no_of_users_in_slice - 1))) for value in range(
                    no_of_users_in_slice)]  # get the colors of the values, according to the colormap used by imshow
                patches = [mpatches.Patch(color=colors[k], label="User id {l}".format(l=k)) for k in
                           range(no_of_users_in_slice)]  # create a patch (proxy artist) for every color
            else:
                colors = im.cmap(0.)
                patches = [mpatches.Patch(label="User id {l}".format(l=k)) for k in
                           range(no_of_users_in_slice)]  # create a patch (proxy artist) for every color

            plt.legend(handles=patches, bbox_to_anchor=(1,1), loc='upper left')
            filename = path + "plot_slice_%d.png" % i
            plt.savefig(filename)
            plt.close(fig)

    # Server(user) Results
    pseudo_server = Server(0,0,0)
    tmp_counter_collection = CounterCollection(pseudo_server)
    user_id = 0
    if plot_user_results:
        path = parent_dir + "/user_results"
        for j in range(no_of_slices):
            for k in range(sim_param.no_of_users_list[j]):
                #user_id = j*no_of_users_per_slice + k

                # tp
                filename = path + "/tp" + "/slice%d_user%d_tp_data.csv" % (j, user_id)
                df = pd.read_csv(filename, header= None, index_col=0)
                tmp_counter_collection.cnt_tp.sum_power_two = df.loc['SumPowerTwo'].to_numpy()
                tmp_counter_collection.cnt_tp.values = df.loc['Values'].to_numpy()
                tmp_counter_collection.cnt_tp.timestamps = df.loc['Timestamps'].to_numpy()
                plotname = path + "/tp" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_tp.timestamps.size ==0:
                    print("Warning: Throughput data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_tp.plot(plotname, one_round=False)

                # tp2
                filename = path + "/tp2" + "/slice%d_user%d_tp2_data.csv" % (j, user_id)
                df = pd.read_csv(filename, header=None, index_col=0)
                tmp_counter_collection.cnt_tp2.sum_power_two = df.loc['SumPowerTwo'].to_numpy()
                tmp_counter_collection.cnt_tp2.values = df.loc['Values'].to_numpy()
                tmp_counter_collection.cnt_tp2.timestamps = df.loc['Timestamps'].to_numpy()
                plotname = path + "/tp2" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_tp2.timestamps.size ==0:
                    print("Warning: Throughput data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_tp2.plot(plotname, one_round=False)

                # ql
                filename = path + "/ql" + "/slice%d_user%d_ql_data.csv" % (j, user_id)
                df = pd.read_csv(filename, header=None, index_col=0)
                tmp_counter_collection.cnt_ql.sum_power_two = df.loc['SumPowerTwo'].to_numpy()
                tmp_counter_collection.cnt_ql.values = df.loc['Values'].to_numpy()
                tmp_counter_collection.cnt_ql.timestamps = df.loc['Timestamps'].to_numpy()
                plotname = path + "/ql" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_ql.timestamps.size ==0:
                    print("Warning: Queue length data for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_ql.plot(plotname, one_round=False)

                # syst (delay)
                filename = path + "/delay" + "/slice%d_user%d_delay_data.csv" % (j, user_id)
                df = pd.read_csv(filename, header=None, index_col=0)
                tmp_counter_collection.cnt_syst.values = df.loc['Values'].to_numpy()
                tmp_counter_collection.cnt_syst.timestamps = df.loc['Timestamps'].to_numpy()
                plotname = path + "/delay" + "/plot_slice%d_user%d.png" % (j, user_id)
                if tmp_counter_collection.cnt_syst.timestamps.size == 0:
                    print("Warning: System Time for slice%d_user%d is empty. " % (j, user_id))
                else:
                    tmp_counter_collection.cnt_syst.plot(plotname, one_round=False)
                user_id+=1


    # use below to plot average results
    ####### average results can be plotted by batching normal results(histogram)
    if plot_user_results_avg:
        path = parent_dir + "/user_results/average_results/data"
        #for i in range(int(t_final/t_c)):
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        user_id=0
        for j in range(no_of_slices):
            for k in range(sim_param.no_of_users_list[j]):
                #user_id = j * no_of_users_per_slice + k
                filename = path + "/slice%d_user%d_avg_data.csv" % (j, user_id)
                df = pd.read_csv(filename, header=0, index_col=0)
                tmp_mean_queue_length = df.loc['mean_queue_length'].to_numpy()
                tmp_mean_system_time = df.loc['mean_system_time'].to_numpy()
                tmp_mean_throughput = df.loc['mean_throughput2'].to_numpy()
                tmp_packets_total = df.loc['packets_total'].to_numpy()
                tmp_packets_served = df.loc['packets_served'].to_numpy()
                tmp_packets_dropped = df.loc['packets_dropped'].to_numpy()
                tmp_blocking_probability = df.loc['blocking_probability'].to_numpy()

                fig, axes = plt.subplots(4, 2, figsize=(12, 20))
                try:
                    tmp_data = tmp_mean_queue_length
                    tmp_plot = axes[0, 0]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [mean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_mean_system_time
                    tmp_plot = axes[1, 0]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center', transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_mean_throughput
                    tmp_plot = axes[2, 0]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), np.nanmean(tmp_data) * 1.001, 'mean:%.2f' % (np.nanmean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_packets_total
                    tmp_plot = axes[0, 1]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_packets_served
                    tmp_plot = axes[1, 1]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_packets_dropped
                    tmp_plot = axes[2, 1]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass
                try:
                    tmp_data = tmp_blocking_probability
                    tmp_plot = axes[3, 1]
                    tmp_plot.plot(t_arr, tmp_data, linestyle='-', marker='o')
                    tmp_plot.plot(t_arr, [np.nanmean(tmp_data)] * len(tmp_data), linestyle='--', color='r')
                    #tmp_plot.text(t_arr.min(), mean(tmp_data) * 1.001, 'mean:%.2f' % (mean(tmp_data)))
                    tmp_plot.text(0.1, 0.9, 'mean:%.2f' % (np.nanmean(tmp_data)), ha='center', va='center',
                                  transform=tmp_plot.transAxes)
                except:
                    print ("ERROR: plot user avg")
                    pass

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
                axes[2,0].set_ylabel('mean_throughput2')
                axes[0,1].set_ylabel('packets_total')
                axes[1,1].set_ylabel('packets_served')
                axes[2,1].set_ylabel('packets_dropped')
                axes[3,1].set_ylabel('blocking_probability')
                axes[3,1].set_xlabel('time')
                axes[0,0].set_xlabel('time')
                filename = parent_dir + "/user_results/average_results/plot_slice%d_user%d_average_values.png" % (j, user_id)
                plt.savefig(filename)
                plt.close(fig)
                user_id += 1


    # plot average slice results
    if plot_slice_results:
        path = parent_dir + "/slice_results/average_results/data"
        #for i in range(int(t_final/t_c)):
        t_arr = np.arange(t_c,t_final+t_c,t_c)
        for j in range(no_of_slices):
            try:

                filename = path + "/slice%d_avg_data.csv" % j
                df = pd.read_csv(filename, header=0, index_col=0)
                tmp_mean_queue_length = df.loc['mean_queue_length'].to_numpy()
                tmp_mean_system_time = df.loc['mean_system_time'].to_numpy()
                tmp_mean_throughput = df.loc['mean_throughput2'].to_numpy()
                tmp_packets_total = df.loc['packets_total'].to_numpy()
                tmp_packets_served = df.loc['packets_served'].to_numpy()
                tmp_packets_dropped = df.loc['packets_dropped'].to_numpy()
                tmp_blocking_probability = df.loc['blocking_probability'].to_numpy()

                fig, axes = plt.subplots(4, 2, figsize=(12, 20))
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
                axes[2,0].set_ylabel('mean_throughput2')
                axes[0,1].set_ylabel('packets_total')
                axes[1,1].set_ylabel('packets_served')
                axes[2,1].set_ylabel('packets_dropped')
                axes[3,1].set_ylabel('blocking_probability')
                axes[3,1].set_xlabel('time')
                axes[0,0].set_xlabel('time')
                filename = parent_dir + "/slice_results/average_results/plot_slice%d_average_values.png" % j
                plt.savefig(filename)
                plt.close(fig)

            except:
                print("ERROR: in plotting average results for slice %d " % j)
