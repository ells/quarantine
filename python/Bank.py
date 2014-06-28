class Bank:
    ## a class is an independent instantiation of a custom-made object in python
    def __init__(self, id, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate, statusID):
        ## the __init__(self, blah, blah, blah) is the mandatory way of initializing a custom class
        ## the "self" is just a way of associating each of the variables that come after it in the __init__() to that particular object
        ## therefore, each bank has its own ID, capacity, cumulativeShock, solventNeighbors, status, insolventTimesteps, and shockToPropagate
        self.id = id
        self.capacity = capacity
        self.cumulativeShock = cumulativeShock
        self.solventNeighbors = solventNeighbors
        self.status = status
        self.insolventTimestep = insolventTimestep
        self.shockToPropagate = shockToPropagate
        self.statusID = 1

    def updateSolventNeighbors(self, graph, banks):
        potentialNeighbors = 0
        ## acquire all neighbors for the current nodeID
        neighbors = graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborIndex in range(0, len(neighbors)):
            ## here we reference the neighbor in the neighbors list
            neighborID = neighbors[neighborIndex]
            ## then we use the neighborID to reference the specific bank in the master banks list
            neighbor = banks[neighborID]
            ## if that neighbor's status is dead or failed, then decrement the node's degree
            if neighbor.status == "exposed" or neighbor.status == "solvent": potentialNeighbors += 1
            ## reset in both graph and list
            self.solventNeighbors = potentialNeighbors
            self.capacity = self.solventNeighbors

    def updateStatus(self, timestep):
        ## update status for exposed/solvent banks that DO NOT fail
        ## note the awesomesauce condensed conditionals here...not many languages can pull this off
        if (self.status == "solvent" or "exposed") and (self.capacity > self.cumulativeShock > 0):
            self.status = "exposed"

        ## update status for solvent/exposed banks that have failed
        if (self.cumulativeShock >= self.capacity) and (self.status == "solvent" or self.status == "exposed"):
            self.insolventTimestep = timestep
            self.status = "fail"

    def killBank(self):
        ## super simple, kill the failed banks, assuming that they've already propagated
        ## because we don't explicitly check to see if they've propagated, this fxn is sensitive to ordering
        if self.status == "fail": self.status = "dead"

    def calculateShockToPropagate(self, capacityMultiplier, shockMultiplier):
        ## if the banks has failed AND it still has solvent neighbors then calculate the shock to be propagated
        ## we have to check for the solvent neighbors...otherwise we'd be dividing by zero and cause the apocalypse
        if self.status == "fail" and self.solventNeighbors > 0:
            self.shockToPropagate = (1.0 * (1.0 * capacityMultiplier * self.capacity) + (1.0 * shockMultiplier * self.cumulativeShock)) / self.solventNeighbors

    def propagateToNeighbors(self, graph, banks):
        ## acquire all neighbors for the current nodeID
        neighbors = graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborIndex in range(0, len(neighbors)):
            ## find the neighbor in the neighbors list
            neighbor = neighbors[neighborIndex]
            ## then find that neighbor in the master list of banks
            neighborBank = banks[neighbor]

            ## if the neighboring bank is still active, propagate the shock to that bank by adding to its cumulative shock
            if neighborBank.status == "solvent" or neighborBank.status == "exposed":
                neighborBank.cumulativeShock += self.shockToPropagate