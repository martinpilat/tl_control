import numpy as np

import nn

class SOTLController:

    def __init__(self, phases, current_phase, t_min, threshold):
        self.phases = phases
        self.current_phase = current_phase
        self.last_phase_change = 0
        self.t_min = t_min
        self.threshold = threshold
        self.values = [0,0,0,0]

    def update_state(self, features):

        sotl_feat = features[-4:]

        for i in range(4):
            self.values[i] += sotl_feat[i]

        self.values[self.current_phase//2] = 0 # for the current phase, the demand is 0
        self.last_phase_change += 1

    def set_parameters(self, t_min, threshold):
        self.t_min = t_min
        self.threshold = threshold

    def next_phase(self):
        if self.last_phase_change*1000 < self.phases[self.current_phase]._duration1:  # phase too short -> cannot change
            return False, self.current_phase

        if self.last_phase_change*1000 >= self.phases[self.current_phase]._duration2: # phase too long -> must change
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        if self.last_phase_change < self.t_min:
            return False, self.current_phase

        if self.values[0] > self.threshold or self.values[2] > self.threshold:
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        return False, self.current_phase

class NNController:

    def __init__(self, phases, current_phase):
        self.phases = phases
        self.current_phase = current_phase
        self.last_phase_change = 0
        self.features = None
        self.network: nn.NeuralNetwork = None
        self.ph_zeros = [0,0,0,0]
        self.sotl_values = [0.0, 0.0, 0.0, 0.0]
        self.last_states = []

    def update_state(self, features):
        self.last_phase_change += 1
        self.last_states.append(features)
        if len(self.last_states) > 300:
            self.last_states = self.last_states[-300:]

        last = np.array(self.last_states)
        last_avg = np.mean(last, axis=0)

        feat_veh = features[:4]
        feat_jam = features[4:8]
        feat_sotl = features[8:]

        for i in range(4):
            self.ph_zeros[i] = self.ph_zeros[i] + 1 if features[i] == 0 else 0
            self.sotl_values[i] += feat_sotl[i]

        phase_idx = self.current_phase // 2
        self.sotl_values[phase_idx] = 0

        phase_idx = self.current_phase//2

        feat_rel = list(map(lambda x: x[0]/x[1] - 1 if x[1] != 0 else 0, zip(features, last_avg)))

        feat_veh = feat_veh[phase_idx:] + feat_veh[:phase_idx]
        feat_jam = feat_jam[phase_idx:] + feat_jam[:phase_idx]
        feat_sotl = self.sotl_values[phase_idx:] + self.sotl_values[:phase_idx]

        zeros = self.ph_zeros[phase_idx:] + self.ph_zeros[:phase_idx]

        max_phase_len = self.phases[self.current_phase]._duration2

        self.features = feat_veh + feat_jam + feat_sotl + zeros + [self.last_phase_change/max_phase_len]

    def set_network(self, network):
        self.network = network

    def next_phase(self):
        if self.last_phase_change*1000 < self.phases[self.current_phase]._duration1:  # phase too short -> cannot change
            return False, self.current_phase

        if self.last_phase_change*1000 >= self.phases[self.current_phase]._duration2: # phase too long -> must change
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        if self.network.eval_network(self.features)[0] > 0:
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        return False, self.current_phase

class EnsembleController(NNController):

    def __init__(self, phases, current_phase, sotl_min_time, sotl_threshold, act_min_time, act_max_time):
        super().__init__(phases, current_phase)
        self.min_time = sotl_min_time
        self.threshold = sotl_threshold
        self.act_min_time = act_min_time
        self.act_max_time = act_max_time
        self.sotl_values = [0.0, 0.0, 0.0, 0.0]

    def update_state(self, features):

        self.last_phase_change += 1
        self.last_states.append(features)
        if len(self.last_states) > 300:
            self.last_states = self.last_states[-300:]

        feat_sotl = features[8:]

        for i in range(4):
            self.ph_zeros[i] = self.ph_zeros[i] + 1 if features[i] == 0 else 0
            if self.ph_zeros[i] > 5:
                self.ph_zeros[i] = 5
            self.sotl_values[i] += feat_sotl[i]

        phase_idx = self.current_phase // 2
        self.sotl_values[phase_idx] = 0

        sotl_switch = 1.0 if self.last_phase_change >= self.min_time and \
                             (self.sotl_values[0] > self.threshold or self.sotl_values[2] > self.threshold) else 0.0

        if (self.current_phase == 2 or self.current_phase == 6) and self.last_phase_change >= 5:
            sotl_switch = 1.0

        feat_sotl = self.sotl_values[phase_idx:] + self.sotl_values[:phase_idx]
        feat_sotl = list(map(lambda x: x/self.threshold, feat_sotl))

        zeros = self.ph_zeros[phase_idx:] + self.ph_zeros[:phase_idx]
        zeros = list(map(lambda x : x/5, zeros))

        actuated_switch = 1.0 if self.last_phase_change > self.act_max_time \
                                 or (zeros[0] > 0 and self.last_phase_change > self.act_min_time) else 0.0

        self.features = [sotl_switch, actuated_switch] + feat_sotl + zeros

    def next_phase(self):

        if self.last_phase_change >= self.act_max_time or (self.current_phase % 2 == 1 and self.last_phase_change >= 3): # phase too long -> must change
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        if self.last_phase_change < self.act_min_time:  # phase too short -> cannot change
            return False, self.current_phase

        if self.network.eval_network(self.features)[0] > 0:
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            self.last_phase_change = 0
            return True, self.current_phase

        return False, self.current_phase