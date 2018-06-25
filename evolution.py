import argparse
import json
import multiprocessing
import os
import pickle

import numpy
from deap import tools, base, cma, algorithms, creator

from tl_connector import fitness
import nn

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

def evaluate_ind(x, config):
    return sum(fitness(x, config)),

def main():

    parser = argparse.ArgumentParser(description='Evolution of EV charging controllers')
    parser.add_argument('-c', '--config', help='configuration file', type=str, required=True)
    parser.add_argument('-s', '--seed', help='seed of random number generator', type=int, default=-1)

    args = parser.parse_args()

    config = json.load(open(args.config, 'r'))

    seed = args.seed
    if seed == -1:
        seed = numpy.random.randint(0, 1_000_000_000)

    log_prefix = config['log_prefix']

    net = nn.NeuralNetwork([17, 5, 1], nn.relu) # create network to get vectorized size, activations do not matter
    if config.get('controller_type', 'nn') == 'ensemble':
        net = nn.NeuralNetwork([10, 5, 1], nn.relu)
    N = net.vectorized_size()

    numpy.random.seed(seed)

    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    toolbox = base.Toolbox()

    pool = multiprocessing.Pool(config['cpus'])
    toolbox.register('map', pool.map)
    toolbox.register("evaluate", evaluate_ind, config=config)

    strategy = cma.Strategy(centroid=0.1 * numpy.random.randn(N), sigma=config['sigma'], lambda_=config['pop_size'])
    toolbox.register("generate", strategy.generate, creator.Individual)
    toolbox.register("update", strategy.update)

    pop, log = algorithms.eaGenerateUpdate(toolbox, ngen=config['max_gen'], stats=stats, halloffame=hof)

    if not os.path.isdir('results'):
        os.mkdir('results')

    numpy.save(f'results/{log_prefix}_best_sol_{seed}.npy', hof.items[0])
    pickle.dump(log, open(f'results/{log_prefix}_stats_{seed}.pkl', 'wb'))
    pickle.dump(pop, open(f'results/{log_prefix}_pop_{seed}.pkl', 'wb'))
    with open(f'results/{log_prefix}_logbook_{seed}.txt', 'w') as logfile:
        logfile.write(str(log))

if __name__ == '__main__':
    main()