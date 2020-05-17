import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding

#import sys
#sys.path.insert(1, '/home/lkn/GitRepositories/ran_simulation/src/simulation')

from counter import TimeIndependentCounter
#from slicesimulation import SliceSimulation
from trafficgenerator import TrafficGenerator
#from sliceparam import SliceParam
from simparam import SimParam
#from user import User
from controller import Controller
from datetime import datetime
from createdirectory import create_dir
from initialize_slices import initialize_slices
from numpy import savetxt
import numpy as np
#from rng import RNG, ExponentialRNS, UniformRNS
from pandas import DataFrame
from plot_results import plot_results

class RanSimEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    """
    Main ran_simulation
    """
    sim_param = SimParam()

    # state space limits
    max_buffer_size = sim_param.max_buffer_size
    no_of_slices = sim_param.no_of_slices
    high = np.array([max_buffer_size]*no_of_slices) # max buffer size * no_of_slices
    low = np.array([0, 0, 0])
    self.observation_space = spaces.Box(low, high, dtype=np.float32)

    # action space limits
    no_of_rb =  len(sim_param.RB_pool)
    no_of_timeslots = int(sim_param.T_C / sim_param.T_S)
    self.action_space = spaces.MultiDiscrete(no_of_slices*[[no_of_rb] * no_of_timeslots]) # no_of_slices* no of rb * no_of_timeslots

    # other attributes of ran_environment
    self.state = None
    self.sim_param = sim_param


  def step(self, action):
    #assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
    slices = self.slices
    #slice_results = self.slice_results

    # assign resources depending on action
    RB_mapping = self.SD_RAN_Controller.RB_allocate_from_action(slices[0].sim_state.now, slices, action)

    # simulate one round
    for i in range(len(slices)):
        slices[i].prep_next_round(RB_mapping[i, :, :])
        slices[i].simulate_one_round()
        #slice_results[i].append(slices[i].simulate_one_round())

    # get next state
    for i in range(len(slices)):
        tmp_state = 0
        for srv in slices[i].server_list:
            tmp_state += srv.get_queue_length()
        self.state[i]=tmp_state

    # check done
    if slices[0].sim_state.now == self.sim_param.T_FINAL:
        done = 1
    else:
        done = 0
    done = bool(done)

    # calculate reward
    reward_arr = np.zeros(len(slices))
    for i in range(len(slices)):
        reward_arr[i] = slices[i].slice_result.mean_throughput/ self.sim_param.P_SIZE

    reward = reward_arr
    return np.array(self.state), reward, done, {}

  def reset(self, parameters=None):
      # insert parameters to sim_param
      self.sim_param.SEED_IAT = parameters.SEED_IAT
      self.sim_param.SEED_SHADOWING = parameters.SEED_SHADOWING

      # create result directories and logfile
      log_file = create_dir(self.sim_param)

      # initialize SD_RAN_Controller
      self.SD_RAN_Controller = Controller(self.sim_param)

      # initialize all slices
      #self.slices, self.slice_results = initialize_slices(self.sim_param, log_file)
      self.slices = initialize_slices(self.sim_param, log_file)

      self.state = np.array([0,0,0])
      return np.array(self.state)

  def plot(self):
    sim_param = self.sim_param
    slices = self.slices
    #slice_results = self.slice_results
    no_of_slices = sim_param.no_of_slices
    no_of_users_per_slice = sim_param.no_of_users_per_slice

    # Store Simulation Results
    # user results
    parent_dir = "results/" + sim_param.timestamp + "/user_results"
    for i in range(len(slices)):
        tmp_slice_result = slices[i].slice_result
        user_count = len(tmp_slice_result.server_results)  # choose latest result for data
        for k in range(user_count):
            common_name = "/slice%d_user%d_" % (i, tmp_slice_result.server_results[k].server.user.user_id)
            cc_temp = tmp_slice_result.server_results[k].server.counter_collection

            # avg results
            filename = parent_dir + "/average_results" + common_name + "avg_data.csv"
            df = tmp_slice_result.server_results[k].df
            df.to_csv(filename, header=True)
            # tp
            filename = parent_dir + "/tp" + common_name + "tp_data.csv"
            df = DataFrame(np.array([cc_temp.cnt_tp.timestamps, cc_temp.cnt_tp.values, cc_temp.cnt_tp.sum_power_two]),
                           index=['Timestamps','Values','SumPowerTwo'])
            df.to_csv(filename, header=False)
            # tp2
            filename = parent_dir + "/tp2" + common_name + "tp2_data.csv"
            df = DataFrame(np.array([cc_temp.cnt_tp2.timestamps, cc_temp.cnt_tp2.values, cc_temp.cnt_tp2.sum_power_two]),
                           index=['Timestamps','Values','SumPowerTwo'])
            df.to_csv(filename, header=False)
            # ql
            filename = parent_dir + "/ql" + common_name + "ql_data.csv"
            df = DataFrame(np.array([cc_temp.cnt_ql.timestamps, cc_temp.cnt_ql.values, cc_temp.cnt_ql.sum_power_two]),
                           index=['Timestamps','Values','SumPowerTwo'])
            df.to_csv(filename, header=False)
            # system time (delay)
            filename = parent_dir + "/delay" + common_name + "delay_data.csv"
            df = DataFrame(np.array([cc_temp.cnt_syst.timestamps, cc_temp.cnt_syst.values]),
                           index=['Timestamps','Values'])
            df.to_csv(filename, header=False)
            # Find how to insert histograms

    # slice results
    parent_dir = "results/" + sim_param.timestamp + "/slice_results"
    for i in range(len(slices)):
        common_name = "/slice%d_" % i
        # avg results
        filename = parent_dir + "/average_results" + common_name + "avg_data.csv"
        df = slices[i].slice_result.df
        df.to_csv(filename, header=True)

    # Store Slice manager allocation dataframe
    parent_dir = "results/" + sim_param.timestamp + "/sm"
    for i in range(len(slices)):
        common_name = "/slice%d_" % i
        # avg results
        filename = parent_dir + common_name + "rb_allocation.csv"
        df = slices[i].slice_manager.df
        df.to_csv(filename, header=True)

    '''# plot results
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

        print("Slice %d dist: " % s.slice_param.SLICE_ID, *np.round(np.divide(rb_dist_slice, slicesum / 100), 1))
        # write these to file savetxt(filename, cc_temp.cnt_ql.sum_power_two, delimiter=',')
        rb_dist.append(slicesum)
    totalsum = np.nansum(rb_dist)
    print("rb dist (RR MCQI PF): ", *np.round(np.divide(rb_dist, totalsum / 100), 1))
    '''

def render(self, mode='human', close=False):
    ...