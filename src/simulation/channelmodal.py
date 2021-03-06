import numpy as np
from scipy import constants
from rng import RNG, ExponentialRNS, UniformRNS, NormalRNS


class ChannelModal(object):

    """

    """

    def __init__(self, user):
        """
        R
        """

        self.user = user
        self.RB_pool = user.sim_param.RB_pool
        #self.rng = RNG(ExponentialRNS(1. / float(user.sim_param.MEAN_CG), user.sim_param.SEED_CG), s_type='cg')
        #self.rng = RNG(UniformRNS(2*float(user.sim_param.MEAN_CG), 0., user.sim_param.SEED_CG), s_type='cg')
        #self.rng = RNG(ExponentialRNS(1. / float(user.sim_param.MEAN_CG), user.user_id), s_type='cg')
        #self.rng = RNG(UniformRNS(2. , 0., 21), s_type='cg')
        # self.channel_gains = (user.user_id%2+0.1)*self.rng.get_cg(len(self.RB_pool), user.sim_param.T_FINAL + user.sim_param.T_C)

        #self.channel_gains = np.random.rand(len(self.RB_pool), user.sim_param.T_FINAL+user.sim_param.T_C)
        #self.channel_gains = np.ones((len(self.RB_pool), user.sim_param.T_FINAL + user.sim_param.T_C))

        # Rayleigh Fading:
        # self.rayleigh_envelope = GenerateRayleighEnvelope(self.RB_pool, user.sim_param.T_FINAL, user.sim_param.T_S, fm=10)

        # New channel model rate = BW * log2(1+SINR)
        # SNR(dB) = Pt-PL-P_noise,
        #self.pathloss_dB = self.get_pathloss()
        self.noise_per_rb_dBm = self.get_noise_per_rb()
        #self.SINR_dB = self.user.sim_param.P_TX_dBm - self.pathloss_dB - self.noise_per_rb_dBm

        #seed_shadowing = self.user.user_id  # % self.user.sim_param.no_of_users_per_slice
        #self.rng_shadowing = RNG(NormalRNS(0, self.user.sim_param.SIGMA_shadowing, seed_shadowing), s_type='shadowing')
        #self.shadowing = self.rng_shadowing.get_shadowing(user.sim_param.T_FINAL)
        self.shadowing = self.get_shadowing()

    def get_shadowing(self):
        t_final = self.user.sim_param.T_FINAL*10
        shadowing = np.empty((0, t_final))

        seed_shadowing = self.user.user_id * len(self.RB_pool)
        for i in range(len(self.RB_pool)):
            self.rng_shadowing = RNG(NormalRNS(0, self.user.sim_param.SIGMA_shadowing, seed_shadowing), s_type='shadowing')
            temp_arr = self.rng_shadowing.get_shadowing(t_final)
            shadowing = np.append(shadowing, [temp_arr], axis=0)
            if self.user.sim_param.freq_selective:
                seed_shadowing+=1
        return shadowing


    def get_noise_per_rb(self):
        """
        returns noise in dB

        P_noise_dBm = 10*log10(k_boltzmann * temperature * bandwidth / 1mW)
        """
        try:
            k_boltzmann = constants.Boltzmann
            temperature = self.user.sim_param.TEMPERATURE
            rb_bw = self.user.sim_param.RB_BANDWIDTH

            P_noise_dBm = 10 * np.log10(k_boltzmann * temperature * rb_bw / 1e-3)

        except:
            raise RuntimeError("Noise calculation error")
            return

        return P_noise_dBm

    def get_pathloss(self, rb, time):
        """
        returns pathloss in dB

        PL= FSPL(f,1m)+10n log_10⁡(d/1m)+ shadowing
        FSPL(f,1m)=20 log_10⁡(4πf/c)
        shadowing =
        """
        try:
            f = self.user.sim_param.FREQ
            n = self.user.sim_param.PL_Exponent
            d = self.user.distance  # in meter
            c = constants.c
            pi = constants.pi

            shadowing_dB = self.shadowing[rb, time]
            fs_pl_dB = 20*np.log10(4*pi*f/c)
            pl_dB = fs_pl_dB + 10*n*np.log10(d) + shadowing_dB

        except:
            raise RuntimeError("Path loss calculation error")
            return

        return pl_dB

    def get_data_rate(self, rb_arr, time):
        """
        add effect of time in deterministic manner!!!!
        rate = BW * log2(1 + SINR)  in bits per sec
        :return: summation of data rate of given user for given resource blocks
        """

        try:
            rate = 0
            rb_bw = self.user.sim_param.RB_BANDWIDTH
            if time-int(time) > 0.0001:
                raise RuntimeError("Time variable is not integer!!")

            if rb_arr == [-1]:
                return 0
            for rb in rb_arr:
                pathloss_dB = self.get_pathloss(rb, time)
                SINR_dB = self.user.sim_param.P_TX_dBm - pathloss_dB - self.noise_per_rb_dBm
                SINR = np.power(10, SINR_dB / 10)
                rate += rb_bw * np.log2(1 + SINR)
                #rate += 1000 # for testing each ms 1 bit is served
        except:
            raise RuntimeError("Data Rate Calculation error")

        return rate

    def get_load_change(self, rb_arr, time_arr):
        """
        :return: data rate * duration of given user for given resource blocks at given time array
        data rate is calculated separately for each ms and summed.
        load_change in bits
        """

        try:
            if len(time_arr) == 0:
                return 0
            load_change = 0
            for t in time_arr:
                if isinstance(t,float):
                    raise RuntimeError("time must be integer")
                load_change += np.nansum(self.get_data_rate(rb_arr, t)*1e-3)  # rate * 1ms
        except:
            raise RuntimeError("Error during transmitted load calculation")

        return load_change  # np.sum(self.channel_gains[rb_arr][time])  # user_id-1 for indexing

    def get_serving_duration(self, packet):
        """
        Change the status of the packet once the serving process starts.
        """
        t_s = self.user.sim_param.T_S
        #t_temp = packet.slicesim.sim_state.now # - packet.slicesim.sim_state.t_round_start)
        t_temp = packet.t_last_start
        t_arr = np.arange(t_temp, t_temp + t_s)
        RB_arr = packet.server.RB_list
        r_temp = self.get_load_change(RB_arr, t_arr)

        try:
            while r_temp < packet.remaining_load:
                t_temp += t_s
                t_arr = np.arange(t_temp, t_temp + t_s)
                r_temp += self.get_load_change(RB_arr, t_arr)

        except:
            raise RuntimeError("Error during get_serving_duration")


        r_last = self.get_load_change(RB_arr, t_arr)
        t_last = (packet.remaining_load-(r_temp-r_last))/(r_last/t_s)
        t_est = t_temp+t_last
        #packet.estimated_duration = t_est - packet.slicesim.sim_state.now
        #packet.occupation_duration = t_temp+t_s-packet.slicesim.sim_state.now
        packet.t_finish_real = t_est#+packet.slicesim.sim_state.t_round_start
        packet.t_finish = t_temp+t_s#+packet.slicesim.sim_state.t_round_start

    def update_remaining_load(self, packet):
        """
        substract load change since the latest serving from remaining load
        return tp = load_change / duration
        """
        t_start = int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        if packet.t_arrival + (packet.d_wait + packet.d_served) - t_start > 0.0001:
            raise RuntimeError("time calculation error in packet")
        t_arr = np.arange(t_start, packet.slicesim.sim_state.now)
        RB_arr = packet.server.RB_list  # function is called before RB_list is changed
        r_temp = self.get_load_change(RB_arr, t_arr)
        packet.remaining_load -= r_temp
        if packet.remaining_load < 0:
            raise RuntimeError("Remaining load can't be negative!")

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(r_temp) / float(packet.slicesim.sim_state.now-t_start)
            return tp  # throughput in kilobits  per second
        else:
            return float(0)

    def get_remaining_load(self, packet):
        """
        returns the remaining load without changing anything
        initially same as update_remaining_load
        """
        t_start = int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        if packet.t_arrival + (packet.d_wait + packet.d_served) - t_start > 0.0001:
            raise RuntimeError("time calculation error in packet")
        t_arr = np.arange(t_start, packet.slicesim.sim_state.now)
        RB_arr = packet.server.RB_list
        r_temp = self.get_load_change(RB_arr, t_arr)
        return packet.remaining_load - r_temp

    def get_throughput_rt(self, packet):
        """
        NOT USED
        returns throughput for round termination event without changing anything
        """
        t_start = int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        if packet.t_arrival + (packet.d_wait + packet.d_served) - t_start > 0.0001:
            raise RuntimeError("time calculation error in packet")
        t_arr = np.arange(t_start, packet.slicesim.sim_state.now)
        RB_arr = packet.server.RB_list
        r_temp = self.get_load_change(RB_arr, t_arr)

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(r_temp)/float(packet.slicesim.sim_state.now-t_start)  # total served size over time
            return tp  #throughput
        else:
            return float(0)

    def get_throughput_sc(self, packet):
        """
        Only when service is completed, calculates the latest serve
        """
        t_start = int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        if packet.t_arrival + (packet.d_wait + packet.d_served) - t_start > 0.0001:
            raise RuntimeError("time calculation error in packet")
        t_arr = np.arange(t_start, packet.slicesim.sim_state.now)
        #RB_arr = packet.server.RB_list  # function is called after RB_list is changed
        #r_temp = self.get_output_rate(RB_arr, t_arr)

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(packet.remaining_load)/float(packet.slicesim.sim_state.now-t_start)  # total served size over time
            return tp  #throughput
        else:
            return float(0)

    def get_throughput_sc2(self, packet):
        """
        Only when service is completed, counts just service completions
        """
        t_start = packet.t_last_start# int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        t_arr = np.arange(t_start, packet.slicesim.sim_state.now)

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(packet.size)/float(packet.slicesim.sim_state.now-t_start)  # total served size over time
            return tp  #throughput
        else:
            return float(0)

    def get_CQI_list(self, server, RB_mapping_sm):
        """
            returns data_rate values for each rb at each timeslot in T_sm
            only get the rate at the beginning of new Ts period.
        """
        CQI_list = []
        t_s = self.user.sim_param.T_S
        t_temp = int(server.slicesim.sim_state.now)# - packet.slicesim.sim_state.t_round_start)
        if server.slicesim.sim_state.now - t_temp > 0.0001:
            raise RuntimeError("time calculation error in get_CQI_list")
        #t_arr = np.arange(t_temp, t_temp + t_s)

        # fill RB_matching_sm
        for i in range(RB_mapping_sm.shape[1]):         # loop over time
            RB_arr = []
            tmp_arr = []
            for j in range(RB_mapping_sm.shape[0]):     # loop over RBs
                if RB_mapping_sm[j][i]:
                    #RB_arr.append(j)
                    #tmp_arr.append(self.get_load_change([j], t_arr))
                    tmp_arr.append(self.get_data_rate([j], t_temp))
                else:
                    tmp_arr.append(-1.)

            #CQI_list.append(self.get_output_rate(RB_arr, t_arr))
            CQI_list.append(tmp_arr)
            t_temp += t_s   # increase time by t_s for the next slots rate
            #t_arr = np.arange(t_temp, t_temp + t_s)

        return CQI_list  # indexing: [time], [RB]

