This scenario simulates the situation where there is stronger traffic in the 
east<->west direction and lighter traffic in the north<->south direction in 
the beginning of the simulation and it switches over during the simulation. 
Specifically, in the first 10 minutes, there are 1,200 cars coming each hour 
through each road on E or W, and 600 cars coming on each road on N or S.
Afterwards every 5 minutes, the number of cars on each road in the E<->W 
direction is reduced by 60 per hour and the number of cars on each road in
the N<->S direction is increased by the same amount. Thus, the overall traffic
intensity stays the same in the simulation. 

The cars decide on each junction whether to go straight (80%), turn left (10%),
 or turn right (10%).  

The grid was generated by the `generate_grid.py` file in the root directory. 

The scenario is created from the files in this directory. The flows are 
specified in the `grid.sc2.jtr.flows.xml` file. The JTR router is used to 
create the routes. The turn probabilities can be set in the 
`scenario2.jtrconfig.xml` as the `turn-defaults` parameter (the numbers are 
probabilities for right turn, straight, and left turn respectively).

In order to recreate the routes (possibly with a different seed) simply run

````bash
    jtrrouter -c scenario2.jtrconfig.xml 
````