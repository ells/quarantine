class Bank:
    def __init__(self, id, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate):
        self.id = id
        self.capacity = capacity
        self.cumulativeShock = cumulativeShock
        self.solventNeighbors = solventNeighbors
        self.status = status
        self.insolventTimestep = insolventTimestep
        self.shockToPropagate = shockToPropagate

    def updateSolventNeighbors(self, Graph, banks):
        potentialNeighbors = 0
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborIndex in range(0, len(neighbors)):
            neighborID = neighbors[neighborIndex]
            neighbor = banks[neighborID]
            ## if that neighbor's status is dead or failed, then decrement the node's degree
            if neighbor.status == "exposed" or neighbor.status == "solvent": potentialNeighbors += 1
            ## reset in both graph and list
            self.solventNeighbors = potentialNeighbors

    def updateStatus(self, timestep):
        ## update status for exposed/solvent banks that DO NOT fail
        if (self.status == "solvent" or "exposed") and (self.capacity > self.cumulativeShock > 0): self.status = "exposed"

        ## update status for solvent/exposed banks that have failed
        if (self.cumulativeShock >= self.capacity) and (self.status == "solvent" or self.status == "exposed"):
            self.insolventTimestep = timestep
            self.status = "fail"

    def killBank(self):
        if self.status == "fail": self.status = "dead"

    def calculateShockToPropagate(self, capacityMultiplier, shockMultiplier):
        ## We're working with integer division, so we need to multiply the numerator by 1.0 to make it a double/float/decimal
        if self.status == "fail" and self.solventNeighbors > 0:
            self.shockToPropagate = ((capacityMultiplier * self.capacity) + (shockMultiplier * self.cumulativeShock)) / self.solventNeighbors

    def propagateToNeighbors(self, Graph, banks):
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborIndex in range(0, len(neighbors)):
            neighborID = neighbors[neighborIndex]
            neighbor = banks[neighborID]

            if neighbor.status == "solvent" or neighbor.status == "exposed": neighbor.cumulativeShock += self.shockToPropagate
