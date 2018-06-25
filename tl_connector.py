import sys
import os
import random
import tempfile
import time

import controllers
import nn

SUMO_HOME='C:/Program Files (x86)/DLR/Sumo/'

if os.environ.get('SUMO_HOME'):
    SUMO_HOME = os.environ.get('SUMO_HOME')


try:
    sys.path.append(os.path.join(SUMO_HOME, "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

print('sys.path', sys.path)

import traci
import traci.constants

def fitness(ind, config):

    controller_type = config.get('controller_type', 'nn')

    (fd, path) = tempfile.mkstemp('.xml', 'tripdata_', dir='temp')

    sumoBinary = checkBinary('sumo')

    for i in range(10): # try connecting multiple times - sometimes the port is taken due to a race condition
        try:
            traci.start([sumoBinary,
                         "-c", config['scenario'],
                         "--tripinfo-output", path,
                         "--tripinfo-output.write-unfinished",
                         "--no-step-log"])
        except:
            time.sleep(random.random()*10)
            continue
        break
    else:
        return None

    traffic_lights :traci._trafficlight.TrafficLightDomain = traci.trafficlight
    detectors : traci._lanearea.LaneAreaDomain = traci.lanearea

    tl_ids = traffic_lights.getIDList()
    tl_ids = [tl for tl in tl_ids if len(traffic_lights.getRedYellowGreenState(tl)) > 1] #only consider internal tl
    det_ids = detectors.getIDList()

    lanes_det = {detectors.getLaneID(det) : det for det in det_ids}
    tl_lanes = {tl: traffic_lights.getControlledLanes(tl) for tl in tl_ids}

    tl_det = {tl: list(sorted(set(map(lambda x: lanes_det[x], tl_lanes[tl])))) for tl in tl_ids}

    ph1_idx = [3,4,5,6,7,8]
    ph2_idx = [5,8]
    ph3_idx = [0,1,2,9,10,11]
    ph4_idx = [2,11]

    #dirty computation of normalization for SOTL
    phase_counts = [1]*12
    phase_counts[5] = 2
    phase_counts[8] = 2
    phase_counts[2] = 2
    phase_counts[11] = 2

    ph1_weight = sum([1/phase_counts[x] for x in ph1_idx])
    ph2_weight = sum([1/phase_counts[x] for x in ph2_idx])
    ph3_weight = sum([1/phase_counts[x] for x in ph3_idx])
    ph4_weight = sum([1/phase_counts[x] for x in ph4_idx])

    for det in detectors.getIDList():
        detectors.subscribe(det, [traci.constants.JAM_LENGTH_VEHICLE, traci.constants.LAST_STEP_VEHICLE_NUMBER])

    if controller_type == 'nn':
        tl_controllers = {tl: controllers.NNController(traffic_lights.getCompleteRedYellowGreenDefinition(tl)[-1]._phases,
                                                       traffic_lights.getPhase(tl)) for tl in tl_ids}

        for ctr in tl_controllers.values():
            net = nn.NeuralNetwork([17, 5, 1], [nn.relu, nn.tanh])
            net.set_weights(ind)
            ctr.set_network(net)
    elif controller_type == 'sotl':
        tl_controllers = {tl: controllers.SOTLController(traffic_lights.getCompleteRedYellowGreenDefinition(tl)[-1]._phases,
                                                         traffic_lights.getPhase(tl), None, None) for tl in tl_ids}

        for ctr in tl_controllers.values():
            ctr.set_parameters(ind[0], ind[1])
    elif controller_type == 'ensemble':
        tl_controllers = {tl: controllers.EnsembleController(traffic_lights.getCompleteRedYellowGreenDefinition(tl)[-1]._phases,
                                                             traffic_lights.getPhase(tl),
                                                             config['sotl_min_time'], config['sotl_threshold'],
                                                             config['act_min_time'], config['act_max_time']
                                                             ) for tl in tl_ids}

        for ctr in tl_controllers.values():
            net = nn.NeuralNetwork([10, 5, 1], [nn.relu, nn.tanh])
            net.set_weights(ind)
            ctr.set_network(net)

    for i in range(10000):
        if i > 100 and traci.vehicle.getIDCount() == 0:
            break

        traci.simulationStep()

        detector_values = detectors.getSubscriptionResults()

        for tl in tl_ids:

            jam_length = list(map(lambda x: detector_values[x][traci.constants.JAM_LENGTH_VEHICLE], tl_det[tl]))
            veh_num = list(map(lambda x: detector_values[x][traci.constants.LAST_STEP_VEHICLE_NUMBER], tl_det[tl]))

            jl_ph1 = sum(map(lambda x: jam_length[x], ph1_idx))/(5*len(ph1_idx))
            jl_ph2 = sum(map(lambda x: jam_length[x], ph2_idx))/(5*len(ph2_idx))
            jl_ph3 = sum(map(lambda x: jam_length[x], ph3_idx))/(5*len(ph3_idx))
            jl_ph4 = sum(map(lambda x: jam_length[x], ph4_idx))/(5*len(ph4_idx))

            vh_ph1 = sum(map(lambda x: veh_num[x], ph1_idx))/(5*len(ph1_idx))
            vh_ph2 = sum(map(lambda x: veh_num[x], ph2_idx))/(5*len(ph2_idx))
            vh_ph3 = sum(map(lambda x: veh_num[x], ph3_idx))/(5*len(ph3_idx))
            vh_ph4 = sum(map(lambda x: veh_num[x], ph4_idx))/(5*len(ph4_idx))

            sotl_ph1 = sum(map(lambda x: veh_num[x]/phase_counts[x], ph1_idx))/(5*ph1_weight)
            sotl_ph2 = sum(map(lambda x: veh_num[x]/phase_counts[x], ph2_idx))/(5*ph2_weight)
            sotl_ph3 = sum(map(lambda x: veh_num[x]/phase_counts[x], ph3_idx))/(5*ph3_weight)
            sotl_ph4 = sum(map(lambda x: veh_num[x]/phase_counts[x], ph4_idx))/(5*ph4_weight)

            tl_feat = [vh_ph1, vh_ph2, vh_ph3, vh_ph4, jl_ph1, jl_ph2, jl_ph3, jl_ph4, sotl_ph1, sotl_ph2, sotl_ph3, sotl_ph4]
            tl_controllers[tl].update_state(tl_feat)
            (next_phase, phase_id) = tl_controllers[tl].next_phase()
            if next_phase:
                traffic_lights.setPhase(tl, phase_id)

    traci.close()

    import xml.etree.ElementTree as ET
    import numpy as np

    root = ET.parse(path)
    losses = np.mean([float(e.attrib['timeLoss']) for e in root.findall('./tripinfo')])
    depart_delays = np.mean([float(e.attrib['departDelay']) for e in root.findall('./tripinfo')])

    os.close(fd)
    os.remove(path)

    return losses, depart_delays

if __name__ == '__main__':
    import numpy as np
    import json
    net = nn.NeuralNetwork([10, 5, 1], [nn.relu, nn.tanh])
    ind = np.load('results/sc1_ens_best_sol_14111.npy')

    config = json.load(open('configs/config_sc1_ens.json'))

    fit = fitness(ind, config=config)
    print(fit)
    print(fit[0] + fit[1])