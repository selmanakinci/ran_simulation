from sliceparam import SliceParam
from slicesimulation import SliceSimulation
from event import PacketArrival
from user import User
from simparam import SimParam
from packet import Packet
'''
packet arrival
start service
pause service
start service
complete service
'''
sim_param = SimParam(100)
slice_param = SliceParam(sim_param)
slice = SliceSimulation(slice_param)
user = User(user_id=0, dist=10, slice_list=[slice], sim_param=sim_param)
slice.insert_users([user])
server = slice.server_list[0]
server.RB_list = [0]
# -----------------------
P = Packet(slice, user, size=60)
P.t_arrival = 8
slice.sim_state.now = 8
P.start_service()

slice.sim_state.now = 9
P.pause_service()

slice.sim_state.now = 5
P.start_service()

slice.sim_state.now = 6
P.complete_service()

msa = 0