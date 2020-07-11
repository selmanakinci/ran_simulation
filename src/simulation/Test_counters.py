from sliceparam import SliceParam
from slicesimulation import SliceSimulation
from rng import RNG, ExponentialRNS, UniformRNS
from user import User
from simparam import SimParam

sim_param = SimParam(100)
slice_param = SliceParam(sim_param)
slice = SliceSimulation(slice_param)
user = User(user_id=0, dist=10, slice_list=[slice], sim_param=sim_param)
slice.insert_users([user])
counter_collection = slice.server_list[0].counter_collection

# -----------------------
slice.sim_state.now = 0
slice.sim_state.now = 1
mean_tp_1 = counter_collection.cnt_tp.get_mean_one_round()

slice.sim_state.now = 2
mean_tp_2 = counter_collection.cnt_tp.get_mean_one_round()

slice.sim_state.now = 3
mean_tp_3 = counter_collection.cnt_tp.get_mean_one_round()
counter_collection.count_throughput(0)  # start

slice.sim_state.now = 4
mean_tp_4 = counter_collection.cnt_tp.get_mean_one_round()
counter_collection.count_throughput(4000)  # pause


slice.sim_state.now = 5
mean_tp_5 = counter_collection.cnt_tp.get_mean_one_round()
mean_delay_5 = counter_collection.cnt_syst.get_mean_one_round()
counter_collection.count_throughput(0)     # start

slice.sim_state.now = 5.4
counter_collection.count_throughput(5000)  # finish
counter_collection.cnt_syst.count(5.4-2.3)

slice.sim_state.now = 6
mean_tp_6 = counter_collection.cnt_tp.get_mean_one_round()
mean_delay_6 = counter_collection.cnt_syst.get_mean_one_round()

msa = 0