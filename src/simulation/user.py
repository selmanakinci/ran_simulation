from trafficgenerator import TrafficGenerator
from event import PacketArrival
import numpy as np
from channelmodal import ChannelModal
from channelmodal_cts import ChannelModalCts
from simparam import SimParam


class User(object):

    """
    User
    """

    def __init__(self, user_id, dist=10, slice_list=[], sim_param=SimParam()):
        """

        """
        self.user_id = user_id
        self.slice_list = slice_list
        self.sim_param = sim_param
        self.distance = dist # np.random.uniform(self.sim_param.dist_range)
        if self.sim_param.cts_service:
            self.channel = ChannelModalCts(self)
        else:
            self.channel = ChannelModal(self)

        self.traffic_generator = TrafficGenerator(self)
        self.traffic_list = []
        self.traffic_list_dict = {}
        for i in self.slice_list:
            self.traffic_list.append(self.traffic_generator.poisson_arrivals(i))
            self.traffic_list_dict.update({i.slice_param.SLICE_ID: self.traffic_list[-1]})
