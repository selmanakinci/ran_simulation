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
    assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
    slices = self.slices
    slice_results = self.slice_results

    # assign resources depending on action
    RB_mapping = self.SD_RAN_Controller.RB_allocate_from_action(slices[0].sim_state.now, slices, action)

    # simulate one round
    for i in range(len(slices)):
        slices[i].prep_next_round(RB_mapping[i, :, :])
        slice_results[i].append(slices[i].simulate_one_round())

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
    reward_arr = np.zeros(len(slice_results))
    for i in range(len(slice_results)):
        reward_arr[i] = slice_results[i][0].mean_throughput

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
      self.slices, self.slice_results = initialize_slices(self.sim_param, log_file)

      self.state = np.array([0,0,0])
      return np.array(self.state)

  def plot(self):
    sim_param = self.sim_param
    slices = self.slices
    slice_results = self.slice_results
    no_of_slices = sim_param.no_of_slices
    no_of_users_per_slice = sim_param.no_of_users_per_slice

    # Store Simulation Results
    # user results
    parent_dir = "results/" + sim_param.timestamp + "/user_results"
    path = parent_dir + "/tp"
    for i in range(len(slice_results)):
        user_count = len(slice_results[i][-1].server_results)  # choose latest result for data
        for k in range(user_count):
            common_name = "/slice%d_user%d_" % (i, slice_results[i][-1].server_results[k].server.user.user_id)
            cc_temp = slice_results[i][-1].server_results[k].counter_collection
            # tp
            filename = parent_dir + "/tp" + common_name + "sum_power_two.csv"
            savetxt(filename, cc_temp.cnt_tp.sum_power_two, delimiter=',')
            filename = parent_dir + "/tp" + common_name + "values.csv"
            savetxt(filename, cc_temp.cnt_tp.values, delimiter=',')
            filename = parent_dir + "/tp" + common_name + "timestamps.csv"
            savetxt(filename, cc_temp.cnt_tp.timestamps, delimiter=',')

            filename = parent_dir + "/tp" + common_name + "all_data.csv"
            # savetxt(filename, np.transpose(np.array([cc_temp.cnt_tp.values,cc_temp.cnt_tp.timestamps])), delimiter=',')
            df = DataFrame(np.transpose(np.array([cc_temp.cnt_tp.values, cc_temp.cnt_tp.timestamps])),
                           columns=['Values', 'Timestamps'])
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

        print("Slice %d dist: " % s.slice_param.SLICE_ID, *np.round(np.divide(rb_dist_slice, slicesum / 100), 1))
        # write these to file savetxt(filename, cc_temp.cnt_ql.sum_power_two, delimiter=',')
        rb_dist.append(slicesum)
    totalsum = np.nansum(rb_dist)
    print("rb dist (RR MCQI PF): ", *np.round(np.divide(rb_dist, totalsum / 100), 1))


def render(self, mode='human', close=False):
    ...