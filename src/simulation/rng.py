import math
from random import Random
import numpy as np
import matplotlib.pyplot as plt


class RNG(object):
    
    """
    Class RNG contains two random number streams, one for IAT and one for ST.

    Both RNS can be set during initialization or separately. The next random numbers are generated by the functions
    get_iat() or get_st().
    """
    
    def __init__(self, rns, s_type):
        """
        Initialize a RNG object with two RNS given.
        :param s_type = 'iat': rns: represents the RNS for the inter-arrival times.
        :param s_type = 'cg': rns: represents the RNS for the channel gains.
        """
        if s_type == 'iat':
            self.iat_rns = rns
        elif s_type == 'cg':
            self.cg_rns = rns
        elif s_type == 'dist':
            self.dist_rns = rns
        elif s_type == 'shadowing':
            self.shadowing_rns = rns
        elif s_type == 'rb_allocation':
            self.rb_rns = rns
    
    # def set_iat_rns(self, rns):
    #     """
    #     Set a new RNS for the inter-arrival times.
    #     """
    #     self.iat_rns = rns
    #
    # def set_cg_rns(self, rns):
    #     """
    #     Set a new RNS for the channel gains.
    #     """
    #     self.cg_rns = rns
    #
    # def set_dist_rns(self, rns):
    #     """
    #     Set a new RNS for the user distance.
    #     """
    #     self.dist_rns = rns

    def get_iat(self):
        """
        Return a new sample of the IAT RNS
        """
        return self.iat_rns.next()#*1000

    def get_cg(self, m, n):
        """
        Return a new sample of the CG RNS
        """
        channel_gains = np.zeros((m,n))
        for i in range(m):
            for j in range(n):
                channel_gains[i][j] = self.cg_rns.next()
        return channel_gains

    def get_dist(self):
        """
        Return a new sample of the Dist RNS
        """
        return self.dist_rns.next()

    def get_rb(self):
        """
        Return a new sample of the Dist RNS
        """
        return self.rb_rns.next()

    def get_shadowing(self, t_final):
        """
        Return a new sample of the Shadowing RNS
        """
        shadowing = np.zeros(t_final)
        for i in range(t_final):
            shadowing[i] = self.shadowing_rns.next()

        # # Plot histogram of shadowing
        # count, bins, ignored = plt.hist(shadowing, 30, normed=True)
        # sigma = self.shadowing_rns.sigma
        # mu = self.shadowing_rns.mu
        # plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (bins - mu)**2 / (2 * sigma**2)), linewidth=2, color='r')
        # plt.show()

        return shadowing

    def get_shadowing2(self, t_final, t_c, t_coh, buffer):
        """
        Return a new sample of the Shadowing RNS
        """
        no_of_frames = int(t_final/t_coh) + buffer


        shadowing_per_t_coh = np.zeros(no_of_frames)
        for i in range(no_of_frames):
            shadowing_per_t_coh[i] = self.shadowing_rns.next()
        shadowing_per_ms = np.repeat(shadowing_per_t_coh, t_coh)
        start_idx = self.shadowing_rns.r.randint(0, (t_coh / t_c)-1) * t_c
        shadowing = shadowing_per_ms[start_idx:-(t_coh-start_idx)]


        # # Plot histogram of shadowing
        # count, bins, ignored = plt.hist(shadowing, 30, normed=True)
        # sigma = self.shadowing_rns.sigma
        # mu = self.shadowing_rns.mu
        # plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *np.exp( - (bins - mu)**2 / (2 * sigma**2)), linewidth=2, color='r')
        # plt.show()

        return shadowing

class RNS(object):
    
    """
    Basic abstract class for random number streams.

    To be implemented in subclass.
    Contains a Random class r in order to allow different seeds for different RNS
    """

    def __init__(self, the_seed=None):
        """
        Initialize the general RNS with an optional seed.
        All further initialization is done in subclass.
        """
        self.r = Random(the_seed)

    def set_parameters(self, *args):
        NotImplementedError("Implement in subclass")

    def next(self):
        """
        Method should be overwritten in subclass.
        """
        return 0
    

class ExponentialRNS(RNS):
    
    """
    Class to provide exponentially distributed random numbers. After initialization, new numbers can be generated
    using next(). Initialization with given lambda and optional seed.
    :param lambda_x: the inverse of the mean of the exponential distribution
    :param the_seed: optional seed for the random number stream
    """
    
    def __init__(self, lambda_x, the_seed=None):
        """
        Initialize Exponential RNS and set the parameters.
        """
        super(ExponentialRNS, self).__init__(the_seed)
        self.mean = 0
        self.set_parameters(lambda_x)
        
    def set_parameters(self, lambda_x):
        """
        Set parameter lambda, hence the mean of the exponential distribution.
        """
        self.mean = 1./float(lambda_x)
        
    def next(self):
        """
        Generate the next random number using the inverse transform method.
        """
        return -math.log(self.r.random()) * self.mean


class UniformIntRNS(RNS):

    """
    Class to provide exponentially distributed random numbers. After initialization, new numbers can be generated
    using next(). Initialization with upper and lower bound and optional seed.
    :param a: the lower bound of the uniform distribution
    :param b: the upper bound of the uniform distribution
    :param the_seed: optional seed for the random number stream
    """

    def __init__(self, a, b, the_seed=None):
        """
        Initialize Uniform RNS and set the parameters.
        """
        super(UniformIntRNS, self).__init__(the_seed)
        self.lower_bound = a
        self.upper_bound = b

    def next(self):
        """
        Generate the next random number using the inverse transform method.
        """
        return self.r.randint(self.lower_bound, self.upper_bound)

class UniformRNS(RNS):

    """
    Class to provide exponentially distributed random numbers. After initialization, new numbers can be generated
    using next(). Initialization with upper and lower bound and optional seed.
    :param a: the lower bound of the uniform distribution
    :param b: the upper bound of the uniform distribution
    :param the_seed: optional seed for the random number stream
    """

    def __init__(self, a, b, the_seed=None):
        """
        Initialize Uniform RNS and set the parameters.
        """
        super(UniformRNS, self).__init__(the_seed)
        self.upper_bound = a
        self.lower_bound = b
        self.width = self.upper_bound - self.lower_bound

    def set_parameters(self, a, b):
        """
        Set parameters a and b, the upper and lower bound of the distribution
        """
        self.upper_bound = a
        self.lower_bound = b
        self.width = self.upper_bound - self.lower_bound

    def next(self):
        """
        Generate the next random number using the inverse transform method.
        """
        return self.lower_bound + self.width * self.r.random()


class NormalRNS(RNS):
    """
    Class to provide exponentially distributed random numbers. After initialization, new numbers can be generated
    using next(). Initialization with upper and lower bound and optional seed.
    :param a: the lower bound of the uniform distribution
    :param b: the upper bound of the uniform distribution
    :param the_seed: optional seed for the random number stream
    """

    def __init__(self, mean, variance, the_seed=None):
        """
        Initialize Uniform RNS and set the parameters.
        """
        super(NormalRNS, self).__init__(the_seed)
        self.mu = mean
        self.sigma = variance

    def set_parameters(self, mean, variance):
        """
        Set parameters a and b, the upper and lower bound of the distribution
        """
        self.mu = mean
        self.sigma = variance

    def next(self):
        """
        Generate the next random number using the inverse transform method.
        """
        return self.r.gauss(self.mu, self.sigma)