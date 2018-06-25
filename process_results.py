import tl_connector
import nn

sc1_best_sols = ['10437', '14111', '15054', '16515', '23350']
sc2_best_sols = ['9497', '14059', '17327', '24205', '32514']
sc3_best_sols = ['1880', '3740', '5218', '7442', '11489']

best_sols = map(lambda x: f'sc3_ens_best_sol_{x}.npy', sc3_best_sols)

for bs in best_sols:
    import numpy as np
    import json

    net = nn.NeuralNetwork([10, 5, 1], [nn.relu, nn.tanh])
    ind = np.load(f'results/{bs}')

    config = json.load(open('configs/config_sc3_ens.json'))

    fit = tl_connector.fitness(ind, config=config)
    print(fit)
    print(fit[0] + fit[1])