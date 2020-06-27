import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding

# import sys
# sys.path.insert(1, '/home/lkn/GitRepositories/ran_simulation/src/simulation')

# from counter import TimeIndependentCounter
# from slicesimulation import SliceSimulation
# from trafficgenerator import TrafficGenerator
# from sliceparam import SliceParam
from simparam import SimParam
# from user import User
from controller import Controller
# from datetime import datetime
from createdirectory import create_dir
from initialize_slices import initialize_slices
# from numpy import savetxt
import numpy as np
# from rng import RNG, ExponentialRNS, UniformRNS
from pandas import DataFrame
from plot_results import plot_results


class RanSimEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, t_final: int = 100):
        """
        Main ran_simulation
        """
        sim_param = SimParam(t_final)

        no_of_slices = sim_param.no_of_slices
        no_of_users_per_slice = sim_param.no_of_users_per_slice
        no_of_rb = len(sim_param.RB_pool)
        no_of_timeslots = int(sim_param.T_C / sim_param.T_S)

        # state space limits
        ##  -------------------------------------------------------
        # method1 ql
        max_buffer_size = sim_param.max_buffer_size
        high = np.array([max_buffer_size] * no_of_slices * no_of_users_per_slice)
        low = np.array([0] * no_of_slices * no_of_users_per_slice)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        ##  -------------------------------------------------------
        '''# method2 CQI data
        len_of_CQI_data = no_of_slices * no_of_users_per_slice * no_of_rb * no_of_timeslots
        high = np.array([np.inf] * len_of_CQI_data)
        low = np.array([0] * len_of_CQI_data)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)'''
        ##  -------------------------------------------------------

        # action space limits
        ##  -------------------------------------  method0 multi agent
        # self.action_space = spaces.MultiDiscrete(no_of_slices*[[no_of_rb] * no_of_timeslots]) # no_of_slices* no of rb * no_of_timeslots
        ##  -------------------------------------  method1 single agent : no_of_slices ** no_of_rb
        # self.action_space = spaces.Discrete(no_of_slices ** no_of_rb)
        ##  -------------------------------------  method2 single agent : no_of_rb: each digit maps rb to slice
        self.action_space = spaces.MultiDiscrete(no_of_rb * [no_of_slices])  # no of rb
        ##  -------------------------------------------------------

        # other attributes of ran_environment
        self.state = None
        self.sim_param = sim_param
        self.C_algo = None
        self.slice_scores = None  # slice scores for reward method 3

    def step(self, action):
        slices = self.slices

        if self.C_algo is not None:  # action == 'baseline':
            self.sim_param.C_ALGO = self.C_algo
            RB_mapping = self.SD_RAN_Controller.RB_allocate_to_slices(slices[0].sim_state.now, slices)
        else:
            assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
            # assign resources depending on action
            RB_mapping = self.SD_RAN_Controller.RB_allocate_from_action(slices[0].sim_state.now, slices, action)

        # simulate one round
        for i in range(len(slices)):
            slices[i].prep_next_round(RB_mapping[i, :, :])
            slices[i].simulate_one_round()
            # slice_results[i].append(slices[i].simulate_one_round())

        # get next state
        ##  -------------------------------------------------------
        # method1: queue_lenghts
        for slc in slices:
            for srv in slc.server_list:
                idx = srv.user.user_id
                self.state[idx] = srv.get_queue_length()
        ##  -------------------------------------------------------
        '''# method 2 get CQI data
        # get CQI matrix
        CQI_data = self.SD_RAN_Controller.get_CQI_data(self.slices)

        # get observation from CQI_data
        def recursive_len(item):
            if type(item) == list:
                return sum(recursive_len(subitem) for subitem in item)
            else:
                return 1
        observations_arr = np.array(np.reshape(CQI_data, (1, recursive_len(CQI_data))))
        self.state = observations_arr[0]'''
        ##  -------------------------------------------------------

        # check done
        if slices[0].sim_state.now == self.sim_param.T_FINAL:
            done = 1
        else:
            done = 0
        done = bool(done)

        # calculate reward
        ##  -------------------------------------------------------
        '''# method 0:   each slice 1 agent
        reward_arr = np.zeros(len(slices))
        for i in range(len(slices)):
            reward_arr[i] = slices[i].slice_result.mean_throughput/ self.sim_param.P_SIZE
        reward = reward_arr'''
        ##  -------------------------------------------------------
        '''# method tp:   single agent
        reward = 0
        for i in range(len(slices)):
            reward += slices[i].slice_result.mean_throughput / self.sim_param.P_SIZE'''
        ##  -------------------------------------------------------
        '''# method 1: DRL paper
        def calculate_reward(self, RB_mapping):
            # calculate SE=tp/BW
            SE = 0
            for i in range(len(self.slices)):
                SE += self.slices[i].slice_result.total_throughput * 1e3  # in bits
            SE /= (self.sim_param.RB_BANDWIDTH * len(self.sim_param.RB_pool))
            # Calculate QoE=successful_packets(QoS satisfied) / arrived_packets
            p_arrived = 0
            p_served = 0
            p_served_SLA = 0
            for i in range(len(self.slices)):
                p_arrived += self.slices[i].slice_result.packets_arrived
                p_served_SLA += self.slices[i].slice_result.packets_served_SLA_satisfied
                p_served += self.slices[i].slice_result.packets_served
            QoE: float = p_served_SLA / p_arrived if p_arrived > 0 else 0
            a = 1 / 100
            b = 1
            reward = a * SE + b * QoE
            # print("SE: %f QoE: %f" % (SE, QoE))
            return reward
        reward = calculate_reward(self, RB_mapping)'''
        ##  -------------------------------------------------------
        # method 3: scoring slices
        def get_slice_scores():
            # Calculate QoE=successful_packets(QoS satisfied) / arrived_packets
            slice_scores = np.zeros([self.sim_param.no_of_slices])
            for i in range(len(self.slices)):
                p_arrived = self.slices[i].slice_result.packets_arrived
                p_served_SLA = self.slices[i].slice_result.packets_served_SLA_satisfied
                p_served = self.slices[i].slice_result.packets_served
                QoE: float = p_served_SLA / p_arrived if p_arrived > 0 else 0
                slice_scores[i] = QoE

            # print("SE: %f QoE: %f" % (SE, QoE))
            return slice_scores

        def calculate_reward(slice_scores_):
            score_deltas = np.subtract(slice_scores_, self.slice_scores)
            reward = np.sum(score_deltas)
            #print("scores: ", slice_scores_,"deltas: ", score_deltas)
            return reward

        slice_scores_ = get_slice_scores()
        reward = calculate_reward(slice_scores_)
        self.slice_scores = slice_scores_
        ##  -------------------------------------------------------

        return np.array(self.state), reward, done, {}

    def reset(self, parameters=None, NO_logging=1, C_algo=None, **kwargs):
        ''' # insert parameters to sim_param
        if parameters != None:
          self.sim_param.SEED_IAT = parameters.SEED_IAT
          self.sim_param.SEED_SHADOWING = parameters.SEED_SHADOWING'''

        '''if NO_logging:
          log_file = None
        else:
          # update timestamp amd create result directories and logfile
          self.sim_param.update_timestamp()
          log_file = create_dir(self.sim_param)'''

        # plot before reset
        for key, value in kwargs.items():
            if key == 'plot_before_reset' and value is True:
                self.plot()

        log_file = None
        self.C_algo = C_algo  # enables baseline algorithms

        # update seeds ( not for baselines)
        if C_algo is None:
            new_seed = seeding.create_seed()
            self.sim_param.update_seeds(new_seed)

        # initialize all slices
        self.slices = initialize_slices(self.sim_param, log_file)

        # initialize SD_RAN_Controller
        self.SD_RAN_Controller = Controller(self.sim_param)

        # get initial state
        ##  -------------------------------------------------------
        self.state = np.array([0] * self.sim_param.no_of_slices * self.sim_param.no_of_users_per_slice)
        ##  -------------------------------------------------------
        # # method 2 get CQI matrix
        # CQI_data = self.SD_RAN_Controller.get_CQI_data(self.slices)
        #
        # # get observation from CQI_data
        # def recursive_len(item):
        #     if type(item) == list:
        #         return sum(recursive_len(subitem) for subitem in item)
        #     else:
        #         return 1
        #
        # observations_arr = np.array(np.reshape(CQI_data, (1, recursive_len(CQI_data))))
        # self.state = observations_arr[0]
        ##  -------------------------------------------------------

        # initialize slice scores as 0 from reward method 3
        self.slice_scores = np.zeros(self.sim_param.no_of_slices)

        return np.array(self.state)

    def plot(self):
        # temp solution for logfile
        self.sim_param.update_timestamp()
        log_file = create_dir(self.sim_param)

        sim_param = self.sim_param
        slices = self.slices
        # slice_results = self.slice_results
        no_of_slices = sim_param.no_of_slices
        no_of_users_per_slice = sim_param.no_of_users_per_slice

        # Store Simulation Results
        # user results
        parent_dir = "results/" + sim_param.timestamp + "/user_results"
        print_data = ""
        for i in range(len(slices)):
            tmp_slice_result = slices[i].slice_result
            user_count = len(tmp_slice_result.server_results)  # choose latest result for data
            for k in range(user_count):
                common_name = "/slice%d_user%d_" % (i, tmp_slice_result.server_results[k].server.user.user_id)
                cc_temp = tmp_slice_result.server_results[k].server.counter_collection

                # avg results
                filename = parent_dir + "/average_results/data/" + common_name + "avg_data.csv"
                df = tmp_slice_result.server_results[k].df
                df.to_csv(filename, header=True)

                # sim average results
                filename = parent_dir + "/average_results/data/" + common_name + "sim_avg_data.csv"
                mean_df = df.mean(axis=1)
                mean_df.to_csv(filename, header=True)
                # print mean tp/p_size
                print_data = print_data + "%.2f " % (mean_df.loc['mean_throughput'] / sim_param.P_SIZE)

                # tp
                filename = parent_dir + "/tp" + common_name + "tp_data.csv"
                df = DataFrame(
                    np.array([cc_temp.cnt_tp.timestamps, cc_temp.cnt_tp.values, cc_temp.cnt_tp.sum_power_two]),
                    index=['Timestamps', 'Values', 'SumPowerTwo'])
                df.to_csv(filename, header=False)
                # tp2
                filename = parent_dir + "/tp2" + common_name + "tp2_data.csv"
                df = DataFrame(
                    np.array([cc_temp.cnt_tp2.timestamps, cc_temp.cnt_tp2.values, cc_temp.cnt_tp2.sum_power_two]),
                    index=['Timestamps', 'Values', 'SumPowerTwo'])
                df.to_csv(filename, header=False)
                # ql
                filename = parent_dir + "/ql" + common_name + "ql_data.csv"
                df = DataFrame(
                    np.array([cc_temp.cnt_ql.timestamps, cc_temp.cnt_ql.values, cc_temp.cnt_ql.sum_power_two]),
                    index=['Timestamps', 'Values', 'SumPowerTwo'])
                df.to_csv(filename, header=False)
                # system time (delay)
                filename = parent_dir + "/delay" + common_name + "delay_data.csv"
                df = DataFrame(np.array([cc_temp.cnt_syst.timestamps, cc_temp.cnt_syst.values]),
                               index=['Timestamps', 'Values'])
                df.to_csv(filename, header=False)
                # Find how to insert histograms
            print_data = print_data + " | "
        print(print_data)

        # slice results
        parent_dir = "results/" + sim_param.timestamp + "/slice_results"
        print_data = ""
        for i in range(len(slices)):
            common_name = "/slice%d_" % i
            # avg results
            filename = parent_dir + "/average_results/data/" + common_name + "avg_data.csv"
            df = slices[i].slice_result.df
            df.to_csv(filename, header=True)

            # sim average results
            filename = parent_dir + "/average_results/data/" + common_name + "sim_avg_data.csv"
            mean_df = df.mean(axis=1)
            mean_df.to_csv(filename, header=True)
            # print mean tp/p_size
            print_data = print_data + "%.2f " % (mean_df.loc['mean_throughput'] / sim_param.P_SIZE)
        print(print_data)

        # Store Slice manager allocation dataframe
        parent_dir = "results/" + sim_param.timestamp + "/sm/data/"
        for i in range(len(slices)):
            common_name = "/slice%d_" % i
            filename = parent_dir + common_name + "rb_allocation.csv"
            df = slices[i].slice_manager.df
            df.to_csv(filename, header=True, index=False)

        # Store Controller allocation dataframe
        parent_dir = "results/" + sim_param.timestamp + "/controller/data/"
        filename = parent_dir + "rb_allocation.csv"
        df = self.SD_RAN_Controller.df
        df.to_csv(filename, header=True, index=False)

        # plot results
        parent_dir = "results/" + sim_param.timestamp
        plot_results(parent_dir, sim_param, slices)

        '''# rb dist printing
        filename = "results/" + sim_param.timestamp + "/summary"
        rb_total = 0
        rb_dist = []
        for s in slices:
            rb_dist_slice = []
            for u in s.server_list:
                rb_dist_slice.append(u.RB_counter)
            slicesum = np.nansum(rb_dist_slice)
        
            print("Slice %d dist: " % s.slice_param.SLICE_ID, *np.round(np.divide(rb_dist_slice, slicesum / 100), 1))
            # write these to file savetxt(filename, cc_temp.cnt_ql.sum_power_two, delimiter=',')
            rb_dist.append(slicesum)
        totalsum = np.nansum(rb_dist)
        print("rb dist (RR MCQI PF): ", *np.round(np.divide(rb_dist, totalsum / 100), 1))'''


def render(self, mode='human', close=False):
    ...
