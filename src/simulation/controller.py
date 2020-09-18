import numpy as np
import math
from matplotlib import pyplot
from numpy import savetxt
from itertools import cycle
import pandas as pd
from rng import RNG, ExponentialRNS, UniformRNS, UniformIntRNS


class Controller(object):
    """

    """

    def __init__(self, sim_param):
        """

        """
        self.sim_param = sim_param
        self.slices_cycle = []
        self.avg_rate_pf = []
        self.df = pd.DataFrame()

        # random allocation
        self.rng_rb_allocate = RNG(UniformIntRNS (0, sim_param.no_of_slices - 1, the_seed=sim_param.SEED_OFFSET), s_type='rb_allocation')

    def RB_allocate_from_action(self, t_start, slice_list, action):
        '''""" method 0: 1slice-1agent: discrete action (0, no_of_rb),
                        mapped to no_of_rb by bidding
        """
        # mapping actions to rbs
        no_of_rb = len(self.sim_param.RB_pool)
        if np.sum(action,axis=0)==0:
            bidding = np.sum(action,axis=1)/1.
        else:
            bidding = np.sum(action,axis=1)/np.sum(action,axis=0)
        bidding *= no_of_rb
        rb_allocation = np.floor(bidding).astype(int)
        rb_remaining = no_of_rb - np.sum(rb_allocation)
        while rb_remaining>0:
            bidding-=rb_allocation
            rb_allocation[np.argmax(bidding)]+=1  # only first occurance of max argument is returned
            rb_remaining-=1

        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C

        t_arr = np.arange(t_start, t_start+t_c, t_s)
        RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)
        rb_idx = 0
        for i in range(len(slice_list)):
            count = rb_allocation[i]
            while count>0:
                RB_mapping[i, rb_idx, 0]= True
                rb_idx+=1
                count -=1'''
        ##  -------------------------------------------------------
        '''"""
            method 1: 1agent: discrete action (0, no_of_slices ** no_of_rb), 
                        mapped to no_of_rb by convertion 
        """
        no_of_rb = len(self.sim_param.RB_pool)
        def dec_to_base( num, base, size):  # Maximum base - 36
            base_num = ""
            while num > 0:
                dig = int(num % base)
                if dig < 10:    base_num += str(dig)
                else:           base_num += chr(ord('A') + dig - 10)  # Using uppercase letters
                num //= base
            while len(base_num)<size: base_num += str(0)
            base_num = base_num[::-1]  # To reverse the string
            return base_num

        rb_dist = dec_to_base(action,len(slice_list), no_of_rb)

        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C
        t_arr = np.arange(t_start, t_start + t_c, t_s)
        RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)
        for i in range(no_of_rb):
            slice_idx = int(rb_dist[i])
            RB_mapping[slice_idx, i, 0] = True'''
        ##  -------------------------------------------------------
        """
            method 2: 1agent: Multi discrete action ( no_of_rb * [(0,no_of_slices)] )
                        maps no_of_rb to slices
        """
        no_of_rb = action.size
        rb_dist = action

        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C
        t_arr = np.arange(t_start, t_start + t_c, t_s)
        RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)
        for i in range(no_of_rb):
            slice_idx = int(rb_dist[i])
            RB_mapping[slice_idx, i] = True
        # ##  -------------------------------------------------------
        # """
        #     method 3:  PF with trimming alpha
        # """
        # t_s = self.sim_param.T_S
        # t_c = self.sim_param.T_C
        # t_arr = np.arange(t_start, t_start + t_c, t_s)
        # RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)
        #
        # # Prop Fair per RB, each user has avg_ratio( only works if each slice has same amount of users)
        # if len(self.avg_rate_pf) == 0:  # avg_rate initialization
        #     no_of_users = len(slice_list[0].user_list)
        #     self.avg_rate_pf = np.ones([RB_mapping.shape[0], no_of_users])  # indexing: slice,user
        #
        # avg_rate = self.avg_rate_pf
        # #alpha = (action + 1)/4  # -1,1 mapped to 0,1
        # if action==0: alpha = 0
        # elif action==1: alpha = 0.1
        # elif action==2: alpha = 0.5
        # else: RuntimeError("ERROR: wrong alpha.")
        # for j in range(RB_mapping.shape[1]):  # loop over RBs
        #     token_slice = -1
        #     token_user = -1
        #     max_ratio = -1
        #     for k in range(RB_mapping.shape[0]):  # loop over slices
        #         for u in range(len(slice_list[k].user_list)):  # loop over users
        #             tmp_user = slice_list[k].user_list[u]
        #             # tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
        #             tmp_CQI = tmp_user.channel.get_data_rate([j], t_start)  # insert index of rb as list and time
        #             tmp_ratio = tmp_CQI / avg_rate[k, u]  # current rate average rate ratio, indexing: slice,user
        #             if max_ratio < tmp_ratio:
        #                 max_ratio = tmp_ratio
        #                 token_slice = k
        #                 token_user = u
        #     RB_mapping[token_slice, j] = True  # indexing: slice,RB
        #
        #     # updating average rates for next rb-time slot (alpha = 0.1)
        #     for k2 in range(RB_mapping.shape[0]):  # loop over slices
        #         for u2 in range(len(slice_list[k2].user_list)):  # loop over users
        #             if k2 == token_slice and u2 == token_user:
        #                 tmp_user = slice_list[k2].user_list[u2]
        #                 # tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
        #                 tmp_CQI = tmp_user.channel.get_data_rate([j], t_start)  # insert index of rb as list and time
        #                 avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2] + alpha * tmp_CQI
        #             else:
        #                 avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2]
        #
        # ##  -------------------------------------------------------

        # Storing data with dataframe
        RB_allocation = np.full(RB_mapping.shape[1:], np.nan, dtype=int)
        for i in range(len(slice_list)):
            RB_allocation[RB_mapping[i] == True] = i

        t_arr = np.arange(t_start, t_start + t_c, t_s)
        idx = 0
        for t in t_arr:
            self.df[t] = RB_allocation[:, idx]
            idx += 1

        return RB_mapping

    def get_CQI_data(self, slice_list):
        '''
        return CQI values for each slice* user* rb* time combination within next round(T_C)

        :param slice_list:
        :return:
        '''

        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C
        t_start = slice_list[0].sim_state.now
        t_arr = np.arange(t_start, t_start + t_c, t_s)

        # CQI_matrix = np.zeros([len(slice_list),len(slice_list[0].server_list), len(self.sim_param.RB_pool), len(t_arr)])
        CQI_data = []
        tmp_CQI_slice = []
        for s in slice_list:  # loop over slices
            tmp_CQI_user = []
            for u in s.user_list:  # loop over users
                tmp_CQI_time = []
                for t in t_arr:  # loop over time
                    tmp_CQI_rb = []
                    for r in self.sim_param.RB_pool:  # loop over RBs
                        data_rate = u.channel.get_data_rate([r], t)  # insert index of rb as list, time
                        tmp_CQI = data_rate # / s.slice_param.P_SIZE
                        tmp_CQI_rb.append(tmp_CQI)
                    tmp_CQI_time.append(tmp_CQI_rb)
                tmp_CQI_user.append(tmp_CQI_time)
            tmp_CQI_slice.append(tmp_CQI_user)
        CQI_data.append(tmp_CQI_slice)

        return CQI_data

    def RB_allocate_to_slices(self, t_start, slice_list):
        """

        """
        t_s = self.sim_param.T_S
        t_c = self.sim_param.T_C

        t_arr = np.arange(t_start, t_start + t_c, t_s)
        RB_mapping = np.zeros([len(slice_list), len(self.sim_param.RB_pool), len(t_arr)], dtype=bool)

        # Hard slicing
        if self.sim_param.C_ALGO == 'H':
            no_of_RB_per_slice = int(RB_mapping.shape[1] / RB_mapping.shape[0])
            for i in range(RB_mapping.shape[0]):
                for j in range(no_of_RB_per_slice):
                    rb_idx = i * no_of_RB_per_slice + j
                    RB_mapping[i][rb_idx] = True

        # random allocation
        elif self.sim_param.C_ALGO == 'Random':
            for j in range(RB_mapping.shape[1]):  # loop over RBs
                tmp_slice_idx = self.rng_rb_allocate.get_rb()
                RB_mapping[tmp_slice_idx][j] = True

        # round robin
        elif self.sim_param.C_ALGO == 'RR':
            if not isinstance(self.slices_cycle, cycle):
                self.slices_cycle = cycle(np.arange(0, RB_mapping.shape[0]))
            for j in range(RB_mapping.shape[1]):  # loop over RBs
                tmp_slice_idx = next(self.slices_cycle)
                RB_mapping[tmp_slice_idx][j] = True

        # Max CQI
        elif self.sim_param.C_ALGO == 'MCQI':
            # CQI is calculated considering user with max CQI in a slice
            CQI_arr = np.zeros([len(slice_list), len(self.sim_param.RB_pool)])
            for i in range(len(slice_list)):  # loop over slices
                for k in range(RB_mapping.shape[1]):  # loop over RBs
                    max_CQI = -1
                    for u in slice_list[i].user_list:  # loop over users
                        # tmp_CQI2 = u.channel.channel_gains[k, t_arr[j]]  # indexing: RB,time
                        tmp_CQI = u.channel.get_data_rate([k], t_start)  # insert index of rb as list, time
                        if max_CQI < tmp_CQI:
                            max_CQI = tmp_CQI
                    CQI_arr[i, k] = max_CQI  # indexing: slice,RB

            # For each rb and time, map rb to max valued CQI_arr values owner slice
            for j in range(RB_mapping.shape[1]):  # loop over RBs
                max_CQI = -1
                for k in range(RB_mapping.shape[0]):  # loop over slices
                    tmp_CQI = CQI_arr[k, j]  # indexing: slice,RB
                    if max_CQI < tmp_CQI:
                        max_CQI = tmp_CQI
                        token = k
                RB_mapping[token, j] = True  # indexing: slice,RB

        # Prop Fair per RB, each user has avg_ratio( only works if each slice has same amount of users)
        elif self.sim_param.C_ALGO == 'PF':
            if len(self.avg_rate_pf) == 0:  # avg_rate initialization
                no_of_users = len(slice_list[0].user_list)
                self.avg_rate_pf = np.ones([RB_mapping.shape[0], no_of_users])  # indexing: slice,user

            avg_rate = self.avg_rate_pf
            alpha = self.sim_param.ALPHA_C
            for j in range(RB_mapping.shape[1]):  # loop over RBs
                token_slice = -1
                token_user = -1
                max_ratio = -1
                for k in range(RB_mapping.shape[0]):  # loop over slices
                    for u in range(len(slice_list[k].user_list)):  # loop over users
                        tmp_user = slice_list[k].user_list[u]
                        # tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
                        tmp_CQI = tmp_user.channel.get_data_rate([j], t_start)  # insert index of rb as list and time
                        tmp_ratio = tmp_CQI / avg_rate[k, u]  # current rate average rate ratio, indexing: slice,user
                        if max_ratio < tmp_ratio:
                            max_ratio = tmp_ratio
                            token_slice = k
                            token_user = u
                RB_mapping[token_slice, j] = True  # indexing: slice,RB

                # updating average rates for next rb-time slot (alpha = 0.1)
                for k2 in range(RB_mapping.shape[0]):  # loop over slices
                    for u2 in range(len(slice_list[k2].user_list)):  # loop over users
                        if k2 == token_slice and u2 == token_user:
                            tmp_user = slice_list[k2].user_list[u2]
                            # tmp_CQI = tmp_user.channel.channel_gains[j, t_arr[i]]  # indexing: RB,time
                            tmp_CQI = tmp_user.channel.get_data_rate([j], t_start)  # insert index of rb as list and time
                            avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2] + alpha * tmp_CQI
                        else:
                            avg_rate[k2, u2] = (1 - alpha) * avg_rate[k2, u2]

        # Storing data with dataframe
        RB_allocation = np.full(RB_mapping.shape[1:], np.nan, dtype=int)
        for i in range(len(slice_list)):
            RB_allocation[RB_mapping[i] == True] = i

        t_arr = np.arange(t_start, t_start + t_c, t_s)
        idx = 0
        for t in t_arr:
            self.df[t] = RB_allocation[:, idx]
            idx += 1

        return RB_mapping
