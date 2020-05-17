import numpy as np
from itertools import cycle
from event import ServerActivation, ServerDeactivation
from matplotlib import pyplot
from matplotlib import colors
import matplotlib.patches as mpatches
from numpy import savetxt
import pandas as pd


class SliceManager(object):
    """

    """

    def __init__(self, slicesim):
        """
        Generate TrafficGenerator objects and initialize variables.
        """
        self.slicesim = slicesim
        self.user_ids_cycle = []
        self.avg_rate_pf = []
        self.df = pd.DataFrame()

    def RB_allocate_to_users(self):
        """

        """
        t_s = self.slicesim.slice_param.T_S
        t_sm = self.slicesim.slice_param.T_SM
        t_c = self.slicesim.slice_param.T_C
        idx1 = int((self.slicesim.sim_state.now - self.slicesim.sim_state.t_round_start) / t_s)
        idx2 = int(min(idx1 + t_sm/t_s, t_c/t_s))
        RB_mapping_sm = self.slicesim.slice_param.RB_mapping[:, idx1:idx2]
        RB_matching_sm = np.full(RB_mapping_sm.shape,np.nan)


        # Necessary Inputs: buffer states(byte), user ids, CQI_list, average_rate(FairQueing)
        buffer_states = []
        CQI_list = []
        avg_r_tmp = []
        user_ids = []
        for i in self.slicesim.server_list:
            # buffer_states.append(i.buffer.get_queue_length())
            buffer_states.append(i.buffer.get_queue_length_bits())  # served_packet_size added, in byte
            CQI_list.append(i.get_CQI_list(RB_mapping_sm))
            avg_r_tmp.append(1.)   # for pf algorithm for each rb
            user_ids.append(i.user.user_id)
        if not isinstance(self.user_ids_cycle, cycle):
            self.user_ids_cycle = cycle(user_ids)
        if len(self.avg_rate_pf) == 0:
            self.avg_rate_pf = avg_r_tmp

        RB_user_lists = [[[-1] for _ in range(RB_mapping_sm.shape[1])] for _ in range(len(user_ids))]

        # fill RB_matching_sm
        for i in range(RB_mapping_sm.shape[1]):         # loop over time
            # round robin
            if self.slicesim.slice_param.SM_ALGO == 'RR':
                for j in range(RB_mapping_sm.shape[0]):     # loop over RBs
                    if RB_mapping_sm[j][i]:
                        for _ in range(len(user_ids)):      # to ensure not repeat users
                            next_user_id = next(self.user_ids_cycle)
                            if (buffer_states[next_user_id%len(user_ids)] > 0) or not self.slicesim.slice_param.buffer_check:     # buffer control
                                RB_matching_sm[j,i] = next_user_id
                                break

            # Max CQI per RB
            elif self.slicesim.slice_param.SM_ALGO == 'MCQI':
                for j in range(RB_mapping_sm.shape[0]):  # loop over RBs
                    if RB_mapping_sm[j][i]:
                        max_CQI = -1
                        for k in range(len(CQI_list)):  # loop over users
                            if (buffer_states[k] > 0) or not self.slicesim.slice_param.buffer_check:         # buffer control
                                tmp_CQI = CQI_list[k][i][j]  # indexing: user,time,RB
                            else:
                                tmp_CQI = -1
                            if max_CQI < tmp_CQI:
                                max_CQI = tmp_CQI
                                RB_matching_sm[j, i] = user_ids[k]

            # Prop Fair per RB, each user has avg_ratio
            elif self.slicesim.slice_param.SM_ALGO == 'PF':
                alpha = self.slicesim.slice_param.ALPHA_SM
                avg_rate = self.avg_rate_pf
                for j in range(RB_mapping_sm.shape[0]):  # loop over RBs
                    if RB_mapping_sm[j][i]:
                        token = -1
                        max_ratio = -1
                        for k in range(len(CQI_list)):   # loop over users
                            tmp_CQI = CQI_list[k][i][j]  # for current rate, indexing: user,time,RB
                            if (buffer_states[k] > 0) or not self.slicesim.slice_param.buffer_check:     # buffer control
                                tmp_ratio = tmp_CQI / avg_rate[k]  # current rate average rate ratio, indexing: user
                            else:
                                tmp_ratio = -1
                            if max_ratio < tmp_ratio:
                                max_ratio = tmp_ratio
                                RB_matching_sm[j, i] = user_ids[k]
                                token = k  # indicates the winner user

                        # updating average rates for next rb-time slot (alpha = 0.1)
                        for k2 in range(len(user_ids)):  # loop over users
                            if k2 == token:
                                tmp_CQI = CQI_list[k2][i][j]  # for current rate
                                avg_rate[token] = (1 - alpha) * avg_rate[token] + alpha * tmp_CQI
                            else:
                                avg_rate[k2] = (1 - alpha) * avg_rate[k2]

            # fill RB_user_lists
            for u1 in range(len(user_ids)):     # loop over user array
                temp_list = []
                for k in range(RB_matching_sm.shape[0]):    # loop over RBs
                    if RB_matching_sm[k,i] == user_ids[u1]:
                        temp_list.append(k)         # if RB matches, add RB into list
                if not temp_list==[]:
                    RB_user_lists[u1][i] = temp_list

        #  insert_RB_to_servers
        for u2 in range(len(user_ids)):         # loop over user array
            tmp_server = self.slicesim.server_list_dict[user_ids[u2]]
            prev_RB = tmp_server.RB_list             # current RB list
            for i in range(len(RB_user_lists[0])):  # loop over time
                RB_list = RB_user_lists[u2][i]

                # insert RB_list to server
                if not RB_list == prev_RB:  # or (i == len(RB_user_lists[0])-1): second part is commented for now
                    if not RB_list == [-1]:       # -1 corresponds to no RB
                        tmp_server.event_chain.insert(ServerActivation(self.slicesim,self.slicesim.sim_state.now + t_s*i,RB_list))
                    else:
                        tmp_server.event_chain.insert(ServerDeactivation(self.slicesim,self.slicesim.sim_state.now + t_s*i))

                # Counting total rb count
                if not RB_list == [-1]:  # -1 corresponds to no RB
                    tmp_server.RB_counter += len(RB_list)

                prev_RB = RB_list

        # # plotting RB matching
        # # create a color map with random colors
        # fig = pyplot.figure()
        # im = pyplot.imshow(RB_matching_sm)
        # # get the colors of the values, according to the
        # # colormap used by imshow
        # colors = [im.cmap(im.norm(value)) for value in user_ids]
        # # create a patch (proxy artist) for every color
        # patches = [mpatches.Patch(color=colors[i], label="User id {l}".format(l=user_ids[i])) for i in range(len(user_ids))]
        # # put those patched as legend-handles into the legend
        # pyplot.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        #
        # path = "plots/" + self.slicesim.slice_param.timestamp + "/sm"
        # filename = path + "/slice_%d_t_%d.png" % (int(self.slicesim.slice_param.SLICE_ID), self.slicesim.sim_state.now)
        # pyplot.savefig(filename)
        # pyplot.close(fig)

        '''# Storing Data
        path = "results/" + self.slicesim.slice_param.timestamp + "/sm/data"
        filename = path + "/RB_matching_t_%d_slice_%d.csv" % (self.slicesim.sim_state.now, int(self.slicesim.slice_param.SLICE_ID))
        savetxt(filename, RB_matching_sm, delimiter=',')'''

        # Storing data with dataframe
        t_arr = np.arange(self.slicesim.sim_state.now,self.slicesim.sim_state.now+t_sm,t_s)
        idx = 0
        for t in t_arr:
            self.df[t] = RB_matching_sm[:,idx]
            idx +=1

        return

