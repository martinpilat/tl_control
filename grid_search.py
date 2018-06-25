import argparse
import functools
import json
import multiprocessing
import random

from tl_connector import fitness

def evaluate_ind(x, config):
    return sum(fitness(x, config)),

def main():

    parser = argparse.ArgumentParser(description='Evolution of EV charging controllers')
    parser.add_argument('-c', '--config', help='configuration file', type=str, required=True)
    parser.add_argument('-s', '--seed', help='seed of random number generator', type=int, default=-1)

    args = parser.parse_args()

    config = json.load(open(args.config, 'r'))

    log_prefix = config['log_prefix']

    t_min_range = config['time_range']
    threshold_range = config['threshold_range']

    inds = [[t, theta] for t in range(*t_min_range) for theta in range(*threshold_range)]

    random.shuffle(inds)

    print(len(inds))

    pool = multiprocessing.Pool(config['cpus'])

    fit = functools.partial(evaluate_ind, config=config)

    values = pool.map(fit, inds)

    for i, v in zip(inds, values):
        print(i, '->', v)

    json.dump(list(zip(inds, values)), open(f'results/{log_prefix}_all.json', 'w'))

if __name__ == '__main__':
    main()