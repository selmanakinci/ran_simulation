import numpy as np
from scipy import constants
from rng import RNG, ExponentialRNS, UniformRNS, NormalRNS


class ChannelModalCts(object):
    """
    """
    def __init__(self, user):
        """
        """
        self.user = user
        self.RB_pool = user.sim_param.RB_pool
        '''self.rng = RNG(ExponentialRNS(1. / float(user.sim_param.MEAN_CG), user.sim_param.SEED_CG), s_type='cg')
        # self.rng = RNG(UniformRNS(2*float(user.sim_param.MEAN_CG), 0., user.sim_param.SEED_CG), s_type='cg')
        # self.rng = RNG(ExponentialRNS(1. / float(user.sim_param.MEAN_CG), user.user_id), s_type='cg')
        # self.rng = RNG(UniformRNS(2. , 0., 21), s_type='cg')
        # self.channel_gains = (user.user_id%2+0.1)*self.rng.get_cg(len(self.RB_pool), user.sim_param.T_FINAL + user.sim_param.T_C)
        #self.channel_gains = np.random.rand(len(self.RB_pool), user.sim_param.T_FINAL+user.sim_param.T_C)
        #self.channel_gains = np.ones((len(self.RB_pool), user.sim_param.T_FINAL + user.sim_param.T_C))'''

        self.noise_per_rb_dBm = self.get_noise_per_rb()

        # seed_shadowing = self.user.user_id  # % self.user.sim_param.no_of_users_per_slice
        # self.rng_shadowing = RNG(NormalRNS(0, self.user.sim_param.SIGMA_shadowing, seed_shadowing), s_type='shadowing')
        # self.shadowing = self.rng_shadowing.get_shadowing(user.sim_param.T_FINAL)
        self.shadowing = self.get_shadowing()

    def get_shadowing(self):
        t_final = self.user.sim_param.T_FINAL
        t_c = self.user.sim_param.T_C
        t_coh = self.user.sim_param.T_COH # in ms
        buffer = 2  # for the packets in simulation final
        shadowing = np.empty((0, int(t_final) + t_coh * (buffer -1) ))

        seed_shadowing = (self.user.user_id * len(self.RB_pool)) + self.user.sim_param.SEED_SHADOWING
        for i in range(len(self.RB_pool)):
            self.rng_shadowing = RNG(NormalRNS(0, self.user.sim_param.SIGMA_shadowing, seed_shadowing), s_type='shadowing')

            temp_shadowing = self.rng_shadowing.get_shadowing2(t_final, t_c, t_coh, buffer)
            shadowing = np.append(shadowing, [temp_shadowing], axis=0)
            if self.user.sim_param.freq_selective:
                seed_shadowing += 1
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
                SINR_dB = self.user.sim_param.P_TX_dBm - pathloss_dB - self.noise_per_rb_dBm  # SNR(dB) = Pt-PL-P_noise
                SINR = np.power(10, SINR_dB / 10)
                rate += rb_bw * np.log2(1 + SINR)
                #rate += 1000 # for testing each ms 1 bit is served
        except:
            raise RuntimeError("Data Rate Calculation error")

        return rate

    def get_load_change2(self, rb_arr, t_start, t_end):
        """
        :return: data rate * duration of given user for given resource blocks at given time interval(float)
        data rate is calculated separately for each ms and summed.
        load_change in bits
        """
        try:
            if t_start == t_end:
                return 0

            t0_f = int(np.floor(t_start))
            t0_c = int(np.ceil(t_start))
            t1_f = int(np.floor(t_end))
            if t0_c > t1_f:     # interval within the same ms
                assert(t0_f==t1_f)
                data_rate = self.get_data_rate(rb_arr, t0_f)
                duration = (t_end - t_start) * 1e-3
                load_change = duration * data_rate
            else:               # interval on different ms's
                data_rate_0 = self.get_data_rate(rb_arr, t0_f)
                duration_0 = (t0_c - t_start) * 1e-3
                load_change_0 = duration_0 * data_rate_0

                data_rate_1 = self.get_data_rate(rb_arr, t1_f)
                duration_1 = (t_end - t1_f) * 1e-3
                load_change_1 = duration_1 * data_rate_1

                load_change_btw = 0
                t_arr = np.arange(t0_c, t1_f, dtype=int)
                for t in t_arr:
                    load_change_btw += self.get_data_rate(rb_arr, t) * 1e-3

                load_change = load_change_0 + load_change_1 + load_change_btw

        except:
            raise RuntimeError("Error during transmitted load calculation")

        return load_change

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

    def get_serving_duration2(self, packet):
        """
        Change the status of the packet once the serving process starts.
        """
        RB_arr = packet.server.RB_list
        try:
            t_end_temp = np.ceil (packet.t_last_start)
            load_change = self.get_load_change2 (RB_arr, packet.t_last_start, t_end_temp)

            while load_change < packet.remaining_load:
                t_end_temp += 1
                load_change = self.get_load_change2(RB_arr, packet.t_last_start, t_end_temp)

            r_last = self.get_load_change2(RB_arr, t_end_temp-1, t_end_temp)
            t_delta = (load_change - packet.remaining_load) / r_last
            t_end = t_end_temp - t_delta

            assert(np.isclose(packet.remaining_load , self.get_load_change2(RB_arr, packet.t_last_start, t_end)))
            packet.t_finish_real = t_end
            packet.t_finish = packet.t_finish_real
        except:
            raise RuntimeError("Error during get_serving_duration")

    def get_serving_duration(self, packet):
        """
        Change the status of the packet once the serving process starts.
        """
        RB_arr = packet.server.RB_list
        #t_s = self.user.sim_param.T_S
        t_temp = packet.t_last_start
        if (packet.t_last_start % 1.) == 0:
            t_temp = packet.t_last_start
            t_arr = np.arange(t_temp, t_temp + 1)
            r_temp = self.get_load_change(RB_arr, t_arr)
        else:
            t_1 = packet.t_last_start % 1.
            t_temp = int(packet.t_last_start - t_1)
            t_arr = np.arange(t_temp, t_temp + 1)
            r_temp0 = self.get_load_change(RB_arr, t_arr)
            r_temp = r_temp0 * (1.-t_1)/1.

        try:
            while r_temp < packet.remaining_load:
                t_temp += 1
                t_arr = np.arange(t_temp, t_temp + 1)
                r_temp += self.get_load_change(RB_arr, t_arr)

        except:
            raise RuntimeError("Error during get_serving_duration")


        r_last = self.get_load_change(RB_arr, t_arr)
        t_last = (packet.remaining_load-(r_temp-r_last))/(r_last/1.)
        t_est = t_temp+t_last
        #packet.estimated_duration = t_est - packet.slicesim.sim_state.now
        #packet.occupation_duration = t_temp+t_s-packet.slicesim.sim_state.now
        packet.t_finish_real = t_est#+packet.slicesim.sim_state.t_round_start
        packet.t_finish = packet.t_finish_real

    def update_remaining_load2(self, packet):
        """
        substract load change since the latest serving from remaining load
        return tp = load_change / duration
        """
        RB_arr = packet.server.RB_list  # function is called before RB_list is changed
        t_start = (packet.t_arrival + (packet.d_wait + packet.d_served))  # starting time of latest serve
        load_change = self.get_load_change2(RB_arr, t_start, packet.slicesim.sim_state.now)
        packet.remaining_load -= load_change

        if packet.remaining_load < 0:
            raise RuntimeError("Remaining load can't be negative!")

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(load_change) / float(packet.slicesim.sim_state.now-t_start)
            return tp  # throughput in kilobits  per second: bits / ms
        else:
            return float(0)

    def update_remaining_load(self, packet):
        """
        substract load change since the latest serving from remaining load
        return tp = load_change / duration
        """
        #t_s = self.user.sim_param.T_S
        RB_arr = packet.server.RB_list  # function is called before RB_list is changed
        t_start = (packet.t_arrival + (packet.d_wait + packet.d_served))  # starting time of latest serve

        if (t_start % 1) > 0.0000001:
            t_0 = (t_start % 1)
            t_1 = int(t_start - t_0)
            t_arr = np.arange(t_1, t_1 + 1, dtype=int)
            r_temp0 = self.get_load_change(RB_arr, t_arr) * t_0/1.
        else:
            t_1 = int(t_start)
            r_temp0 = 0

        t_arr = np.arange(t_1, packet.slicesim.sim_state.now, dtype=int)
        r_temp = self.get_load_change(RB_arr, t_arr)
        packet.remaining_load -= (r_temp - r_temp0)  # rtemp0 is not received part
        if packet.remaining_load < 0:
            raise RuntimeError("Remaining load can't be negative!")

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(r_temp - r_temp0) / float(packet.slicesim.sim_state.now-t_start)
            return tp  # throughput in kilobits  per second
        else:
            return float(0)

    def get_remaining_load(self, packet):
        """
        returns the remaining load without changing anything
        initially same as update_remaining_load
        """
        RB_arr = packet.server.RB_list  # function is called before RB_list is changed
        t_start = (packet.t_arrival + (packet.d_wait + packet.d_served))  # starting time of latest serve

        if (t_start % 1) > 0.0001:
            t_0 = (t_start % 1)
            t_1 = int(t_start - t_0)
            t_arr = np.arange(t_1, t_1 + 1)
            r_temp0 = self.get_load_change(RB_arr, t_arr) * t_0/1.
        else:
            t_1 = int(t_start)
            r_temp0 = 0

        t_arr = np.arange(t_1, packet.slicesim.sim_state.now)
        r_temp = self.get_load_change(RB_arr, t_arr)
        return packet.remaining_load - (r_temp - r_temp0)  # rtemp0 is not received part

    def get_throughput_rt(self, packet):
        """
        NOT USED
        returns throughput for round termination event without changing anything
        """
        RB_arr = packet.server.RB_list  # function is called before RB_list is changed
        t_start = (packet.t_arrival + (packet.d_wait + packet.d_served))  # starting time of latest serve

        if (t_start % 1) > 0.0001:
            t_0 = (t_start % 1)
            t_1 = int(t_start - t_0)
            t_arr = np.arange(t_1, t_1 + 1)
            r_temp0 = self.get_load_change(RB_arr, t_arr) * t_0/1.
        else:
            t_1 = int(t_start)
            r_temp0 = 0

        t_arr = np.arange(t_1, packet.slicesim.sim_state.now)
        r_temp = self.get_load_change(RB_arr, t_arr)

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(r_temp - r_temp0)/float(packet.slicesim.sim_state.now-t_start)  # total served size over time
            return tp  #throughput
        else:
            return float(0)

    def get_throughput_sc(self, packet):
        """
        Only when service is completed,
        tp in Kbps
        """
        t_start = (packet.t_arrival + (packet.d_wait + packet.d_served))  # starting time of latest serve

        if packet.slicesim.sim_state.now-t_start != 0:
            tp = float(packet.remaining_load)/float(packet.slicesim.sim_state.now-t_start)  # total served size over time
            return tp  #throughput
        else:
            return float(0)

    def get_throughput_sc_pauseless(self, packet):
        """
        Only when service is completed, counts the datarate when packet is served.
        tp in Kbps
        """
        #t_start = packet.t_last_start # int(round(packet.t_arrival + (packet.d_wait + packet.d_served)))  # starting time of latest serve
        t_start = packet.t_start

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

