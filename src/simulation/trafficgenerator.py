from event import PacketArrival
import numpy as np
from rng import RNG, ExponentialRNS
import matplotlib.pyplot as plt


class TrafficGenerator(object):

    """

    """

    def __init__(self, user, no_seed=False):
        """
        Generate TrafficGenerator objects and initialize variables.
        """
        self.sim_param = user.sim_param
        seed_iat = (user.user_id % user.sim_param.no_of_users_per_slice) + user.sim_param.SEED_IAT
        self.rng = RNG(ExponentialRNS(1. / float(self.sim_param.MEAN_IAT), seed_iat), s_type='iat')

    def poisson_arrivals(self, slicesim):
        """

        """
        iat = self.sim_param.MEAN_IAT  # slicesim.slice_param.IAT
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
