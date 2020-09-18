from event import PacketArrival
import numpy as np
from rng import RNG, ExponentialRNS
import matplotlib.pyplot as plt


class TrafficGenerator(object):

    """

    """

    def __init__(self, user):
        """
        Generate TrafficGenerator objects and initialize variables.
        """
        self.sim_param = user.sim_param
        # self.seed_iat = (user.user_id % user.sim_param.no_of_users_per_slice) + user.sim_param.SEED_IAT
        self.seed_iat = user.user_id + user.sim_param.SEED_OFFSET

    def poisson_arrivals(self, slicesim):
        """

        """
        iat = slicesim.slice_param.MEAN_IAT
        self.rng = RNG (ExponentialRNS (1. / float(iat), self.seed_iat), s_type='iat')

        #iat = self.sim_param.MEAN_IAT
        t_start = slicesim.sim_state.now
        t_end = self.sim_param.T_FINAL

        # Poisson
        t_arr = []
        iat_arr = []
        t_temp = t_start+self.rng.get_iat()
        while t_temp < t_end:
            t_arr.append(t_temp)
            t_temp += self.rng.get_iat()
            if len(t_arr)>2:
                iat_arr.append(t_arr[-1]-t_arr[-2])

        # # Fixed IAT
        # t_arr = np.arange(t_start, t_end, iat)

        # # Plot histogram of interarrivals for poisson dist
        # count, bins, ignored = plt.hist(iat_arr, 30, normed=True)
        # lmda = 1/iat
        # plt.plot(bins, lmda * np.exp(- lmda*bins), linewidth=2, color='r')
        # plt.show()

        arrivals = []
        for i in t_arr:
            arrivals.append(PacketArrival(slicesim, i))

        return arrivals

    def periodic_arrivals(self, slicesim):
        """

        """
        iat = slicesim.slice_param.MEAN_IAT

        t_start = slicesim.sim_state.now
        t_end = self.sim_param.T_FINAL

        # Fixed IAT
        t_arr = np.arange(t_start, t_end, iat)

        arrivals = []
        for i in t_arr:
            arrivals.append(PacketArrival(slicesim, i))
        return arrivals
