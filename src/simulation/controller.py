import numpy as np
from matplotlib import pyplot
from numpy import savetxt
from itertools import cycle


class Controller(object):
    """

    """

    def __init__(self, sim_param):
        """

        """
        self.sim_param = sim_param
        self.slices_cycle = []
        self.avg_rate_pf = []

    def RB_allocate_to_slices(self, t_start, slice_list):
        """

        """
        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C

        t_arr = np.arange(t_start, t_start+t_c, t_s)
        RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)


        # Hard slicing
        if self.sim_param.C_ALGO == 'H':
            no_of_RB_per_slice = int(RB_mapping.shape[1]/RB_mapping.shape[0])
            for i in range(RB_mapping.shape[0]):
                for j in range(no_of_RB_per_slice):
                    rb_idx = i * no_of_RB_per_slice + j
                    RB_mapping[i][rb_idx] = True

        # round robin
        elif self.sim_param.C_ALGO == 'RR':
            if not isinstance(self.slices_cycle, cycle):
                self.slices_cycle = cycle(np.arange(0,RB_mapping.shape[0]))
            # slices_cycle = cycle(np.arange(0,RB_mapping.shape[0]))
            for i in range(RB_mapping.shape[2]):         # loop over time
                for j in range(RB_mapping.shape[1]):     # loop over RBs
                    tmp_slice_idx = next(self.slices_cycle)
                    RB_mapping[tmp_slice_idx][j][i] = True

        # Max CQI
        elif self.sim_param.C_ALGO == 'MCQI':
            # CQI is calculated considering user with max CQI in a slice
            CQI_arr = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)])
            for i in range(len(slice_list)):              # loop over slices
                for j in range(RB_mapping.shape[2]):      # loop over time
                    for k in range(RB_mapping.shape[1]):  # loop over RBs
                        max_CQI = -1
                        for u in slice_list[i].user_list:     # loop over users
                            # tmp_CQI2 = u.channel.channel_gains[k, t_arr[j]]  # indexing: RB,time
                            tmp_CQI = u.channel.get_data_rate([k], t_arr[j])  # insert index of rb as list, time
                            if max_CQI < tmp_CQI:
                                max_CQI = tmp_CQI
                        CQI_arr[i, k, j] = max_CQI         # indexing: slice,RB,time

            # For each rb and time, map rb to max valued CQI_arr values owner slice
            for i in range(RB_mapping.shape[2]):          # loop over time
                for j in range(RB_mapping.shape[1]):      # loop over RBs
                    max_CQI = -1
                    for k in range(RB_mapping.shape[0]):  # loop over slices
                        tmp_CQI = CQI_arr[k,j,i]       # indexing: slice,RB,time
                        if max_CQI < tmp_CQI:
                            max_CQI = tmp_CQI
                            token = k
                    RB_mapping[token,j,i] = True    # indexing: slice,RB,time

         # Prop Fair per RB, each user has avg_ratio( only works if each slice has same amount of users)
        elif self.sim_param.C_ALGO == 'PF':

            if len(self.avg_rate_pf) == 0:        # avg_rate initialization
                no_of_users = len(slice_list[0].user_list)
                self.avg_rate_pf = np.ones([RB_mapping.shape[0], no_of_users])  # indexing: slice,user

            avg_rate = self.avg_rate_pf
            alpha = self.sim_param.ALPHA_C
            for i in range(RB_mapping.shape[2]):  # loop over time
                for j in range(RB_mapping.shape[1]):  # loop over RBs
                    token_slice = -1
                    token_user = -1
                    max_ratio = -1
                    for k in range(RB_mapping.shape[0]):  # loop over slices
                        for u in range(len(slice_list[k].user_list)):  # loop over users
                            tmp_user = slice_list[k].user_list[u]
                            #tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
                            tmp_CQI = tmp_user.channel.get_data_rate([j], t_arr[i])  # insert index of rb as list and time

                            tmp_ratio = tmp_CQI / avg_rate[k, u]   # current rate average rate ratio, indexing: slice,user

                            if max_ratio < tmp_ratio:
                                max_ratio = tmp_ratio
                                token_slice = k
                                token_user = u
                    RB_mapping[token_slice, j, i] = True    # indexing: slice,RB,time

                    # updating average rates for next rb-time slot (alpha = 0.1)
                    for k2 in range(RB_mapping.shape[0]):  # loop over slices
                        for u2 in range(len(slice_list[k2].user_list)):  # loop over users
                            if k2 == token_slice and u2 == token_user:
                                tmp_user = slice_list[k2].user_list[u2]
                                #tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
                                tmp_CQI = tmp_user.channel.get_data_rate([j], t_arr[i])  # insert index of rb as list and time
                                avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2] + alpha * tmp_CQI
                            else:
                                avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2]


        # # plotting RB mapping
        # fig, axes = pyplot.subplots(1, RB_mapping.shape[0], figsize=(12, 3))
        #
        # if RB_mapping.shape[0]==1:
        #     axes.imshow(RB_mapping[i], aspect='auto')
        # else:
        #     for i in range(RB_mapping.shape[0]):
        #         axes[i].imshow(RB_mapping[i], aspect='auto')
        #
        # path = "plots/" + self.sim_param.timestamp + "/controller"
        # filename = path + "/controller_%d.png" % t_start
        # pyplot.savefig(filename)
        # pyplot.close(fig)

        # Storing Data
        path = "results/" + self.sim_param.timestamp + "/controller/data"

        for i in range(len(slice_list)):
            filename = path + "/RB_list_t_%d_slice_%d.csv" % (t_start,i)
            savetxt(filename, RB_mapping[i], delimiter=',')


        return RB_mapping
