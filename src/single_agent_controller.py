import numpy as np
import gym
from torch_actor_critic_discrete import Agent
import matplotlib.pyplot as plt
from utils import plotLearning
from gym import wrappers
import gym_ransim
import time
from simparam import SimParam

#if __name__ == '__main__':
def main(alpha, beta, gamma):


    sim_param = SimParam()
    no_of_slices = sim_param.no_of_slices
    no_of_users_per_slice = sim_param.no_of_users_per_slice
    no_of_rb =  len(sim_param.RB_pool)
    no_of_timeslots = int(sim_param.T_C / sim_param.T_S)

    # state space :
    n_states = no_of_slices * no_of_users_per_slice * no_of_rb * no_of_timeslots
    # action space : #_slices ^ #_rb
    n_actions = no_of_slices ** no_of_rb
    agent = Agent(alpha=alpha, beta=beta, input_dims=[n_states], gamma=gamma,
                  n_actions=n_actions, layer1_size=32, layer2_size=32)

    env = gym.make('ransim-v0')

    # run baseline algorithm
    baseline_score = 0
    done = False
    observation = env.reset()
    while not done:
        action = 'baseline'
        observation_, reward, done, info = env.step(action)
        if done:
            env.plot()
        observation = observation_
        baseline_score += reward
    print('baseline score: %.3f' % baseline_score)

    score_history = []
    score = 0
    num_episodes = 5000
    t0 = time.time()
    for i in range(num_episodes):
        t_tmp = time.time()

        done = False
        score = 0

        # insert parameters
        class Parameters:
            pass
        parameters = Parameters()
        parameters.SEED_IAT = 0
        parameters.SEED_SHADOWING = 0
        if (i%1000 ==0):
            NO_logging = 0
        else:
            NO_logging = 1

        observation = env.reset(parameters, NO_logging)


        while not done:
            action = agent.choose_action(observation)
            observation_, reward, done, info = env.step(action)

            if done & (i%1000 ==0):
                env.plot()

            agent.learn(observation, reward, observation_, done)

            observation = observation_
            score += reward#.sum()

        score_history.append(score)
        elapsed_time = time.time() - t_tmp
        print('episode: ', i,'score: %.3f  time: %d' % (score,elapsed_time))

    print(time.time()-t0)
    filename = 'results/result_alpha_%.4f_beta_%.4f_gamma_%.2f.png' %(alpha, beta, gamma)
    #filename = 'cartpole-discrete-actor-critic-alpha0001-beta0005-32x32fc-1500games.png'
    plotLearning(score_history, filename=filename, window=10)


if __name__ == '__main__':
    alpha = 0.0001
    beta = 0.0005
    gamma = 0.99
    main(alpha, beta, gamma)