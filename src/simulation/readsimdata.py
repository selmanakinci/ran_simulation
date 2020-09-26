import csv
import numpy as np
from matplotlib import pyplot
import pandas as pd
from matplotlib.patches import Polygon


def read_sim_data(parent_dir, no_of_slices=3, no_of_users_list=(10,10,10)):

    # slices avg over simulation run
    class SimAvgResult(object):
        def __init__(self):
            self.tp = None
            self.tp2 = None
            self.ql = None
            self.delay = None
            self.packets_total = None
            self.packets_served = None
            self.packets_dropped = None
            self.bp = None

    class SliceResult(object):
        def __init__(self):
            self.round_avg = None
            self.sim_avg = None

        def get_sim_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()[0]
            tmp.delay = df.loc['mean_system_time'].to_numpy ()[0]
            tmp.tp = df.loc['mean_rate'].to_numpy ()[0]
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()[0]
            tmp.packets_total = df.loc['packets_total'].to_numpy ()[0]
            tmp.packets_served = df.loc['packets_served'].to_numpy ()[0]
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()[0]
            tmp.bp = df.loc['blocking_probability'].to_numpy ()[0]
            self.sim_avg = tmp

        def get_round_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()
            tmp.delay = df.loc['mean_system_time'].to_numpy ()
            tmp.tp = df.loc['mean_rate'].to_numpy ()
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()
            tmp.packets_total = df.loc['packets_total'].to_numpy ()
            tmp.packets_served = df.loc['packets_served'].to_numpy ()
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()
            tmp.bp = df.loc['blocking_probability'].to_numpy ()
            self.round_avg = tmp

    class UserResult(object):
        def __init__(self):
            self.tp = None
            self.tp2 = None
            self.ql = None
            self.delay = None
            self.round_avg = None
            self.sim_avg = None

        def get_sim_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()[0]
            tmp.delay = df.loc['mean_system_time'].to_numpy ()[0]
            tmp.tp = df.loc['mean_rate'].to_numpy ()[0]
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()[0]
            tmp.packets_total = df.loc['packets_total'].to_numpy ()[0]
            tmp.packets_served = df.loc['packets_served'].to_numpy ()[0]
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()[0]
            tmp.bp = df.loc['blocking_probability'].to_numpy ()[0]
            self.sim_avg = tmp

        def get_round_avg(self, df: pd.DataFrame):
            tmp = SimAvgResult()
            tmp.ql = df.loc['mean_queue_length'].to_numpy ()
            tmp.delay = df.loc['mean_system_time'].to_numpy ()
            tmp.tp = df.loc['mean_rate'].to_numpy ()
            tmp.tp2 = df.loc['mean_throughput2'].to_numpy ()
            tmp.packets_total = df.loc['packets_total'].to_numpy ()
            tmp.packets_served = df.loc['packets_served'].to_numpy ()
            tmp.packets_dropped = df.loc['packets_dropped'].to_numpy ()
            tmp.bp = df.loc['blocking_probability'].to_numpy ()
            self.round_avg = tmp

    class SimResult(object):
        def __init__(self):
            self.controller = None
            self.sm = []
            self.user_results = [UserResult()] * sum(no_of_users_list)
            self.slice_results = [SliceResult()] * no_of_slices

            self.reward_arr = []
            self.slice_scores = None

        def add_sm_data(self, sm_data):
            self.sm.append(sm_data)

    result = SimResult()

    # env_dataframe
    # reward and slice scores
    filename = parent_dir + "/env_df.csv"
    env_df = pd.read_csv (filename)
    result.reward_arr = env_df['reward_hist'].values.tolist()
    result.slice_scores = [env_df[['slice_score_%d' %(i)]].values.tolist() for i in range(no_of_slices)]


    # Controller
    path = parent_dir + "/controller/"
    filename = path + "data/rb_allocation.csv"
    result.controller = pd.read_csv(filename)

    # SLICE MANAGER
    path = parent_dir + "/sm/"
    for i in range(no_of_slices):
        filename = path + "data/slice%d_rb_allocation.csv" % i
        result.add_sm_data(sm_data=pd.read_csv(filename))

    # Server(user) Results
    path = parent_dir + "/user_results"
    user_id = 0
    for j in range(no_of_slices):
        for k in range(no_of_users_list[j]):
            tmp_user_result = UserResult()
            # user_id = j * no_of_users_per_slice + k

            # tp
            filename = path + "/tp" + "/slice%d_user%d_tp_data.csv" % (j, user_id)
            tmp_user_result.tp = pd.read_csv (filename, header=None, index_col=0)

            # tp2
            filename = path + "/tp2" + "/slice%d_user%d_tp2_data.csv" % (j, user_id)
            tmp_user_result.tp2 = pd.read_csv (filename, header=None, index_col=0)

            # ql
            filename = path + "/ql" + "/slice%d_user%d_ql_data.csv" % (j, user_id)
            tmp_user_result.ql = pd.read_csv (filename, header=None, index_col=0)

            # syst (delay)
            filename = path + "/delay" + "/slice%d_user%d_delay_data.csv" % (j, user_id)
            tmp_user_result.delay = pd.read_csv (filename, header=None, index_col=0)

            # round average results
            filename = path + "/average_results/data" + "/slice%d_user%d_avg_data.csv" % (j, user_id)
            tmp_user_result.get_round_avg (pd.read_csv (filename, header=0, index_col=0))

            # sim average results
            filename = path + "/average_results/data" + "/slice%d_user%d_sim_avg_data.csv" % (j, user_id)
            tmp_user_result.get_sim_avg(pd.read_csv (filename, header=0, index_col=0))

            # assign tmp user result
            result.user_results[user_id] = tmp_user_result
            user_id+=1

    # Slice Results
    path = parent_dir + "/slice_results/average_results/data"
    for j in range(no_of_slices):
        try:
            filename = path + "/slice%d_sim_avg_data.csv" % j
            tmp_slice_result = SliceResult()
            tmp_slice_result.get_sim_avg(pd.read_csv(filename, header=0, index_col=0))

            # round average results
            filename = path + "/slice%d_avg_data.csv" % j
            tmp_slice_result.get_round_avg (pd.read_csv (filename, header=0, index_col=0))

            result.slice_results[j] = tmp_slice_result

        except:
            print ("ERROR: in reading results for slice %d " % j)

    return result