import numpy as np
#from matplotlib import pyplot
#from numpy import savetxt
#import csv
import pandas as pd


class SliceResult(object):
    """
    SliceResults gathers all simulation results that are generated during the simulation.

    This object should be returned after a simulation to extract the data for output analysis.
    """

    def __init__(self, sim):
        """
        Initialize SliceResult object
        :param sim: the simulation, this object belongs to
        :return: SliceResult object
        """
        self.sim = sim
        # self.system_utilization = 0
        self.packets_dropped = 0
        self.packets_served = 0
        self.packets_arrived = 0
        self.packets_served_SLA_satisfied = 0
        # self.mean_waiting_time = 0
        self.mean_system_time = np.NAN
        self.mean_queue_length = 0
        self.blocking_probability = 0
        self.mean_rate = np.NAN
        self.mean_throughput2 = np.NAN
        self.mean_cumulative_throughput2 = np.NAN

        self.total_throughput = 0

        index = 'mean_queue_length mean_system_time mean_rate mean_throughput2 cumulative_tp tp2_mov_avg packets_dropped packets_served packets_total blocking_probability packets_served_SLA_satisfied'
        self.df = pd.DataFrame(index=index.split())

        self.server_results = None
        #self.total_throughput_x = None
        #self.total_throughput_y = None

    def reset(self):
        """
        reset all result values before gathering
        """
        self.packets_dropped = 0
        self.packets_served = 0
        self.packets_arrived = 0
        self.packets_served_SLA_satisfied = 0

        self.mean_system_time = np.NAN
        self.mean_queue_length = 0
        self.blocking_probability = 0
        self.mean_rate = np.NAN
        self.mean_throughput2 = np.NAN
        self.mean_throughput2_mov_avg = np.NAN
        self.mean_cumulative_throughput2 = 0

        self.total_throughput = 0

    def gather_results(self, server_results):
        """
        Gather all available simulation results from SimState and CounterCollection
        """
        self.reset()
        self.server_results = server_results

        try:
            # # fill timestamps for total tp
            # for s in server_results:
            #     if s.cnt_tp is not None:
            #         self.total_throughput_x = s.cnt_tp.x_round
            #         self.total_throughput_y = np.zeros(self.total_throughput_x.shape)
            #         break
            #
            # # fill timestamps for total ql
            # for s in server_results:
            #     if s.cnt_ql is not None:
            #         self.total_ql_x = s.cnt_ql.x_round
            #         self.total_ql_y = np.zeros(self.total_ql_x.shape)
            #         break
            # self.total_syst_y = []
            # self.total_syst_x = []

            no_of_tp_users = 0
            no_of_tp_users2 = 0
            no_of_tp_users2_mov_avg = 0
            for i in range(len(server_results)):
                self.packets_arrived += server_results[i].packets_arrived
                self.packets_served += server_results[i].packets_served
                self.packets_dropped += server_results[i].packets_dropped

                self.packets_served_SLA_satisfied += server_results[i].packets_served_SLA_satisfied

                self.blocking_probability += server_results[i].blocking_probability
                self.mean_queue_length += server_results[i].mean_queue_length

                if server_results[i].mean_system_time is not np.NAN:
                    if self.mean_system_time is np.NAN:
                        self.mean_system_time = server_results[i].mean_system_time * server_results[i].packets_served
                    else:
                        self.mean_system_time += server_results[i].mean_system_time * server_results[i].packets_served

                self.mean_cumulative_throughput2 += server_results[i].mean_cumulative_throughput
                if server_results[i].mean_rate is not np.NAN:
                    self.total_throughput += server_results[i].mean_rate

                    if self.mean_rate is np.NAN:
                        self.mean_rate = server_results[i].mean_rate
                        no_of_tp_users += 1
                    else:
                        self.mean_rate += server_results[i].mean_rate
                        no_of_tp_users += 1

                if server_results[i].mean_throughput2 is not np.NAN:
                    if self.mean_throughput2 is np.NAN:
                        self.mean_throughput2 = server_results[i].mean_throughput2
                        no_of_tp_users2 += 1
                    else:
                        self.mean_throughput2 += server_results[i].mean_throughput2
                        no_of_tp_users2 += 1

                if server_results[i].mean_throughput2_mov_avg is not np.NAN:
                    if self.mean_throughput2_mov_avg is np.NAN:
                        self.mean_throughput2_mov_avg = server_results[i].mean_throughput2_mov_avg
                        no_of_tp_users2_mov_avg += 1
                    else:
                        self.mean_throughput2_mov_avg += server_results[i].mean_throughput2_mov_avg
                        no_of_tp_users2_mov_avg += 1


            # averaging for mean values
            no_of_users = float(len(server_results))
            self.blocking_probability /= no_of_users
            if self.packets_served > 0:
                self.mean_system_time /= self.packets_served  # since time independent, use served packet count as weights
            self.mean_queue_length /= no_of_users
            self.mean_cumulative_throughput2 /= no_of_users
            if no_of_tp_users > 0:
                self.mean_rate /= no_of_tp_users  # users with tp data are counted
            if no_of_tp_users2 > 0:
                self.mean_throughput2 /= no_of_tp_users2  # users with tp data are counted
            if no_of_tp_users2_mov_avg > 0:
                self.mean_throughput2_mov_avg /= no_of_tp_users2_mov_avg  # users with tp data are counted


            # Storing data with dataframe
            time = self.sim.sim_state.now
            self.df[time] = [self.mean_queue_length, self.mean_system_time, self.mean_rate, self.mean_throughput2,
                             self.mean_cumulative_throughput2, self.mean_throughput2_mov_avg, self.packets_dropped,
                             self.packets_served, self.packets_arrived, self.blocking_probability, self.packets_served_SLA_satisfied]


        except:
            print("ERROR: Slice Result.gather_results()_slice%d is empty. " % self.sim.slice_param.SLICE_ID)
            pass
