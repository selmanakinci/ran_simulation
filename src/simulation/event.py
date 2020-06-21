import heapq
import random


class EventChain(object):

    """
    This class contains a queue of events.

    Events can be inserted and removed from queue and are sorted by their time.
    Always the oldest event is removed.
    """

    def __init__(self):
        """
        Initialize variables and event chain
        """
        self.event_list = []

    def insert(self, e):
        """
        Inserts event e to the event chain. Event chain is sorted during insertion.
        :param: e is of type SimEvent

        """
        heapq.heappush(self.event_list, e)

    def remove_oldest_event(self):
        """
        Remove event with smallest timestamp (and priority) from queue
        :return: next event in event chain
        """
        heapq.heapify(self.event_list)
        return heapq.heappop(self.event_list)

    def copy_oldest_event(self):
        """
        Return event with smallest timestamp (and priority) from queue without removing
        :return: next event in event chain
        """
        heapq.heapify(self.event_list)
        e = self.event_list[0]
        return e

    def remove_event(self, e):
        """
        Removes event e from event chain. Event chain is sorted after removal.
        :param: e is of type SimEvent

        """
        self.event_list.remove(e)
        heapq.heapify(self.event_list)

class SimEvent(object):

    """
    SimEvent represents an abstract type of simulation event.

    Contains mainly abstract methods that should be implemented in the subclasses.
    Comparison for EventChain insertion is implemented by comparing first the timestamps and then the priorities
    """

    def __init__(self, slicesim, timestamp):
        """
        Initialization routine, setting the timestamp of the event and the simulation it belongs to.
        """
        self.timestamp = timestamp
        self.priority = 0
        self.slicesim = slicesim

    #self.event_chain.event_list.remove(PacketArrival(self, 450))
    #PacketArrival(self, 450) in self.event_chain.event_list
    def process(self, server):
        """
        General event processing routine. Should be implemented in subclass
        """
        raise NotImplementedError("Please Implement method \"process\" in subclass of SimEvent")

    def __hash__(self):         # added when python 3 is used and dictionary keys require this
        return hash((self.timestamp, self.priority, str(self)))

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.priority == other.priority

    def __lt__(self, other):
        """
        Comparison is made by comparing timestamps. If time stamps are equal, priorities are compared.
        """
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        elif self.priority != other.priority:
            return self.priority < other.priority
        else:
            return self.priority < other.priority


class ServiceCompletion(SimEvent):

    """
    Defines a service completion event (highest priority in EventChain)
    """

    def __init__(self, slicesim, timestamp):
        """
        Create a new service completion event with given execution time.

        Priority of service completion event is set to 0 (highest).
        """
        super(ServiceCompletion, self).__init__(slicesim, timestamp)
        self.priority = 0

    def process(self, server):
        """
        Processing procedure of a service completion.

        First, the server is set from busy to idle.
        Then, if the queue is not empty, the next packet is taken from the queue and served,
        hence a new service completion event is created and inserted in the event chain.
        """
        completed_packet = server.complete_service()
        server.server_state.packet_completed(completed_packet.SLA_satisfied)
        if server.start_service():
            # trigger next packet
            ev = ServiceCompletion(self.slicesim, server.served_packet.t_finish)
            server.event_chain.insert(ev)


class PacketArrival(SimEvent):

    """
    Defines a new customer arrival event (new packet comes into the system)
    """

    def __init__(self, slicesim, timestamp):
        """
        Create a new customer arrival event with given execution time.

        Priority of customer arrival event is set to 1 (second highest)
        """
        super(PacketArrival, self).__init__(slicesim, timestamp)
        self.priority = 3

    def process(self, server):
        """
        Processing procedure of a customer arrival.

        First, the next customer arrival event is created
        Second, the process tries to add the packet to the server, then to the queue, if necessary.
        If packet is added to the server, a service completion event is generated.
        Each customer is counted either as accepted or as dropped.
        """

        if server.add_packet_to_server():
            # packet is added to server and served
            ev = ServiceCompletion(self.slicesim, server.served_packet.t_finish)
            server.event_chain.insert(ev)
            #self.slicesim.sim_state.packet_accepted()
            server.server_state.packet_accepted()

        else:
            if server.add_packet_to_queue():
                # packet is added to queue
                #self.slicesim.sim_state.packet_accepted()
                server.server_state.packet_accepted()
            else:
                #self.slicesim.sim_state.packet_dropped()
                server.server_state.packet_dropped()


