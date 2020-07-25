from counter import TimeIndependentCrosscorrelationCounter, TimeIndependentAutocorrelationCounter
from counter import TimeIndependentCounter, TimeDependentCounter
from histogram import TimeIndependentHistogram, TimeDependentHistogram


class CounterCollection(object):

    """
    CounterCollection is a collection of all counters and histograms that are used in the simulations.

    It contains several counters and histograms, that are used in the different tasks.
    Reporting is done by calling the report function. This function can be adapted, depending on which counters should
    report their results and print strings or plot histograms.
    """

    def __init__(self, server):
        """
        Initialize the counter collection.
        :param sim: the simulation, the CounterCollection belongs to.
        """
        self.server = server
        #self.sim = server.slicesim

        # waiting time
        #self.cnt_wt = TimeIndependentCounter(self.server)
        #self.hist_wt = TimeIndependentHistogram(self.server, "w")
        #self.acnt_wt = TimeIndependentAutocorrelationCounter("waiting time with lags 1 to 20", max_lag=20)

        # system time(delay)
        self.cnt_syst = TimeIndependentCounter(self.server)
        self.hist_syst = TimeIndependentHistogram(self.server, "s")

        # queue length
        self.cnt_ql = TimeDependentCounter(self.server)
        self.hist_ql = TimeDependentHistogram(self.server, "q")

        # throughput
        self.cnt_tp = TimeDependentCounter(self.server, 'tp')
        self.cnt_tp2 = TimeDependentCounter(self.server, 'tp2')

        # system utilization
        #self.cnt_sys_util = TimeDependentCounter(self.server)

        # blocking probability
        #self.cnt_bp = TimeIndependentCounter(self.server, "bp")
        #self.hist_bp = TimeIndependentHistogram(self.server, "bp")

        # cross correlations
        #self.cnt_iat_wt = TimeIndependentCrosscorrelationCounter("inter-arrival time vs. waiting time")
        #self.cnt_iat_st = TimeIndependentCrosscorrelationCounter("inter-arrival time vs. service time")
        #self.cnt_iat_syst = TimeIndependentCrosscorrelationCounter("inter-arrival time vs. system time")
        #self.cnt_st_syst = TimeIndependentCrosscorrelationCounter("service time vs. system time")

    def reset(self):
        """
        Resets all counters and histograms.
        """
        #self.cnt_wt.reset()
        #self.hist_wt.reset()
        #self.acnt_wt.reset()

        self.cnt_syst.reset()
        self.hist_syst.reset()

        self.cnt_ql.reset()
        self.hist_ql.reset()

        self.cnt_tp.reset()

        #self.cnt_sys_util.reset()

        #self.cnt_bp.reset()
        #self.hist_bp.reset()

        #self.cnt_iat_wt.reset()
        #self.cnt_iat_st.reset()
        #self.cnt_iat_syst.reset()
        #self.cnt_st_syst.reset()
    
    def report(self, filename=''):
        """
        Calls the report function of the counters and histograms.
        Can be adapted, such that not all reports are printed
        """
        #self.cnt_wt.report(filename)
        #self.hist_wt.report(filename)
        #self.acnt_wt.report()

        self.cnt_syst.report(filename)
        self.hist_syst.report(filename)

        self.cnt_ql.report(filename)
        self.hist_ql.report(filename)

        self.cnt_tp.report(filename)

        #self.cnt_sys_util.report()

        #self.cnt_iat_wt.report()
        #self.cnt_iat_st.report()
        #self.cnt_iat_syst.report()
        #self.cnt_st_syst.report()

    def count_throughput(self, throughput):
        """
        Count a throughput. Its data is counted by the various counters
        tp in bits per second
        """
        self.cnt_tp.count(throughput)

    def count_throughput2(self, throughput):
        """
        Count a throughput. Its data is counted by the various counters
        tp in bits per second
        """
        self.cnt_tp2.count(throughput)

    def count_packet(self, packet):
        """
        Count a packet. Its data is counted by the various counters
        """
        #self.cnt_wt.count(packet.get_waiting_time())
        #self.hist_wt.count(packet.get_waiting_time())
        #self.acnt_wt.count(packet.get_waiting_time())

        self.cnt_syst.count(packet.get_system_time())
        self.hist_syst.count(packet.get_system_time())

        #self.cnt_iat_wt.count(packet.get_interarrival_time(), packet.get_waiting_time())
        #self.cnt_iat_st.count(packet.get_interarrival_time(), packet.get_service_time())
        #self.cnt_iat_syst.count(packet.get_interarrival_time(), packet.get_system_time())
        #self.cnt_st_syst.count(packet.get_service_time(), packet.get_system_time())

    def count_queue(self):
        """
        Count the number of packets in the buffer and add the values to the corresponding (time dependent) histogram.
        This function should be called at least whenever the number of packets in the buffer changes.

        The system utilization is counted as well and can be counted from the counter cnt_sys_util.
        """
        self.cnt_ql.count(int(self.server.get_queue_length()))
        self.hist_ql.count(self.server.get_queue_length())

        #if self.server.server_busy:
            #self.cnt_sys_util.count(1)
            #self.cnt_tp.count(self.server.served_packet.get_output_rate())
        #else:
            #self.cnt_sys_util.count(0)
