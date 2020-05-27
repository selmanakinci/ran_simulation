from counter import TimeIndependentCounter
from slicesimulation import SliceSimulation
from matplotlib import pyplot
from trafficgenerator import TrafficGenerator
from sliceparam import SliceParam
from simparam import SimParam
from user import User
from controller import Controller
from datetime import datetime
from createdirectory import create_dir
from plot_results import plot_results
from numpy import savetxt
import numpy as np
from rng import RNG, ExponentialRNS, UniformRNS
from pandas import DataFrame


def ran_simulation():
    """
    Main ran_simulation
    """


    # define sim_param and inside RB pool: all available Resources list
    sim_param = SimParam()

    no_of_slices = sim_param.no_of_slices
    no_of_users_per_slice = sim_param.no_of_users_per_slice

    # create result directories
    create_dir(sim_param)

    # create logfile and write SimParameters
    results_dir = "results/" + sim_param.timestamp
    log_file = open(results_dir + "/logfile.txt", "wt")
    log_file.write('no_of_slices: %d\nno_of_users_per_slice: %d\n\n' % (no_of_slices, no_of_users_per_slice))
    attrs = vars(sim_param)
    log_file.write('SimParam\n'+''.join("%s: %s\n" % item for item in attrs.items()))
    # log_file.close()

    # initialize SD_RAN_Controller
    SD_RAN_Controller = Controller(sim_param)

    # Each slice has different users
    slices = []
    slice_results = []

    # initialize all slices
    for i in range(no_of_slices):
        slice_param_tmp = SliceParam(sim_param)
        slice_param_tmp.SLICE_ID = i
        slices.append(SliceSimulation(slice_param_tmp))
        slice_results.append([])

        # initialize all users with traffics and distances
        tmp_users = []
        seed_dist = 0  # users in all slices have identical distance distributions
        #rng_dist = RNG(ExponentialRNS(lambda_x=1. / float(sim_param.MEAN_Dist)), s_type='dist') # , the_seed=seed_dist
        rng_dist = RNG(UniformRNS(sim_param.DIST_MIN,sim_param.DIST_MAX, the_seed=seed_dist), s_type='dist')  #
        dist_arr = [10, 100 ]#[30, 30, 100, 100, 100, 100, 100, 100, 100, 100]  # 10*(1+user_id%no_of_users_per_slice)**2
        for j in range(no_of_users_per_slice):
            user_id = i*no_of_users_per_slice + j
            #tmp_users.append(User(user_id, rng_dist.get_dist(), slice_list=[slices[i]], sim_param=sim_param))
            tmp_users.append(User(user_id, dist_arr[j], slice_list=[slices[i]], sim_param=sim_param))

        # insert user to slices
        slices[i].insert_users(tmp_users)


    # Choose Slice Manager Algorithm, 'PF': prop fair, 'MCQI': Max Channel Quality Index, 'RR': round-robin
    slices[0].slice_param.SM_ALGO = 'RR'
    slices[1].slice_param.SM_ALGO = 'MCQI'
    slices[2].slice_param.SM_ALGO = 'PF'

    # log Slice Parameters
    for i in range(no_of_slices):
        attrs = vars(slices[i].slice_param)
        log_file.write('\nSliceParam\n' + ''.join("%s: %s\n" % item for item in attrs.items()))
    #log_file.close()

    # loop rounds for each slice
    for i in range(int(sim_param.T_FINAL/sim_param.T_C)):
        RB_mapping = SD_RAN_Controller.RB_allocate_to_slices(slices[0].sim_state.now, slices)

        for j in range(len(slices)):
            slices[j].prep_next_round(RB_mapping[j,:,:])
            slice_results[j].append(slices[j].simulate_one_round())

    # Store Simulation Results
    # user results
    parent_dir = "results/" + sim_param.timestamp + "/user_results"
    path = parent_dir + "/tp"
    for i in range(len(slice_results)):
        user_count = len(slice_results[i][-1].server_results)   # choose latest result for data
        for k in range(user_count):
            common_name = "/slice%d_user%d_" % (i, slice_results[i][-1].server_results[k].server.user.user_id)
            cc_temp = slice_results[i][-1].server_results[k].server.counter_collection
            # tp
            filename = parent_dir + "/tp" + common_name + "sum_power_two.csv"
            savetxt(filename, cc_temp.cnt_tp.sum_power_two, delimiter=',')
            filename = parent_dir + "/tp" + common_name + "values.csv"
            savetxt(filename, cc_temp.cnt_tp.values, delimiter=',')
            filename = parent_dir + "/tp" + common_name + "timestamps.csv"
            savetxt(filename, cc_temp.cnt_tp.timestamps, delimiter=',')

            filename = parent_dir + "/tp" + common_name + "all_data.csv"
            #savetxt(filename, np.transpose(np.array([cc_temp.cnt_tp.values,cc_temp.cnt_tp.timestamps])), delimiter=',')
            df = DataFrame(np.transpose(np.array([cc_temp.cnt_tp.values,cc_temp.cnt_tp.timestamps])), columns=['Values', 'Timestamps'])
            export_csv = df.to_csv(filename, index=None, header=True)

            # tp2
            filename = parent_dir + "/tp2" + common_name + "sum_power_two.csv"
            savetxt(filename, cc_temp.cnt_tp2.sum_power_two, delimiter=',')
            filename = parent_dir + "/tp2" + common_name + "values.csv"
            savetxt(filename, cc_temp.cnt_tp2.values, delimiter=',')
            filename = parent_dir + "/tp2" + common_name + "timestamps.csv"
            savetxt(filename, cc_temp.cnt_tp2.timestamps, delimiter=',')
            # ql
            filename = parent_dir + "/ql" + common_name + "sum_power_two.csv"
            savetxt(filename, cc_temp.cnt_ql.sum_power_two, delimiter=',')
            filename = parent_dir + "/ql" + common_name + "values.csv"
            savetxt(filename, cc_temp.cnt_ql.values, delimiter=',')
            filename = parent_dir + "/ql" + common_name + "timestamps.csv"
            savetxt(filename, cc_temp.cnt_ql.timestamps, delimiter=',')
            # system time (delay)
            filename = parent_dir + "/delay" + common_name + "values.csv"
            savetxt(filename, cc_temp.cnt_syst.values, delimiter=',')
            filename = parent_dir + "/delay" + common_name + "timestamps.csv"
            savetxt(filename, cc_temp.cnt_syst.timestamps, delimiter=',')
            # Find how to insert histograms


    # plot results
    parent_dir = "results/" + sim_param.timestamp
    plot_results(parent_dir, no_of_slices, no_of_users_per_slice, sim_param, slices)

    # rb dist printing
    filename = "results/" + sim_param.timestamp + "/summary"
    rb_total = 0
    rb_dist = []
    for s in slices:
        rb_dist_slice = []
        for u in s.server_list:
            rb_dist_slice.append(u.RB_counter)
        slicesum = np.nansum(rb_dist_slice)

        print("Slice %d dist: " % s.slice_param.SLICE_ID, *np.round(np.divide(rb_dist_slice,slicesum/100), 1))
        # write these to file savetxt(filename, cc_temp.cnt_ql.sum_power_two, delimiter=',')
        rb_dist.append(slicesum)
    totalsum = np.nansum(rb_dist)
    print("rb dist (RR MCQI PF): ", *np.round(np.divide(rb_dist, totalsum / 100), 1))




if __name__ == '__main__':
    ran_simulation()
