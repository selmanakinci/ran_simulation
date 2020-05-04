from event import EventChain, PacketArrival, RoundTermination, ServerActivation, ServerDeactivation, RB_Allocation


def simulate_one_slot(self):
    """
    Do one simulation run. Initialize simulation and create first and last event.
    After that, one after another event is processed.
    :return: SliceResult object
    """
    self.sim_state.t_round_start = self.sim_state.now

    # insert first and last event
    self.event_chain_slice_manager.insert(RoundTermination(self, self.sim_state.now + self.slice_param.T_C))

    # insert periodic RB_Allocation events
    t_arr = np.arange(self.sim_state.now, self.sim_state.now + self.slice_param.T_C, self.slice_param.T_SM)
    for t in t_arr:
        self.event_chain_slice_manager.insert(RB_Allocation(self, t))

    # insert packet arrivals from traffic lists of users
    for i in self.user_list:
        tmp = i.traffic_list_dict[self.slice_param.SLICE_ID]
        tmp_traffic_list = filter(lambda item: (
                self.sim_state.now <= item.timestamp < self.sim_state.now + self.slice_param.T_C),
                                  tmp)
        tmp_server = self.server_list_dict[i.user_id]
        for j in tmp_traffic_list:
            tmp_server.event_chain.insert(j)

    # start simulation (run)
    while not self.sim_state.stop:
        # remove upcoming events
        [current_events, current_events_dict] = self.remove_upcoming_events()
        if len(current_events) != len(current_events_dict):
            raise RuntimeError("ERROR: Event to server mapping error.")

        for e in current_events:
            if e.timestamp == 80:
                msa = 3
            if e.priority == 0:
                msa = 3
            if e:
                # if event exists and timestamps are ok, process the event
                if self.sim_state.now <= e.timestamp:
                    self.sim_state.now = e.timestamp

                    if not (e.priority == 4 or e.priority == 5):  # dont count for for slice manager events
                        current_events_dict[e].counter_collection.count_queue()
                    e.process(current_events_dict[e])
                    if e.timestamp % 1000 == 0:
                        print("TIMESTAMP: " + str(e.timestamp) + ",PRIORITY " + str(e.priority))
                else:
                    print("NOW: " + str(self.sim_state.now) + ", EVENT TIMESTAMP: " + str(e.timestamp) + " " + str(
                        e.priority))
                    raise RuntimeError("ERROR: TIMESTAMP OF EVENT IS SMALLER THAN CURRENT TIME.")

            else:
                print("Event chain is empty. Abort")
                self.sim_state.stop = True

    #  gather results for slice_result object and all servers results
    self.server_results = []
    self.server_results_dict = {}
    for i in self.user_list:
        tmp_server = self.server_list_dict[i.user_id]
        self.server_results.append(tmp_server.server_result.gather_results())
        self.server_results_dict.update({i.user_id: self.server_results[-1]})

    self.slice_result.gather_results(self.server_results)
    return self.slice_result
