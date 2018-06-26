# Evolution of Traffic Light Controllers

This repository contains the source codes used to run the experiments in the 
paper submitted to the ICTAI 2018 conference entitled "Evolving Ensembles of 
Traffic Lights Controllers".

There are three directories -- `configs`, `scenarios`, and `results`. 

The `configs` directory contains the configurations used to run the experiments. 
The naming of the files follows a simple convention -- 
`config_sc<n>_<type>.json`, where `<n>` is the number of the scenario (`1`, `2`,
or `3` -- see bellow), and `<type>` is the type of controller to be used -- 
`ens` for the ensemble controllers, `grid` for the grid search of the SOTL 
controller and `ea` for the evolution of neural network controllers (not 
presented in the paper).

The `scenarios` directory contains the scenarios used in the experiments. See 
the README files in the directories for more information about the traffic flows.
The most important files here are the `<type>.sumocfg` ones. Here, `<type>` 
expresses the type of controller used by SUMO. The meaning is as follows:

- none - the default SUMO controller
- `actuated_tl` - the traffic actuated traffic lights 
- `adapted_tl` - the traffic lights adapted by the Webster's formula
- `ea` - the traffic lights controlled by the evolved NN (not presented in the
paper, to be used in conjunction with the `NNController`)
- `sotl` - the traffic lights controlled by the SOTL algorithm (for use with 
`SOTLController`)
- `ens` - the traffic lights controller by the ensemble controller described 
in the paper (to be used with `EnsembleController`)

The `results` directory contains the best evolved controllers from the five runs
in each of the scenarios. An example how to use them is in the 
`process_results.py` file.

## The source codes

This repository also contains a number of source codes.

- `controllers.py` - contains the implementation of the controllers themselves
- `evolution.py` - contains the implementation of the evolutionary algorithm to 
tune the weights of the neural networks
- `grid_search.py` - implements the grid search algorithm for the tuning of the 
SOTL controller
- `nn.py` - contains a simple implementation of a neural network
- `process_results.py` - runs the best solution in SUMO and prints the fitness
- `tl_connector.py` - implements the interface between the evolution and SUMO
and the evaluation of the fitness function

## Running the sources

If you want to run the evolution or grid search, just start the particular 
scripts with `-c <config_file>` parameter. You may need to change the path to 
your SUMO installation in the `tl_connector.py` file (or set `SUMO_HOME` 
environmental variable). 

The TraCI interface (for connecting Python and SUMO) is unfortunately not thread
safe. As the evaluation of the fitness function is done in parallel, it means 
the evolution sometimes crashes, because the port used by TraCI, is already used 
by another instance (TraCI tries to find a free port, every time it starts a new
instance of SUMO, if two instances do it at the same time, they may both try
to use the same one).  

Some of the experiments presented in the paper are not directly implemented
here, because they were done during the development. Most importantly, the 
manual ensembles are not here, but can be easily re-created by changing the 
`EnsembleController` to perform the respective operation on the first two 
inputs.