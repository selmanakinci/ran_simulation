#import os
from numpy import savetxt
import csv


class ServerResult(object):

    """
    SliceResults gathers all simulation results that are generated during the simulation.

    This object should be returned after a simulation to extract the data for output analysis.
    """

    def __init__(self, server):
        """
        Initialize SliceResult object
        :param server: the simulation, this object belongs to
        :return: SliceResult object
        """
        self.server = server
        #self.system_utilization = 0
        self.packets_dropped = 0    # no of dropped packets
        self.packets_accepted = 0   # no of accepted packets
        self.packets_served = 0     # no of packets completely served
        self.packets_arrived = 0    # no of arrived packets
        #self.mean_waiting_time = 0
        self.mean_system_time = -1
        self.mean_queue_length = 0
        self.mean_throughput = 0
        self.blocking_probability = 0

        self.counter_collection = self.server.counter_collection

        # self.cnt_tp = None
        # self.cnt_ql = None
        # self.cnt_syst = None

    def gather_results(self):
        """
        Gather all available simulation results from SimState and CounterCollection
        """
        parent_dir = "results/" + self.server.slicesim.slice_param.timestamp + "/user_results/average_results/data"
        common_name = "/%d_slice%d_user%d_" % (self.server.slicesim.sim_state.now, self.server.slicesim.slice_param.SLICE_ID, self.server.user.user_id)

        try:
            #self.system_utilization = self.server.counter_collection.cnt_sys_util.get_mean()
            #self.mean_waiting_time = self.server.counter_collection.acnt_wt.get_mean()

            self.mean_queue_length = self.server.counter_collection.cnt_ql.get_mean_one_round()
            self.mean_system_time = self.server.counter_collection.cnt_syst.get_mean_one_round()
            self.mean_throughput = self.server.counter_collection.cnt_tp.get_mean_one_round()
            self.mean_throughput2 = self.server.counter_collection.cnt_tp2.get_mean_one_round()

            # self.cnt_tp = self.server.counter_collection.cnt_tp
            # self.cnt_ql = self.server.counter_collection.cnt_ql
            # self.cnt_syst = self.server.counter_collection.cnt_syst

            # # Plotting
            # filename = parent_dir + "tp" + common_name + "tp.png"
            # self.server.counter_collection.cnt_tp.plot(filename)
            #
            # filename = parent_dir + "ql" + common_name + "H_ql.png"
            # self.server.counter_collection.hist_ql.report(filename)
            # filename = parent_dir + "ql" + common_name + "ql.png"
            # self.server.counter_collection.cnt_ql.plot(filename)
            #
            # filename = parent_dir + "delay" + common_name + "H_delay.png"
            # self.server.counter_collection.hist_syst.report(filename)
            # filename = parent_dir + "delay" + common_name + "delay.png"
            # self.server.counter_collection.cnt_syst.plot(filename)

            self.packets_dropped = self.server.server_state.num_blocked_packets
            self.packets_served = self.server.server_state.num_completed_packets
            self.packets_total = self.server.server_state.num_packets
            self.blocking_probability = self.server.server_state.get_blocking_probability()

            # Storing average data
            row_list = [["mean_queue_length", self.mean_queue_length],
                        ["mean_system_time", self.mean_system_time],
                        ["mean_throughput", self.mean_throughput],
                        ["mean_throughput2", self.mean_throughput2],
                        ["packets_dropped", self.packets_dropped],
                        ["packets_served", self.packets_served],
                        ["packets_total", self.packets_total],
                        ["blocking_probability", self.blocking_probability]]
            filename = parent_dir + common_name + "average_values.csv"
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(row_list)

            # Storing data with dataframe



        except:
            print("ERROR: Server Result.gather_results()_slice%d_user_%d is empty. " % (self.server.slicesim.slice_param.SLICE_ID, self.server.user.user_id))
            pass

        return self

    def update(self):
        """
        Gather all available simulation results from SimState and CounterCollection
        """
        self.gather_results()