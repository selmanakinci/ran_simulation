from stable_baselines3.common.evaluation import evaluate_baseline, evaluate_policy
import gym
import gym_ransim
from utils import make_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3 import A2C
import copy

# parameters
log_dir = 'logs/a2c/ransim-v0_Test_Sim_user_no_adaptation'
env_kwargs = {'t_final':1000}
n_eval_episodes = 1
plot_results = True

# set no_of_user_list
user_list_list = []
for i in range(6):      # no or runs and user list conditions
    if i < 2:          user_list_list.append((5, 5, 5))
    elif i < 4:        user_list_list.append((10, 5, 5))
    else:              user_list_list.append ((5, 5, 5))

# eval_env_list = list(DummyVecEnv([make_env('ransim-v0', 0, seed, log_dir=log_dir, env_kwargs=env_kwargs)]) for _ in range(5))
#model = A2C.load("best_model", env=eval_env)

# for i in range (10):
#     seed = i
#     eval_env = DummyVecEnv ([make_env ('ransim-v0', 0, seed, log_dir=log_dir, env_kwargs=env_kwargs)])
#     model = A2C.load ("best_model", env=eval_env)
#     episode_rewards, episode_lengths = evaluate_policy (model, eval_env,
#                                                         n_eval_episodes=n_eval_episodes,
#                                                         render=False,
#                                                         deterministic=False,
#                                                         return_episode_rewards=True,
#                                                         plot_before_reset=plot_results,
#                                                         env_seed=seed)

eval_env = DummyVecEnv ([make_env ('ransim-v0', 0, log_dir=log_dir, env_kwargs=env_kwargs)])
for i in range (len(user_list_list)):
    seed = i
    no_of_users_list=user_list_list[i]
    episode_rewards, episode_lengths = evaluate_baseline(env=eval_env,
                                                                    C_ALGO='Random',
                                                                    n_eval_episodes=n_eval_episodes,
                                                                    render=False,
                                                                    deterministic=True,
                                                                    return_episode_rewards=True,
                                                                    plot_before_reset=plot_results,
                                                                    env_seed= seed,
                                                                    no_of_users_list=no_of_users_list)

eval_env = DummyVecEnv ([make_env ('ransim-v0', 0, log_dir=log_dir, env_kwargs=env_kwargs)])
for i in range (len(user_list_list)):
    seed = i
    no_of_users_list=user_list_list[i]
    episode_rewards, episode_lengths = evaluate_baseline(env=eval_env,
                                                                    C_ALGO='MCQI',
                                                                    n_eval_episodes=n_eval_episodes,
                                                                    render=False,
                                                                    deterministic=True,
                                                                    return_episode_rewards=True,
                                                                    plot_before_reset=plot_results,
                                                                    env_seed= seed,
                                                                    no_of_users_list=no_of_users_list)


eval_env = DummyVecEnv ([make_env ('ransim-v0', 0, log_dir=log_dir, env_kwargs=env_kwargs)])
for i in range (len(user_list_list)):
    seed = i
    no_of_users_list=user_list_list[i]
    episode_rewards, episode_lengths = evaluate_baseline(env=eval_env,
                                                                    C_ALGO='RR',
                                                                    n_eval_episodes=n_eval_episodes,
                                                                    render=False,
                                                                    deterministic=True,
                                                                    return_episode_rewards=True,
                                                                    plot_before_reset=plot_results,
                                                                    env_seed= seed,
                                                                    no_of_users_list=no_of_users_list)

eval_env = DummyVecEnv ([make_env ('ransim-v0', 0, log_dir=log_dir, env_kwargs=env_kwargs)])
for i in range (len(user_list_list)):
    seed = i
    no_of_users_list=user_list_list[i]
    episode_rewards, episode_lengths = evaluate_baseline(env=eval_env,
                                                                    C_ALGO='PF',
                                                                    n_eval_episodes=n_eval_episodes,
                                                                    render=False,
                                                                    deterministic=True,
                                                                    return_episode_rewards=True,
                                                                    plot_before_reset=plot_results,
                                                                    env_seed= seed,
                                                                    no_of_users_list=no_of_users_list)