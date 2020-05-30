from sliceparam import SliceParam
from slicesimulation import SliceSimulation
from rng import RNG, ExponentialRNS, UniformRNS
from user import User

def initialize_slices(sim_param, log_file):

    #slices, slice_results = ([] for i in range(2))
    slices = []

    for i in range(sim_param.no_of_slices):
        slice_param_tmp = SliceParam(sim_param)
        slice_param_tmp.SLICE_ID = i
        slices.append(SliceSimulation(slice_param_tmp))
        #slice_results.append([])

        # initialize all users with traffics and distances
        tmp_users = []
        seed_dist = 0  # users in all slices have identical distance distributions
        # rng_dist = RNG(ExponentialRNS(lambda_x=1. / float(sim_param.MEAN_Dist)), s_type='dist') # , the_seed=seed_dist
        rng_dist = RNG(UniformRNS(sim_param.DIST_MIN, sim_param.DIST_MAX, the_seed=seed_dist), s_type='dist')  #
        dist_arr = [10, 20]  # [30, 30, 100, 100, 100, 100, 100, 100, 100, 100]  # 10*(1+user_id%no_of_users_per_slice)**2
        for j in range(sim_param.no_of_users_per_slice):
          user_id = i * sim_param.no_of_users_per_slice + j
          # tmp_users.append(User(user_id, rng_dist.get_dist(), slice_list=[slices[i]], sim_param=sim_param))
          tmp_users.append(User(user_id, dist_arr[i], slice_list=[slices[i]], sim_param=sim_param))

        # insert users to slice
        slices[i].insert_users(tmp_users)

    # Choose Slice Manager Algorithm, 'PF': prop fair, 'MCQI': Max Channel Quality Index, 'RR': round-robin
    slices[0].slice_param.SM_ALGO = 'MCQI'#'RR'
    slices[1].slice_param.SM_ALGO = 'MCQI'
    #slices[2].slice_param.SM_ALGO = 'MCQI'#'PF'

    if log_file == None:
        pass
    else:
        # log Slice Parameters
        for i in range(sim_param.no_of_slices):
          attrs = vars(slices[i].slice_param)
          log_file.write('\nSliceParam\n' + ''.join("%s: %s\n" % item for item in attrs.items()))
        log_file.close()

    return slices#, slice_results