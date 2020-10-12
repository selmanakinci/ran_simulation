from datetime import datetime


class SimParam(object):
    """
    Contains all important simulation parameters
    """

    def __init__(self, t_final: int = 1000):

        # initial parameters
        self.no_of_slices = 3
        #self.no_of_users_per_slice = 10
        self.no_of_users_list = (10, 10, 10)
        self.max_no_of_users_per_slice = 10

        # requirements, packet size and iat
        self.delay_requirements = (30, 30, 30)  # ms
        self.rate_requirements = (1500, 1500, 1500) # kbps
        self.packet_sizes = (5000, 5000, 5000)  # in bits
        self.mean_iats = (2.5, 2.5, 2.5)  # in ms

        # Functional Flags
        self.cts_service = True  # serve packets continuously or start on the next slot
        self.buffer_check = True  # slice manager skips if buffer is empty
        self.freq_selective = True  # when false, shadowing is frequency flat

        # timestamp
        now = datetime.now()
        self.timestamp = now.strftime("%Y_%m_%d_%H%M%S")

        #self.P_SIZE = 6000 #1*1000*6  # 1kB in bits

        self.max_buffer_size = 10  # max buffer length in packets

        # inter-arrival-time, simulation time and local_scheduler granularity in ms
        #self.MEAN_IAT = 2    # mean inter arrival time in ms
        #self.MEAN_CG = 1        # mean channel gain value
        self.T_FINAL = t_final     # in ms
        self.T_C = 10        # controller period, round period
        self.T_SM = 1
        self.T_S = 1
        self.T_COH = 5 * self.T_C  # coherent time of the channel

        # Controller Algorithm
        self.C_ALGO = 'RL'  # 'H': Hard Slicing, 'RR': round robin, 'MCQI': max cqi, 'PF': prop. fair

        # Prop. Fair Scheduling constant for controller
        self.ALPHA_C = .1

        # all resource blocks
        self.RB_pool = list(range(25))

        # Channel Model Parameters from selected paper
        self.FREQ = 2*1e9  # 2GHz
        self.PL_Exponent = 3.0
        self.P_TX_dBm = 20   # in dBm
        self.DIST_MIN = 30#30   # in meter
        self.DIST_MAX = 100#60  # in meter
        self.SIGMA_shadowing = 6.8  # in dB
        self.TEMPERATURE = 293  # kelvin
        self.RB_BANDWIDTH = 180*1e3  # 180kHz

        # set seed for random number generation
        # self.SEED_CG = 0
        #self.SEED_SHADOWING = 0
        #self.SEED_IAT = 0
        self.SEED_OFFSET = 0

    def update_seeds(self, new_seed=0):
        self.SEED_OFFSET = new_seed
        #self.SEED_DIST = self.SEED_OFFSET
        #self.SEED_SHADOWING = new_seed  # 0
        #self.SEED_IAT = self.SEED_SHADOWING + (self.no_of_slices*self.no_of_users_per_slice*len(self.RB_pool))# 0

    '''def SimParam(self):
        """
        Print a basic system configuration string.
        """
        print("Simulation with parameters: T_SIM = " + str(self.T_C) + ", S = " + str(self.S))'''

    def update_timestamp(self):
        # timestamp
        now = datetime.now()
        self.timestamp = now.strftime("%Y_%m_%d_%H%M%S")
        self.timestamp = self.timestamp + '_' + self.C_ALGO  #  adding c_algo to result folder