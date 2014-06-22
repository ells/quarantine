
## note that this is duplicated in network generation for the time being
## it won't run here because numberOfNodes is not yet a global variable.
## Once I figure out how to string these files together, we'll clear it out 
## of the netGen.py file and keep it here where it belongs.

def checkSolvency(Graph, timestep):
    ## loop through all nodes
    for nodeID in range(0, numberOfNodes-1):
        ## record capacity
        capacity = Graph.node[nodeID]['capacity']
        ## record cumulative shock
        cumulativeShock = Graph.node[nodeID]['cumulativeShock']
        ## initialize the number of solvent neighbors
        solventNeighbors = 0;
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(nodeID)
        ## loop through all neighbors of current nodeID
        for neighborID in range(0, len(neighbors)):
            ## define the neighbor we're looking at
            neighbor = Graph.node[neighborID]
            ## if that neighbor's status is 1, increment the solventNeighbors variable by 1
            if neighbor['status'] == 1: solventNeighbors = solventNeighbors + 1
        
        ## perform solvency calculation    
        if capacity < (cumulativeShock / solventNeighbors): 
            ## if a bank is insolvent, change its status to 0
            Graph.node[nodeID]['status'] = 0
            ## and record the current timestep
            Graph.node[nodeID]['insolventTimestep'] = timestep
        