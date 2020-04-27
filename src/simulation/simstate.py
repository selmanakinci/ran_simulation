class SimState(object):

    """
    SimState contains the basic simulation state.

    It contains the current time and a stop flag, indicating whether the simulation is still running.
    Furthermore, it contains the number of blocked (dropped) packets and the number of total packets.
    """

    def __init__(self):
        """
        Generate SimState objects and initialize variables.
        """
        self.now = 0
        self.t_round_start = 0
        self.stop = False
        #self.num_packets = 0
        #self.num_blocked_packets = 0

    def prep_next_round(self):
        """
        Simstate is prepared for the next round
        """
        self.stop = False
