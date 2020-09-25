from sliceparam import SliceParam
from slicesimulation import SliceSimulation
from rng import RNG, ExponentialRNS, UniformRNS
from user import User


def initialize_slices(sim_param, log_file):
    slices = []

    # SLA requirements list [RR, MCQI PF]
    delay_thresholds = [60, 40, 60]  # ms
    rate_thresholds = [3000, 4000, 3000]#[2000, 3200, 2000]  # kbps  float(slc.slice_param.P_SIZE / slc.slice_param.MEAN_IAT)

    packet_sizes = [10000, 10000, 10000]  # [2000, 10000, 5000]  # in bits
    mean_iats = [1, 1, 1]
    # dist_arr = [[10]*10,[10]*10,[10]*10]#[[10, 10, 10, 10, 10, 100, 100, 100, 100, 100],[12]*10,[10, 10, 10, 10, 10, 100, 100, 100, 100, 100]]

    seed_dist = sim_param.SEED_OFFSET  # users in all slices have identical distance distributions
    # rng_dist = RNG(ExponentialRNS(lambda_x=1. / float(sim_param.MEAN_Dist)), s_type='dist') # , the_seed=seed_dist
    rng_dist = RNG (UniformRNS (sim_param.DIST_MIN, sim_param.DIST_MAX, the_seed=seed_dist), s_type='dist')

    tmp_user_id=0
    for i in range(sim_param.no_of_slices):
        slice_param_tmp = SliceParam(sim_param)
        slice_param_tmp.SLICE_ID = i

        slice_param_tmp.P_SIZE = packet_sizes[i]
        slice_param_tmp.MEAN_IAT = mean_iats[i]

        # SLA requirements
        slice_param_tmp.DELAY_REQ = delay_thresholds[i]
        slice_param_tmp.RATE_REQ = rate_thresholds[i]
        slices.append(SliceSimulation(slice_param_tmp))

        # initialize all users with traffics and distances
        tmp_users = []
        # dist_arr_tmp = dist_arr[i]  #  [10, 10, 10, 10, 10, 100, 100, 100, 100, 100]  # 10*(1+user_id%no_of_users_per_slice)**2
        for j in range(sim_param.no_of_users_list[i]):
            # user_id = i * sim_param.no_of_users_per_slice + j
            tmp_users.append(User(tmp_user_id, rng_dist.get_dist(), slice_list=[slices[i]], sim_param=sim_param))
            # tmp_users.append(User(user_id, dist_arr_tmp[j], slice_list=[slices[i]], sim_param=sim_param))
            tmp_user_id+=1

        # insert users to slice
        slices[i].insert_users(tmp_users)

    # Choose Slice Manager Algorithm       'PF': prop fair, 'MCQI': Max Channel Quality Index, 'RR': round-robin
    slices[0].slice_param.SM_ALGO = 'RR'
    slices[1].slice_param.SM_ALGO = 'MCQI'
    slices[2].slice_param.SM_ALGO = 'PF'

    if log_file is None:
        pass
    else:
        # log Slice Parameters
        for i in range(sim_param.no_of_slices):
            attrs = vars(slices[i].slice_param)
            log_file.write('\nSliceParam\n' + ''.join("%s: %s\n" % item for item in attrs.items()))
        log_file.close()

    return slices
