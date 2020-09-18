import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding

# import sys
# sys.path.insert(1, '/home/lkn/GitRepositories/ran_simulation/src/simulation')

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
import matplotlib.pyplot as plt


class RanSimEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, t_final: int = 1000):
        """
        Main ran_simulation
        """
        sim_param = SimParam(t_final)

        no_of_slices = sim_param.no_of_slices
        no_of_users_per_slice = sim_param.no_of_users_per_slice
        no_of_rb = len(sim_param.RB_pool)
        no_of_timeslots = int(sim_param.T_C / sim_param.T_S)

        # state space limits
        #  -------------------------------------------------------
        # method0 tp of users
        # np.finfo (np.float32).max
        high = np.array([2] * no_of_slices * no_of_users_per_slice)
        low = np.array([0] * no_of_slices * no_of_users_per_slice)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # #  -------------------------------------------------------
        # # method0 tp of slices
        # # np.finfo (np.float32).max
        # high = np.array([2] * no_of_slices )
        # low = np.array([0] * no_of_slices )
        # self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # # #  -------------------------------------------------------
        # # method1 ql
        # max_buffer_size = sim_param.max_buffer_size
        # high = np.array([max_buffer_size] * no_of_slices * no_of_users_per_slice)
        # low = np.array([0] * no_of_slices * no_of_users_per_slice)
        # self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # #  -------------------------------------------------------
        # # method2 CQI data
        # len_of_CQI_data = no_of_slices * no_of_users_per_slice * no_of_rb * no_of_timeslots
        # high = np.array([np.inf] * len_of_CQI_data)
        # low = np.array([0] * len_of_CQI_data)
        # self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # # #  -------------------------------------------------------
        # # method3 CQI data multidimentional box
        # self.observation_space = spaces.Box(low=0, high=np.inf, shape=(no_of_slices,no_of_users_per_slice,no_of_timeslots, no_of_rb),dtype=np.float32)
        # #  -------------------------------------------------------


        # action space limits
        #  -------------------------------------  method0 multi agent
        # self.action_space = spaces.MultiDiscrete(no_of_slices*[[no_of_rb] * no_of_timeslots]) # no_of_slices* no of rb * no_of_timeslots
        #  -------------------------------------  method1 single agent : no_of_slices ** no_of_rb
        # self.action_space = spaces.Discrete(no_of_slices ** no_of_rb)
        #  -------------------------------------  method2 single agent : no_of_rb: each digit maps rb to slice
        self.action_space = spaces.MultiDiscrete(no_of_rb * [no_of_slices])  # no of rb
        #  -------------------------------------  method3 PF with trimming alpha
        #self.action_space = spaces.Box( np.array([-1]),  np.array([1]), dtype=np.float32)
        #self.action_space = spaces.Discrete(3)
        # #  -------------------------------------------------------

        # other attributes of ran_environment
        self.state = None
        self.sim_param = sim_param
        #self.C_algo = 'RL'
        self.slice_scores = None  # slice scores for reward method 3
        self.user_scores = None

        # generate seed values
        new_seed = seeding.create_seed()
        self.sim_param.update_seeds(new_seed)

        self.user_score_arr = None
        self.slice_score_arr = None
        self.reward_hist = None
        self.cost_tp_hist = None
        self.cost_bp_hist = None
        self.cost_delay_hist = None
        self.reset_counter = 0

    def step(self, action):
        slices = self.slices
        # print("action: ", action)

        if self.sim_param.C_ALGO is not 'RL':  # action == 'baseline':
            #self.sim_param.C_ALGO = self.C_algo
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
        # #  -------------------------------------------------------
        # # method0 tp slices
        # for idx in range (len (self.slices)):
        #     # tp_exp = float(slc.slice_param.P_SIZE / slc.slice_param.MEAN_IAT)
        #     tp_exp = float (self.slices[idx].slice_param.RATE_REQ)
        #     self.state[idx] = float (self.slices[idx].slice_result.mean_throughput2_mov_avg / tp_exp)
        # #  -------------------------------------------------------
        # method0 tp
        for slc in self.slices:
            # tp_exp = float(slc.slice_param.P_SIZE / slc.slice_param.MEAN_IAT)
            tp_exp = float (slc.slice_param.RATE_REQ)
            #self.state[idx] = float (self.slices[idx].slice_result.mean_throughput2_mov_avg / tp_exp)
            for srv in slc.server_list:
                idx = srv.user.user_id
                self.state[idx] = float (srv.server_result.mean_throughput2 / tp_exp)
        # #  -------------------------------------------------------
        # method1: queue_lenghts
        # for slc in slices:
        #     for srv in slc.server_list:
        #         idx = srv.user.user_id
        #         self.state[idx] = srv.get_queue_length()
        # #  -------------------------------------------------------
        # # method 2 get CQI data
        # # get CQI matrix
        # CQI_data = self.SD_RAN_Controller.get_CQI_data(self.slices)
        #
        # # get observation from CQI_data
        # def recursive_len(item):
        #     if type(item) == list:
        #         return sum(recursive_len(subitem) for subitem in item)
        #     else:
        #         return 1
        # observations_arr = np.array(np.reshape(CQI_data, (1, recursive_len(CQI_data))))
        # self.state = observations_arr[0]
        # #  -------------------------------------------------------
        # # method 3 get CQI data
        # # get CQI matrix
        # CQI_data = self.SD_RAN_Controller.get_CQI_data(self.slices)  # bits per sec
        # cqi_arr = np.array(CQI_data[0])
        #
        # ql_arr = np.zeros(shape=cqi_arr.shape)  # (no_of_slices,no_of_users_per_slice,no_of_timeslots, no_of_rb)
        # for i in range(len(slices)):
        #     for j in range(len(slices[i].server_list)):
        #         user_ql = slices[i].server_list[j].get_queue_length()
        #         ql_arr[i, j] = user_ql
        #
        # self.state[0] = (cqi_arr[0] / (1000*2000)) + ql_arr[0]
        # self.state[1] = (cqi_arr[1] / (1000*10000)) + ql_arr[1]
        # self.state[2] = (cqi_arr[2] / (1000*5000)) + ql_arr[2]
        #
        # # self.state = (cqi_arr/1000) + ql_arr  #/2
        # #  -------------------------------------------------------

        # check done
        if slices[0].sim_state.now == self.sim_param.T_FINAL:
            done = 1
        else:
            done = 0
        done = bool(done)

        # calculate reward
        #  -------------------------------------------------------
        '''# method 0:   each slice 1 agent
        reward_arr = np.zeros(len(slices))
        for i in range(len(slices)):
            reward_arr[i] = slices[i].slice_result.mean_throughput/ self.sim_param.P_SIZE
        reward = reward_arr'''
        #  -------------------------------------------------------
        '''# method tp:   single agent
        reward = 0
        for i in range(len(slices)):
            reward += slices[i].slice_result.mean_throughput / self.sim_param.P_SIZE'''
        #  -------------------------------------------------------
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

        # #  -------------------------------------------------------
        # # method 3: scoring slices
        # def get_slice_scores():
        #     # Calculate QoE=successful_packets(QoS satisfied) / arrived_packets
        #     slice_scores = np.zeros(self.sim_param.no_of_slices)
        #     for i in range(len(self.slices)):
        #         p_arrived = self.slices[i].slice_result.packets_arrived
        #         p_served_SLA = self.slices[i].slice_result.packets_served_SLA_satisfied
        #         p_served = self.slices[i].slice_result.packets_served
        #         QoE: float = p_served_SLA / p_arrived if p_arrived > 0 else 0
        #         slice_scores[i] = QoE
        #     # print("SE: %f QoE: %f" % (SE, QoE))
        #     return slice_scores

        # # method 3: scoring users
        # def get_user_scores():
        #     # per user ---------------
        #     # Calculate user_score=successful_packets(QoS satisfied) - (dropped_packets + arrived_packets)
        #     user_scores = np.zeros(self.sim_param.no_of_slices * self.sim_param.no_of_users_per_slice)
        #     for i in range(self.sim_param.no_of_slices):
        #         for j in range(self.sim_param.no_of_users_per_slice):
        #             user_id = i * self.sim_param.no_of_users_per_slice + j
        #             tmp_result = self.slices[i].server_results[j]
        #
        #             p_arrived = tmp_result.packets_arrived
        #             p_dropped = tmp_result.packets_dropped
        #             p_served_SLA = tmp_result.packets_served_SLA_satisfied
        #
        #             tmp_user_score: float = p_served_SLA #- (p_dropped + p_arrived)
        #             user_scores[user_id] = tmp_user_score
        #     # ------------------------
        #     # print("SE: %f QoE: %f" % (SE, QoE))
        #     return user_scores
        #
        # def calculate_reward(scores_):
        #     score_deltas = np.subtract(scores_, self.user_scores)
        #
        #     reward = 0
        #     for s in score_deltas:
        #         reward += 1 if s > 0 else -1 if s < 0 else +0
        #
        #     # reward = np.sum(scores_)
        #     # print("scores: ", slice_scores_,"deltas: ", score_deltas)
        #     return reward

        # #  -------------------------------------------------------
        # slice_scores_ = get_slice_scores()
        # reward = calculate_reward(slice_scores_)
        # self.slice_scores = slice_scores_
        # self.slice_score_arr.append(slice_scores_)
        # #  -------------------------------------------------------
        # user_scores_ = get_user_scores()
        # reward = calculate_reward(user_scores_)
        # self.user_scores = user_scores_
        # self.user_score_arr.append(user_scores_)

        # #  -------------------------------------------------------
        # # method 4_1:   squared cost ( tp2 as cost)
        # def get_slice_scores():
        #     # Calculate QoE=successful_packets(QoS satisfied) / arrived_packets
        #     slice_scores = np.zeros(self.sim_param.no_of_slices)
        #     for i in range(len(slices)):
        #         rate_th = slices[i].slice_param.RATE_REQ #* (self.sim_param.T_S/self.sim_param.MEAN_IAT)
        #         delay_th = slices[i].slice_param.DELAY_REQ
        #         cost_tp = np.square((slices[i].slice_result.mean_throughput2 - rate_th)/rate_th) if slices[i].slice_result.mean_throughput2 < rate_th else 0
        #         cost_delay = np.square((slices[i].slice_result.mean_system_time - delay_th)/delay_th) if not np.isnan(slices[i].slice_result.mean_system_time) and slices[i].slice_result.mean_system_time > delay_th else 0
        #         cost_blocked = np.square(slices[i].slice_result.packets_dropped)
        #         slice_scores[i] = -1*(cost_tp + cost_delay + 1*cost_blocked)
        #         if slice_scores[i] < 0:
        #             print('time: %d, slice: %d ' % (self.slices[0].sim_state.now, i))
        #             if np.isnan(slices[i].slice_result.mean_system_time): print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: nan" % (cost_tp, cost_delay,cost_blocked, slices[i].slice_result.mean_throughput))
        #             else: print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: %.2f" % (cost_tp, cost_delay, cost_blocked, slices[i].slice_result.mean_throughput, slices[i].slice_result.mean_system_time))
        #     return slice_scores
        # # method 4_2:   squared cost ( cumulative values as cost)
        # def get_slice_scores():
        #     # Calculate QoE=successful_packets(QoS satisfied) / arrived_packets
        #     slice_scores = np.zeros(self.sim_param.no_of_slices)
        #     tp_hist_tmp = []
        #     bp_hist_tmp = []
        #     delay_hist_tmp = []
        #     for i in range(len(slices)):
        #         rate_th = slices[i].slice_param.RATE_REQ #* (self.sim_param.T_S/self.sim_param.MEAN_IAT)
        #         delay_th = slices[i].slice_param.DELAY_REQ
        #         cost_tp = np.square((slices[i].slice_result.mean_throughput2 - rate_th)/rate_th)  # if slices[i].slice_result.mean_throughput2 < rate_th else 0
        #         cost_delay = np.square(slices[i].slice_result.mean_system_time/delay_th)
        #         cost_blocked = np.square(slices[i].slice_result.blocking_probability)
        #
        #         # slice_scores[i] = 2 - 1 * (cost_tp + cost_blocked)
        #         if i == 0:
        #             slice_scores[i] = 1 - cost_blocked
        #         if i == 1:
        #             slice_scores[i] = 1 - cost_delay
        #         if i == 2:
        #             slice_scores[i] = 1 - cost_delay
        #
        #         tp_hist_tmp.append(np.round(cost_tp,2))
        #         bp_hist_tmp.append(np.round(cost_blocked,2))
        #         delay_hist_tmp.append(np.round(cost_delay,2))
        #         # slice_scores[i] = slices[i].slice_result.mean_cumulative_throughput2 / 4000  # -1 * (cost_tp)
        #
        #         # if slice_scores[i] < 0:
        #         #     print('time: %d, slice: %d ' % (self.slices[0].sim_state.now, i))
        #         #     if np.isnan(slices[i].slice_result.mean_system_time): print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: nan" % (cost_tp, cost_delay,cost_blocked, slices[i].slice_result.mean_throughput))
        #         #     else: print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: %.2f" % (cost_tp, cost_delay, cost_blocked, slices[i].slice_result.mean_throughput, slices[i].slice_result.mean_system_time))
        #     self.cost_tp_hist.append(tp_hist_tmp)
        #     self.cost_bp_hist.append(bp_hist_tmp)
        #     self.cost_delay_hist.append (delay_hist_tmp)
        #     return slice_scores

        # method 4_3:  rms per user RR_slice, mean tp difference_mcqi slice and rms slice errors
        def get_slice_scores():
            slice_scores = np.zeros (self.sim_param.no_of_slices)
            tp_hist_tmp = []
            bp_hist_tmp = []
            delay_hist_tmp = []

            for i in range (len (slices)):
                rate_th = slices[i].slice_param.RATE_REQ  # * (self.sim_param.T_S/self.sim_param.MEAN_IAT)
                delay_th = slices[i].slice_param.DELAY_REQ

                tmp_data = 0
                for j in range(self.sim_param.no_of_users_per_slice):
                    user_id = i * self.sim_param.no_of_users_per_slice + j
                    tmp_result = self.slices[i].server_results[j]

                    if i == 0 or i == 2:
                        tmp_data += np.square((tmp_result.mean_throughput2 - rate_th) / rate_th) #if tmp_result.mean_throughput2 < rate_th else 0
                    elif i == 1:
                        tmp_data += tmp_result.mean_throughput2
                if i == 0 or i == 2:
                    cost = np.sqrt(tmp_data / self.sim_param.no_of_users_per_slice)
                elif i == 1:
                    cost = -((tmp_data / self.sim_param.no_of_users_per_slice) - rate_th) / rate_th if (tmp_data / self.sim_param.no_of_users_per_slice) < rate_th else 0
                slice_scores[i] = cost

            return slice_scores

        def calculate_reward(scores_):
            #reward = np.sqrt (np.mean (self.slice_scores)) - np.sqrt (np.mean (np.square (scores_)))
            reward = 1 - np.sqrt (np.mean (np.square (scores_)))

            # print("scores: ", slice_scores_)#,"deltas: ", score_deltas)
            return reward

        slice_scores_ = get_slice_scores()
        reward = calculate_reward(slice_scores_)
        self.slice_scores = slice_scores_
        self.slice_score_arr.append(slice_scores_)
        self.reward_hist.append(reward)
        #  -------------------------------------------------------
        #
        # # method 4_4_(0_1):  0/1 per user or per slice, satisfy or not
        # def get_slice_scores():
        #     slice_scores = np.zeros (self.sim_param.no_of_slices)
        #     tp_hist_tmp = []
        #     bp_hist_tmp = []
        #     delay_hist_tmp = []
        #
        #     for i in range (len (slices)):
        #         rate_th = slices[i].slice_param.RATE_REQ  # * (self.sim_param.T_S/self.sim_param.MEAN_IAT)
        #         delay_th = slices[i].slice_param.DELAY_REQ
        #
        #         tmp_data = 0
        #         for j in range (self.sim_param.no_of_users_per_slice):
        #             user_id = i * self.sim_param.no_of_users_per_slice + j
        #             tmp_result = self.slices[i].server_results[j]
        #
        #             if i == 0 or i == 2:
        #                 tmp_data += 0 if tmp_result.mean_throughput2_mov_avg > rate_th else -1
        #             elif i == 1:
        #                 tmp_data += tmp_result.mean_throughput2_mov_avg
        #         if i == 0 or i == 2:
        #             score = tmp_data / self.sim_param.no_of_users_per_slice
        #         elif i == 1:
        #             score = 0 if (tmp_data / self.sim_param.no_of_users_per_slice) > rate_th else -1
        #
        #         slice_scores[i] = score
        #
        #         # tp_hist_tmp.append (np.round (cost_tp, 2))
        #         # bp_hist_tmp.append (np.round (cost_blocked, 2))
        #         # delay_hist_tmp.append (np.round (cost_delay, 2))
        #         # slice_scores[i] = slices[i].slice_result.mean_cumulative_throughput2 / 4000  # -1 * (cost_tp)
        #
        #         # if slice_scores[i] < 0:
        #         #     print('time: %d, slice: %d ' % (self.slices[0].sim_state.now, i))
        #         #     if np.isnan(slices[i].slice_result.mean_system_time): print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: nan" % (cost_tp, cost_delay,cost_blocked, slices[i].slice_result.mean_throughput))
        #         #     else: print("cost_tp: %.2f cost_delay: %.2f cost_blocked: %.2f mean_tp: %.2f mean_delay: %.2f" % (cost_tp, cost_delay, cost_blocked, slices[i].slice_result.mean_throughput, slices[i].slice_result.mean_system_time))
        #     # self.cost_tp_hist.append (tp_hist_tmp)
        #     # self.cost_bp_hist.append (bp_hist_tmp)
        #     # self.cost_delay_hist.append (delay_hist_tmp)
        #     return slice_scores
        # def calculate_reward(scores_):
        #     reward = 1 if (np.sum(scores_) == 0) else -np.square(np.sum(scores_))
        #     # print("scores: ", slice_scores_)#,"deltas: ", score_deltas)
        #     return reward
        #
        # slice_scores_ = get_slice_scores()
        # reward = calculate_reward(slice_scores_)
        # self.slice_scores = slice_scores_
        # self.slice_score_arr.append(slice_scores_)
        # self.reward_hist.append(reward)
        # #  -------------------------------------------------------

        return np.array(self.state), reward, done, {}

    def reset(self, **kwargs):
        ''' # insert parameters to sim_param
        if parameters != None:
          self.sim_param.SEED_IAT = parameters.SEED_IAT
          self.sim_param.SEED_SHADOWING = parameters.SEED_SHADOWING

        if NO_logging:
          log_file = None
        else:
          # update timestamp amd create result directories and logfile
          self.sim_param.update_timestamp()
          log_file = create_dir(self.sim_param)'''

        log_file = None
        #self.C_algo = C_algo  # enables baseline algorithms
        #self.sim_param.C_ALGO = C_algo

        # update seeds ( not for baselines)
        # if C_algo is 'RL':
        # new_seed = seeding.create_seed()
        # self.sim_param.update_seeds(new_seed)

        for key, value in kwargs.items():
            if key == 'env_seed':
                self.sim_param.update_seeds(value)
            if key == 'C_ALGO':
                self.sim_param.C_ALGO = value
        for key, value in kwargs.items():
            if key == 'plot_before_reset' and value is True:
                self.plot()


        # initialize all slices
        self.slices = initialize_slices(self.sim_param, log_file)

        # initialize SD_RAN_Controller
        self.SD_RAN_Controller = Controller(self.sim_param)

        # run simulation with random allocation
        def run_simulation_transient_phase(no_of_steps):
            C_ALGO_original = self.sim_param.C_ALGO
            self.sim_param.C_ALGO = 'Random'

            for _ in range(no_of_steps):
                RB_mapping = self.SD_RAN_Controller.RB_allocate_to_slices (self.slices[0].sim_state.now, self.slices)

                # simulate one round
                for i in range (len (self.slices)):
                    self.slices[i].prep_next_round (RB_mapping[i, :, :])
                    self.slices[i].simulate_one_round ()
            self.sim_param.C_ALGO = C_ALGO_original
            return

        run_simulation_transient_phase(no_of_steps=2)

        # get initial state
        #  -------------------------------------------------------
        # method 0 tp2 of users
        self.state = np.array([0] * self.sim_param.no_of_slices * self.sim_param.no_of_users_per_slice, dtype=np.float32)

        # method0 tp2  (added for transient phase)
        for slc in self.slices:
            # tp_exp = float(slc.slice_param.P_SIZE / slc.slice_param.MEAN_IAT)
            tp_exp = float (slc.slice_param.RATE_REQ)
            for srv in slc.server_list:
                idx = srv.user.user_id
                self.state[idx] = float(srv.server_result.mean_throughput2 / tp_exp)
        # #  -------------------------------------------------------
        # # method 0 tp2 of slices
        # self.state = np.array([0] * self.sim_param.no_of_slices, dtype=np.float32)
        #
        # # method0 tp2  (added for transient phase)
        # for idx in range(len(self.slices)):
        #     # tp_exp = float(slc.slice_param.P_SIZE / slc.slice_param.MEAN_IAT)
        #     tp_exp = float (self.slices[idx].slice_param.RATE_REQ)
        #     self.state[idx] = float (self.slices[idx].slice_result.mean_throughput2_mov_avg / tp_exp)
        # #  -------------------------------------------------------
        # # method 1 queue_lenghts
        # self.state = np.array([0] * self.sim_param.no_of_slices * self.sim_param.no_of_users_per_slice)
        # #  -------------------------------------------------------
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
        # ##  -------------------------------------------------------
        # # # method 3 get CQI matrix
        # CQI_data = self.SD_RAN_Controller.get_CQI_data(self.slices)
        # # self.state = np.array(CQI_data[0])
        # cqi_arr = np.array(CQI_data[0])
        # self.state = np.zeros(shape=cqi_arr.shape)
        # self.state[0] = (cqi_arr[0] / (1000*2000))
        # self.state[1] = (cqi_arr[1] / (1000*10000))
        # self.state[2] = (cqi_arr[2] / (1000*5000))
        # ##  -------------------------------------------------------


        # initialize slice scores as 0 from reward method 3
        self.slice_scores = np.zeros(self.sim_param.no_of_slices)
        self.slice_score_arr = []
        self.user_scores = np.zeros(self.sim_param.no_of_slices*self.sim_param.no_of_users_per_slice)
        self.user_score_arr = []
        self.reward_hist = []
        self.cost_tp_hist = []
        self.cost_bp_hist = []
        self.cost_delay_hist = []

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
        print_data_tp = ""
        print_data_delay = ""
        print_data_ql = ""
        for i in range(len(slices)):
            tmp_slice_result = slices[i].slice_result
            user_count = len(tmp_slice_result.server_results)  # choose latest result for data
            for k in range(user_count):
                common_name = "/slice%d_user%d_" % (i, tmp_slice_result.server_results[k].server.user.user_id)
                cc_temp = tmp_slice_result.server_results[k].server.counter_collection

                # round avg results
                filename = parent_dir + "/average_results/data/" + common_name + "avg_data.csv"
                df = tmp_slice_result.server_results[k].df
                df.to_csv(filename, header=True)

                # sim average results
                filename = parent_dir + "/average_results/data/" + common_name + "sim_avg_data.csv"
                mean_df = df.mean(axis=1)
                mean_df.to_csv(filename, header=True)
                # print mean tp/p_size
                print_data_tp = print_data_tp + "%.2f " % (mean_df.loc['mean_throughput2'] / slices[i].slice_param.P_SIZE)  # packets per ms
                # print mean delay
                print_data_delay = print_data_delay + "%.2f " % (mean_df.loc['mean_system_time'])  # delay in ms
                # print mean ql
                print_data_ql = print_data_ql + "%.2f " % (mean_df.loc['mean_queue_length'])

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
            print_data_tp = print_data_tp + " | "
            print_data_delay = print_data_delay + " | "
            print_data_ql = print_data_ql + " | "
        print("tp2   " + print_data_tp)
        print("delay " + print_data_delay)
        print ("ql " + print_data_ql)

        # slice results
        parent_dir = "results/" + sim_param.timestamp + "/slice_results"
        print_data_tp2 = ""
        print_data_bp = ""
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
            print_data_tp2 = print_data_tp2 + "%.2f " % (mean_df.loc['mean_throughput2'] / slices[i].slice_param.P_SIZE)
            # print mean tp/p_size
            print_data_bp = print_data_bp + "%.2f " % (mean_df.loc['blocking_probability'])
        print("tp2 " + print_data_tp2)
        print("dp  " + print_data_bp)

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

        # rb dist printing
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
        print("rb dist (RR MCQI PF): ", *np.round(np.divide(rb_dist, totalsum / 100), 1))

        # print slice scores
        # score_arr = np.array(self.user_score_arr)
        score_arr = np.array(self.slice_score_arr)
        score_arr = np.nan_to_num(score_arr, nan=0)

        def moving_average(interval, window_size):
            window = np.ones(int(window_size)) / float(window_size)
            return np.convolve(interval, window, 'same')

        window_size = 1

        fig = plt.figure()
        legend_str=[]
        # # user scores
        # for i in range(self.sim_param.no_of_slices*self.sim_param.no_of_users_per_slice):
        #     plt.plot(moving_average(score_arr[:, i], window_size), linestyle='-')
        #     legend_str.append('%d' % i)
        # slice scores
        for i in range(self.sim_param.no_of_slices):
            plt.plot(moving_average(score_arr[:, i], window_size), marker='.')
            legend_str.append('%d' % i)

        plt.legend(legend_str)
        # plt.show()
        filename = "results/" + sim_param.timestamp + "/scores.png"
        plt.savefig(filename)
        plt.close(fig)


def render(self, mode='human', close=False):
    ...
