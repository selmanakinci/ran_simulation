import gym
from gym import error, spaces, utils, logger
from gym.utils import seeding

from counter import TimeIndependentCounter
from slicesimulation import SliceSimulation
from trafficgenerator import TrafficGenerator
from sliceparam import SliceParam
from simparam import SimParam
from user import User
from controller import Controller
from datetime import datetime
from createdirectory import create_dir
from numpy import savetxt
import numpy as np
from rng import RNG, ExponentialRNS, UniformRNS
from pandas import DataFrame

class RanSimEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    """
    Main ran_simulation
    """


    # define sim_param and inside RB pool: all available Resources list
    sim_param = SimParam()

    no_of_slices = sim_param.no_of_slices
    no_of_users_per_slice = sim_param.no_of_users_per_slice

    # create result directories
    create_dir(sim_param.timestamp)

    # create logfile and write SimParameters
    results_dir = "results/" + sim_param.timestamp
    log_file = open(results_dir + "/logfile.txt", "wt")
    log_file.write('no_of_slices: %d\nno_of_users_per_slice: %d\n\n' % (no_of_slices, no_of_users_per_slice))
    attrs = vars(sim_param)
    log_file.write('SimParam\n'+''.join("%s: %s\n" % item for item in attrs.items()))
    # log_file.close()

    # initialize SD_RAN_Controller
    SD_RAN_Controller = Controller(sim_param)

    # Each slice has different users
    slices = []
    slice_results = []

    # initialize all slices
    for i in range(no_of_slices):
        slice_param_tmp = SliceParam(sim_param)
        slice_param_tmp.SLICE_ID = i
        slices.append(SliceSimulation(slice_param_tmp, False))
        slice_results.append([])

        # initialize all users with traffics and distances
        tmp_users = []
        seed_dist = 0  # users in all slices have identical distance distributions
        #rng_dist = RNG(ExponentialRNS(lambda_x=1. / float(sim_param.MEAN_Dist)), s_type='dist') # , the_seed=seed_dist
        rng_dist = RNG(UniformRNS(sim_param.DIST_MIN,sim_param.DIST_MAX, the_seed=seed_dist), s_type='dist')  #
        dist_arr = [10, 100 ]#[30, 30, 100, 100, 100, 100, 100, 100, 100, 100]  # 10*(1+user_id%no_of_users_per_slice)**2
        for j in range(no_of_users_per_slice):
            user_id = i*no_of_users_per_slice + j
            #tmp_users.append(User(user_id, rng_dist.get_dist(), slice_list=[slices[i]], sim_param=sim_param))
            tmp_users.append(User(user_id, dist_arr[j], slice_list=[slices[i]], sim_param=sim_param))

        # insert user to slices
        slices[i].insert_users(tmp_users)


    # Choose Slice Manager Algorithm, 'PF': prop fair, 'MCQI': Max Channel Quality Index, 'RR': round-robin
    slices[0].slice_param.SM_ALGO = 'RR'
    slices[1].slice_param.SM_ALGO = 'MCQI'
    slices[2].slice_param.SM_ALGO = 'PF'

    # log Slice Parameters
    for i in range(no_of_slices):
        attrs = vars(slices[i].slice_param)
        log_file.write('\nSliceParam\n' + ''.join("%s: %s\n" % item for item in attrs.items()))
    log_file.close()

    # Angle limit set to 2 * theta_threshold_radians so failing observation is still within bounds
    high = np.array([9, 9, 9])
    low = np.array([0, 0, 0])

    self.action_space = spaces.Discrete(2)
    self.observation_space = spaces.Box(low, high, dtype=np.float32)
    self.state = None
    self.slices = slices

  def step(self, action):
    assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
    #state = self.state
    # run simulation one Ts


    # check state:
    # get next state
    slices = self.slices
    for i in range(len(slices)):
        tmp_state = 0
        for srv in slices[i].server_list:
            tmp_state += srv.get_queue_length()
        self.state[i]=tmp_state


    # check done
    done = 0
    done = bool(done)

    # check reward
    if not done:
        reward = 1.0
    elif self.steps_beyond_done is None:
        # Pole just fell!
        self.steps_beyond_done = 0
        reward = 1.0
    else:
        if self.steps_beyond_done == 0:
            logger.warn(
                "You are calling 'step()' even though this environment has already returned done = True. You should always call 'reset()' once you receive 'done = True' -- any further steps are undefined behavior.")
        self.steps_beyond_done += 1
        reward = 0.0


    return np.array(self.state), reward, done, {}

  def reset(self):
      self.state = np.array([0,0,0])
      #self.steps_beyond_done = None

      return np.array(self.state)

  def render(self, mode='human', close=False):
    ...