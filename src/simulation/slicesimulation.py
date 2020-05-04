# coding=utf-8
from simstate import SimState
from server import Server
from event import EventChain, PacketArrival, RoundTermination, ServerActivation, ServerDeactivation, RB_Allocation
from sliceresult import SliceResult
from sliceparam import SliceParam
from slicemanager import SliceManager
from countercollection import CounterCollection
from rng import RNG, ExponentialRNS
from channelmodal import ChannelModal
import numpy as np


class SliceSimulation(object):

    def __init__(self, slice_param, no_seed=False):
        """
        Initialize the Slice Simulation object.
        :param slice_param: is an optional SliceParam object for parameter pre-configuration
        :param no_seed: is an optional parameter. If it is set to True, the RNG should be initialized without a
        a specific seed.
        """
        self.slice_param = slice_param
        self.sim_state = SimState()
        self.slice_result = SliceResult(self)
        self.event_chain_slice_manager = EventChain()
        self.slice_manager = SliceManager(self)

        self.user_list = []
        self.server_list = []
        self.server_list_dict = {}

    def insert_users(self, user_list):
        self.user_list = user_list
        self.server_list = []
        self.server_list_dict = {}
        for i in self.user_list:
            temp_server = Server(self, i, EventChain())
            self.server_list.append(temp_server)
            self.server_list_dict.update({i.user_id: self.server_list[-1]})

    def reset(self):
        """
        Reset the Simulation object.
        """
        self.sim_state = SimState()
        self.slice_result = SliceResult(self)

    def remove_upcoming_events(self):
        """
        Check the timestamps of oldest events from each event chain of users and SliceManager
        Find the smallest timestamp and remove only the events with this timestamp
        Return current_events[]
        """
        current_events = []
        current_events_dict = {}
        t_arr = []
        for i in self.server_list:      # t_arr includes timestamps of oldest events in all event_chains
            #t_arr.append(i.event_chain.event_list[0].timestamp)
            if len(i.event_chain.event_list)!=0:
                t_arr.append(float(i.event_chain.copy_oldest_event().timestamp))
            else:
                t_arr.append(np.inf)
        #t_arr.append(self.event_chain_slice_manager.event_list[0].timestamp)  # last element of t_arr belongs event_chain_slice_manager
        t_arr.append(float(self.event_chain_slice_manager.copy_oldest_event().timestamp))
        t_arr = np.array(t_arr)
        current_events_idx = (t_arr == t_arr.min())

        for i in range(len(current_events_idx) - 1):
            if current_events_idx[i]:
                current_events.append(self.server_list[i].event_chain.remove_oldest_event())  # remove oldest elements from event chains
                current_events_dict.update({current_events[-1]: self.server_list[i]})

        if current_events_idx[-1]:
            current_events.append(self.event_chain_slice_manager.remove_oldest_event())     # remove oldest element from event_chain_slice_manager
            current_events_dict.update({current_events[-1]: self.event_chain_slice_manager})

        return current_events, current_events_dict

    def prep_next_round(self, RB_mapping):
        """
        Prepares the Simulation object for the next round.
        """
        self.sim_state.prep_next_round()
        for i in self.server_list:
            i.server_state.prep_next_round()
        self.slice_param.RB_mapping = RB_mapping
        self.slice_result = SliceResult(self)  # server results are not reset due to counters
        # self.rng.iat_rns.set_parameters(1.)
        # self.rng.st_rns.set_parameters(1. / float(self.slice_param.RHO))

    def simulate_one_round(self):  
        """
        Do one simulation run. Initialize simulation and create first and last event.
        After that, one after another event is processed.
        :return: SliceResult object
        """
        self.sim_state.t_round_start = self.sim_state.now

        # insert first and last event
        self.event_chain_slice_manager.insert(RoundTermination(self, self.sim_state.now + self.slice_param.T_C))

        # insert periodic RB_Allocation events
        t_arr = np.arange(self.sim_state.now, self.sim_state.now + self.slice_param.T_C, self.slice_param.T_SM)
        for t in t_arr:
            self.event_chain_slice_manager.insert(RB_Allocation(self, t))

        # insert packet arrivals from traffic lists of users
        for i in self.user_list:
            tmp = i.traffic_list_dict[self.slice_param.SLICE_ID]
            tmp_traffic_list = filter(lambda item: (
                    self.sim_state.now <= item.timestamp < self.sim_state.now + self.slice_param.T_C),
                            tmp)
            tmp_server = self.server_list_dict[i.user_id]
            for j in tmp_traffic_list:
                tmp_server.event_chain.insert(j)

        # start simulation (run)
        while not self.sim_state.stop:
            # remove upcoming events
            [current_events, current_events_dict] = self.remove_upcoming_events()
            if len(current_events) != len(current_events_dict):
                raise RuntimeError("ERROR: Event to server mapping error.")

            for e in current_events:
                if e.timestamp == 80:
                    msa = 3
                if e.priority == 0:
                    msa = 3
                if e:
                    # if event exists and timestamps are ok, process the event
                    if self.sim_state.now <= e.timestamp:
                        self.sim_state.now = e.timestamp

                        if not (e.priority == 4 or e.priority == 5):    # dont count for for slice manager events
                            current_events_dict[e].counter_collection.count_queue()
                        e.process(current_events_dict[e])
                        if e.timestamp % 1000 == 0:
                            print("TIMESTAMP: " + str(e.timestamp) + ",PRIORITY " + str(e.priority))
                    else:
                        print("NOW: " + str(self.sim_state.now) + ", EVENT TIMESTAMP: " + str(e.timestamp) + " " + str(e.priority))
                        raise RuntimeError("ERROR: TIMESTAMP OF EVENT IS SMALLER THAN CURRENT TIME.")

                else:
                    print("Event chain is empty. Abort")
                    self.sim_state.stop = True

        #  gather results for slice_result object and all servers results
        self.server_results = []
        self.server_results_dict = {}
        for i in self.user_list:
            tmp_server = self.server_list_dict[i.user_id]
            self.server_results.append(tmp_server.server_result.gather_results())
            self.server_results_dict.update({i.user_id: self.server_results[-1]})

        self.slice_result.gather_results(self.server_results)
        return self.slice_result
