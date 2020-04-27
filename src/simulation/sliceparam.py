class SliceParam(object):
    """
    Contains all important simulation parameters
    """

    def __init__(self, sim_param, S = 10):

        # Slice ID
        self.SLICE_ID = 1

        # current buffer spaces and minimal buffer spaces
        self.S = S  # max buffer length in packets

        # serve packets continuously or start on the next slot
        self.cts_service = sim_param.cts_service
        # slice manager skips if buffer is empty
        self.buffer_check = sim_param.buffer_check

        # Timestamp for plots
        self.timestamp = sim_param.timestamp

        # Packet properties
        self.P_SIZE = sim_param.P_SIZE  # in bits

        # inter-arrival-time, simulation time and local_scheduler granularity in ms
        self.T_SM = sim_param.T_SM
        self.T_S = sim_param.T_S
        self.T_C = sim_param.T_C

        # Scheduling Algorithm
        self.SM_ALGO = 'PF'   # 'PF': prop fair, 'MCQI': Max Channel Quality Index, 'RR': round-robin

        # Prop. Fair Scheduling constant
        self.ALPHA_SM = .1

        # assigned resource blocks
        self.RB_pool = sim_param.RB_pool

        # set seed for random number generation
        self.SEED_IAT = 0

        # set desired utilization (rho)
        # self.RHO = .5

        # set confidence level and interval width
        # self.ALPHA = .05
        # self.EPSILON = .0015

    def print_sim_config(self):
        """
        Print a basic system configuration string.
        """
        print("Simulation with parameters: T_SIM = " + str(self.SIM_TIME) + ", S = " + str(self.S))