from stable_baselines3.common.evaluation import evaluate_baseline, evaluate_policy
import gym
import gym_ransim
from utils import make_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import A2C
import copy

# parameters
log_dir = 'logs/a2c/ransim-v0_Test'
env_kwargs = {'t_final':1000}
n_eval_episodes = 1
seed = 0
# C_ALGO = 'MCQI'
plot_results = True
#
# eval_env_list = []
eval_env_list = list(DummyVecEnv([make_env('ransim-v0', 0, seed, log_dir=log_dir, env_kwargs=env_kwargs)]) for _ in range(5))

# model = A2C.load("best_model", env=eval_env)
# model = A2C('MlpPolicy', eval_env_list[0], verbose=1)
# model.learn(total_timesteps = 1000)
# episode_rewards, episode_lengths = evaluate_policy(model,  eval_env_list[1],
#                                                                n_eval_episodes=n_eval_episodes,
#                                                                render=False,
#                                                                deterministic=True,
#                                                                return_episode_rewards=True,
#                                                                plot_before_reset=plot_results,
#                                                                env_seed= seed)
episode_rewards, episode_lengths = evaluate_baseline(env=eval_env_list[2],
                                                                C_ALGO='MCQI',
                                                                n_eval_episodes=n_eval_episodes,
                                                                render=False,
                                                                deterministic=True,
                                                                return_episode_rewards=True,
                                                                plot_before_reset=plot_results,
                                                               env_seed= seed)

episode_rewards, episode_lengths = evaluate_baseline(env=eval_env_list[3],
                                                                C_ALGO='RR',
                                                                n_eval_episodes=n_eval_episodes,
                                                                render=False,
                                                                deterministic=True,
                                                                return_episode_rewards=True,
                                                                plot_before_reset=plot_results,
                                                               env_seed= seed)

episode_rewards, episode_lengths = evaluate_baseline(env=eval_env_list[4],
                                                                C_ALGO='PF',
                                                                n_eval_episodes=n_eval_episodes,
                                                                render=False,
                                                                deterministic=True,
                                                                return_episode_rewards=True,
                                                                plot_before_reset=plot_results,
                                                               env_seed= seed)

