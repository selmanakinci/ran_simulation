class Packet(object):

    """
    Packet represents a data packet processed by the DES.

    It contains variables for measurements, which include timestamps (arrival, service start, service completion)
    and the status of the packet (served, completed).
    """

    def __init__(self, slicesim, user, size=None, iat=None):
        """
        Initialize a packet with its arrival time and (optionally) the inter-arrival time w.r.t. the last packet.
        :param slicesim: simulation, the packet belongs to
        :param iat: inter-arrival time with respect to the last arrival
        :return: packet object
        """
        self.slicesim = slicesim
        self.user = user
        self.server = self.slicesim.server_list_dict[self.user.user_id]

        self.t_arrival = slicesim.sim_state.now
        #self.t_start = -1
        self.t_complete = -1
        self.d_wait = 0       # wait duration
        self.d_served = 0     # served duration

        #self.iat = iat
        self.size = size
        self.remaining_load = self.size

        self.t_finish_real = -1    # real completion estimation time
        self.t_finish = -1   # completion estimation time

        self.waiting = True
        self.served = False
        self.completed = False

    def start_service(self):
        """
        Change the status of the packet once the serving process starts.
        """
        self.waiting = False
        self.served = True
        self.server.counter_collection.count_throughput(0.)  # 0 throughput is added since before start, it was zero
        self.server.counter_collection.count_throughput2(0.)

        if self.slicesim.slice_param.cts_service:
            self.t_start = self.slicesim.sim_state.now
        else:
            if (self.slicesim.sim_state.now % self.slicesim.slice_param.T_S)==0:
                self.t_start = self.slicesim.sim_state.now
            else:
                self.t_start = int(round(self.slicesim.sim_state.now + self.slicesim.slice_param.T_S - (self.slicesim.sim_state.now % self.slicesim.slice_param.T_S)))  # starts on next slot

        t_system = self.t_start - self.t_arrival
        self.d_wait = self.d_wait + t_system - (self.d_wait+self.d_served)

        # calculate estimated and occupation durations
        self.user.channel.get_serving_duration(self)

    def pause_service(self):
        """
        Change the status of the packet once the serving process pauses.
        """
        self.waiting = True
        self.served = False
        t_system = self.slicesim.sim_state.now - self.t_arrival
        # calculate estimated and occupation durations
        tp = self.user.channel.update_remaining_load(self)       # update remaining load, return throughput
        self.server.counter_collection.count_throughput(tp)
        self.d_served = self.d_served + t_system - (self.d_wait+self.d_served)

    def complete_service(self):
        """
        Change the status of the packet once the serving process is completed.
        """
        self.served = False
        self.completed = True
        self.t_complete = self.slicesim.sim_state.now
        t_system = self.slicesim.sim_state.now - self.t_arrival
        tp = self.user.channel.get_throughput_sc(self)       # return throughput
        self.server.counter_collection.count_throughput(tp)
        tp2 = self.user.channel.get_throughput_sc2(self)       # return throughput 2
        self.server.counter_collection.count_throughput2(tp2)
        self.remaining_load = 0
        self.d_served = self.d_served + t_system - (self.d_wait + self.d_served)

    def get_remaining_load(self):
        """
        return
        """
        return self.user.channel.get_remaining_load(self)

    def get_throughput(self):
        """
        return the average throughput since remaining_load calculated
        """
        return self.user.channel.get_throughput_rt(self)

    def get_waiting_time(self):
        """
        Return the waiting time of the packet. An error occurs when the packet has not been served yet.
        :return: waiting time
        """
        if not self.served and not self.completed:
            raise SystemError("Packet has not been served yet.")
        else:
            # return self.t_start - self.t_arrival
            return self.d_wait

    def get_service_time(self):
        """
        Calculate and return the service time
        :return: service time
        """
        if not self.completed:
            raise SystemError("Packet is not completed yet.")
        else:
            # return self.t_complete - self.t_start
            return self.d_served

    def get_system_time(self):
        """
        Calculate and return the system time (waiting time + service time)
        :return: system time (waiting time + serving time)
        """
        if not self.completed:
            raise SystemError("Packet is not completed yet.")
        else:
            return self.t_complete - self.t_arrival
