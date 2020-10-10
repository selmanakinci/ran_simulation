from finitequeue import FiniteQueue
from packet import Packet
from event import ServiceCompletion
from countercollection import CounterCollection
from serverstate import ServerState
from serverresult import ServerResult


class Server(object):
    """
    This class represents the state of our system.

    It contains information about whether the server is busy and how many customers
    are waiting in the queue (buffer). The buffer represents the physical buffer or
    memory of our system, where packets are stored before they are served.

    The integer variable buffer_content represents the buffer fill status, the flag
    server_busy indicates whether the server is busy or idle.

    The simulation object is only used to determine the maximum buffer space as
    determined in its object slice_param.
    """

    def __init__(self, slicesim, user, event_chain):
        """
        Create a system state object
        :param slicesim: simulation object for determination of maximum number of stored
        packets in buffer
        user: user object that the server belongs to
        :return: server object
        """
        self.log = []
        self.slicesim = slicesim
        self.user = user

        self.event_chain = event_chain
        self.buffer = FiniteQueue(self)

        self.RB_list = [-1]
        self.RB_list_previous = [-1]
        self.RB_counter = 0  # total no of resources

        self.counter_collection = CounterCollection(self)
        self.server_result = ServerResult(self)

        self.server_state = ServerState()
        self.latest_arrival = 0
        self.server_busy = False
        self.server_active = False
        self.served_packet = None

    def insert_RB_list(self, RB_list):
        # copy current RB_list to previous
        self.RB_list_previous = self.RB_list
        self.RB_list = RB_list

    def remove_oldest_packet(self):
        # removes the oldest packet from server
        if self.served_packet == None:
            if self.buffer.is_empty():
                raise RuntimeError("ERROR: buffer empty, cant remove the packet.")
            else:
                self.removed_packet = self.buffer.remove()
        else:
            if self.served_packet.served:
                self.pause_service()
                self.served_packet = None
                if self.start_service():
                    self.event_chain.insert(ServiceCompletion(self.slicesim, self.served_packet.t_finish))
            else:
                self.served_packet = None
        self.server_state.packet_removed()

    def add_packet_to_server(self):
        """
        Try to add a packet to the server unit.
        :return: True if server is not busy and packet has been added successfully.
        """

        if not self.server_busy and self.server_active:
            self.server_busy = True
            self.served_packet = Packet(self.slicesim, self.user, self.slicesim.slice_param.P_SIZE, self.slicesim.sim_state.now - self.latest_arrival)
            self.latest_arrival = self.slicesim.sim_state.now
            self.served_packet.start_service()
            return True
        else:
            return False

    def add_packet_to_queue(self):
        """
        Try to add a packet to the buffer.
        :return: True if buffer/queue is not full and packet has been added successfully.
        """
        if self.buffer.add(Packet(self.slicesim, self.user, self.slicesim.slice_param.P_SIZE, self.slicesim.sim_state.now - self.latest_arrival)):
            self.latest_arrival = self.slicesim.sim_state.now
            return True
        else:
            self.latest_arrival = self.slicesim.sim_state.now
            return False

    def start_service(self):
        """
        If the buffer is not empty, take the next packet from there and serve it.
        :return: True if buffer is not empty and a stored packet is being served.
        """
        if self.served_packet == None:
            if self.buffer.is_empty():
                return False
            else:
                self.served_packet = self.buffer.remove()
                #self.counter_collection.count_throughput(0)  # firstly throughput is calculated
                self.served_packet.start_service()
                self.server_busy = True
                return True
        else:
            #self.counter_collection.count_throughput(0)  # firstly throughput is calculated
            self.served_packet.start_service()
            self.server_busy = True
            return True

    def pause_service(self):
        """
        If the buffer is not empty, take the next packet from there and serve it.
        :return: True if buffer is not empty and a stored packet is being served.
        """
        #self.counter_collection.count_throughput(self.served_packet.get_throughput())  # firstly throughput is calculated
        #self.event_chain.event_list.remove(ServiceCompletion(self, self.served_packet.t_finish))
        self.event_chain.remove_event(ServiceCompletion(self, self.served_packet.t_finish))
        self.served_packet.pause_service()
        self.server_busy = False

    def complete_service(self):
        """
        Reset server status to idle after a service completion.
        """
        #self.counter_collection.count_throughput(self.served_packet.get_throughput())  # first throughput is calculated
        self.server_busy = False
        p = self.served_packet
        p.complete_service()
        #self.slicesim.counter_collection.count_packet(p) # now each server has counter collection
        self.counter_collection.count_packet(p)
        self.served_packet = None
        return p

    def activate_server(self):
        """
        If the buffer is not empty, take the next packet from there and serve it.
        """
        self.server_busy = False
        self.server_active = True

    def deactivate_server(self):
        """
        If the buffer is not empty, take the next packet from there and serve it.
        """
        self.server_active = False

    def get_queue_length(self):
        """
        Return the current buffer content.
        :return: Fill status of the buffer
        """
        return self.buffer.get_queue_length()

    def get_CQI_list(self, RB_mapping):
        """
        return CQI array
        """
        return self.user.channel.get_CQI_list(self, RB_mapping)