class ServerActivation(SimEvent):

    """
    Defines a server activation event (priority=2)
    """

    def __init__(self, slicesim, timestamp, RB_list):
        """
        Create a new server activation event with given execution time.

        Priority of server activation event is set to 2.
        """
        super(ServerActivation, self).__init__(slicesim, timestamp)
        self.priority = 2
        self.RB_list = RB_list

    def process(self, server):
        """
        Processing procedure of a ServerActivation.

        First, the server is set from busy to idle.
        Then, if the queue is not empty, the next packet is taken from the queue and served,
        hence a new service completion event is created and inserted in the event chain.
        """

        if not server.server_active:
            if server.server_busy:
                raise RuntimeError("ERROR: inactive server cant be busy.")
            else:
                server.insert_RB_list(self.RB_list)
                server.activate_server()
                if server.start_service():
                    # packet is added to server and served
                    ev = ServiceCompletion(self.slicesim, server.served_packet.t_finish)
                    server.event_chain.insert(ev)
                    #self.slicesim.sim_state.packet_accepted()
                    #server.server_state.packet_accepted()
        else:
            if not server.server_busy:
                server.insert_RB_list(self.RB_list)
                server.activate_server()    # unneccessary
                if server.start_service():
                    # packet is added to server and served
                    ev = ServiceCompletion(self.slicesim, server.served_packet.t_finish)
                    server.event_chain.insert(ev)
                    #self.slicesim.sim_state.packet_accepted()
                    #server.server_state.packet_accepted()
            else:
                server.pause_service()
                server.insert_RB_list(self.RB_list)
                server.activate_server()
                if server.start_service():
                    # packet is added to server and served
                    ev = ServiceCompletion(self.slicesim, server.served_packet.t_finish)
                    server.event_chain.insert(ev)
                    #self.slicesim.sim_state.packet_accepted()
                    #server.server_state.packet_accepted()


class ServerDeactivation(SimEvent):

    """
    Defines a server deactivation event (priority=1)
    """

    def __init__(self, slicesim, timestamp):
        """
        Create a new server deactivation event with given execution time.

        Priority of server deactivation event is set to 1.
        """
        super(ServerDeactivation, self).__init__(slicesim, timestamp)
        self.priority = 1

    def process(self, server):
        """
        Processing procedure of a ServerDeactivation.

        """
        if server.server_active:
            if not server.server_busy:
                server.deactivate_server()
            else:
                server.pause_service()  # remove service completion and calculate remaining load too
                server.deactivate_server()

        # inserting new RB_list into server as changing previous one
        server.insert_RB_list([-1])

class RB_Allocation(SimEvent):

    """
    Defines a resource block allocation event for slice manager (priority = 4)
    """

    def __init__(self, slicesim, timestamp):
        """

        """
        super(RB_Allocation, self).__init__(slicesim, timestamp)
        self.priority = 4

    def process(self, event_chain_slice_manager):
        self.slicesim.slice_manager.RB_allocate_to_users()


class RoundTermination(SimEvent):

    """
    Defines the end of a one round (T_C).(priority = 5) least priority in EventChain
    """

    def __init__(self, slicesim, timestamp):
        """
        Create a new simulation termination event with given execution time.
        Priority of round termination event is set to 5 (lowest)
        """
        super(RoundTermination, self).__init__(slicesim, timestamp)
        self.priority = 5

    def process(self, server):
        """
        Simulation stop flag is set to true, so simulation is stopped after this event.
        """
        self.slicesim.sim_state.stop = True
        # count currently served packets
        for s in self.slicesim.server_list:
            s.counter_collection.count_queue()  # count ql

            # if s.served_packet is not None:
            #     p = s.served_packet
            #     tp = p.user.channel.get_throughput_rt(p)       # return throughput
            #     s.counter_collection.count_throughput_rt(tp)
