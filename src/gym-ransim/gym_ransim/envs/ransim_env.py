import gym
from gym import error, spaces, utils
from gym.utils import seeding

class RanSimEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    ...
  def step(self, action):
    ...
  def reset(self):
    ...env = gym.make('CartPole-v1')
  def render(self, mode='human', close=False):
    ...