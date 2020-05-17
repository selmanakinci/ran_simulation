from datetime import datetime


class SimParam(object):
    """
    Contains all important simulation parameters
    """

    def __init__(self):

        # initial parameters
        self.no_of_slices = 3
        self.no_of_users_per_slice = 2

        # Functional Flags
        self.cts_service = True  # serve packets continuously or start on the next slot
        self.buffer_check = False  # slice manager skips if buffer is empty
        self.freq_selective = True  # when false, shadowing is frequency flat

        # timestamp
        now = datetime.now()
        self.timestamp = now.strftime("%Y_%m_%d_%H%M%S")

        # Packet properties# Read slice results for plotting comparison
        # path = "baseline comparison data/08-03-2020 cts_off"
        self.P_SIZE = 100*100#1*1000*8  # 1kB in bits

        self.max_buffer_size = 10 # max buffer length in packets

        # inter-arrival-time, simulation time and local_scheduler granularity in ms
        self.MEAN_IAT = 1     # mean inter arrival time
        #self.MEAN_CG = 1        # mean channel gain value
        self.T_FINAL = 2000     # in ms
        self.T_C = 1          # controller period, round period
        self.T_SM = 1
        self.T_S = 1

        # Controller Algorithm
        self.C_ALGO = 'MCQI'  # 'H': Hard Slicing, 'RR': round robin, 'MCQI': max cqi, 'PF': prop. fair

        # Prop. Fair Scheduling constant for controller
        self.ALPHA_C = .1

        # all resource blocks
        self.RB_pool = list(range(20))  # [0, 1, 2, 3, 4, 5]

        # Channel Model Parameters
        self.FREQ = 2*1e9  # 2GHz
        self.PL_Exponent = 3.0
        self.P_TX_dBm = 20   # in dBm  ????????????????????
        self.DIST_MIN = 10   # in meter
        self.DIST_MAX = 100  # in meter
        self.SIGMA_shadowing = 15#100#6.8  # in dB ??????????????????????????????????????????????????????????????????????????????????
        self.TEMPERATURE = 293  # kelvin
        self.RB_BANDWIDTH = 180000  # 180kHz

        # set seed for random number generation
        self.SEED_IAT = 0
        #self.SEED_CG = 0
        self.SEED_SHADOWING = 0

    def SimParam(self):
        """
        Print a basic system configuration string.
        """
        print("Simulation with parameters: T_SIM = " + str(self.T_C) + ", S = " + str(self.S))