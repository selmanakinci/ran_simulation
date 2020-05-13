import numpy as np
import gym
from torch_actor_critic_discrete import Agent
import matplotlib.pyplot as plt
from utils import plotLearning
from gym import wrappers
import gym_ransim


#if __name__ == '__main__':
def main(alpha, beta, gamma):

    no_of_rb = 20
    no_of_slices = 3

    agent0 = Agent(alpha=alpha, beta=beta, input_dims=[no_of_slices], gamma=gamma,
                  n_actions=no_of_rb, layer1_size=32, layer2_size=32)
    agent1 = Agent(alpha=alpha, beta=beta, input_dims=[no_of_slices], gamma=gamma,
                  n_actions=no_of_rb, layer1_size=32, layer2_size=32)
    agent2 = Agent(alpha=alpha, beta=beta, input_dims=[no_of_slices], gamma=gamma,
                  n_actions=no_of_rb, layer1_size=32, layer2_size=32)

    #env = gym.make('CartPole-v1')
    env = gym.make('ransim-v0')
    score_history = []
    score = 0
    num_episodes = 3
    for i in range(num_episodes):
        print('episode: ', i,'score: %.3f' % score)

        #if i>1000:
        #    env = wrappers.Monitor(env, "tmp/cartpole-untrained",np.sum(action,axis=1)
        #                                video_callable=lambda episode_id: True, force=True)

        done = False
        score = 0

        # insert parameters
        class Parameters:
            pass
        parameters = Parameters()
        parameters.SEED_IAT = i
        parameters.SEED_SHADOWING = i
        observation = env.reset(parameters)


        while not done:
            action0 = agent0.choose_action(observation)
            action1 = agent1.choose_action(observation)
            action2 = agent2.choose_action(observation)
            action = [[action0], [action1], [action2]]

            observation_, reward, done, info = env.step(action)

            agent0.learn(observation, reward[0], observation_, done)
            agent1.learn(observation, reward[1], observation_, done)
            agent2.learn(observation, reward[2], observation_, done)

            observation = observation_
            score += reward.sum()
        ####

        score_history.append(score)

    filename = 'results/result_alpha_%.4f_beta_%.4f_gamma_%.2f.png' %(alpha, beta, gamma)
    #filename = 'cartpole-discrete-actor-critic-alpha0001-beta0005-32x32fc-1500games.png'
    plotLearning(score_history, filename=filename, window=10)


if __name__ == '__main__':
    alpha = 0.0001
    beta = 0.0005
    gamma = 0.99
    main(alpha, beta, gamma)