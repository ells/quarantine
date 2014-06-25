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
        solventNeighbors = self.capacity
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborID in range(0, len(neighbors)):
            ## define the neighbor we're looking at
            neighbor = Graph.node[neighborID]
            neighborBank = banks[neighbor['bankID']]
            ## if that neighbor's status is dead or failed, then decrement the node's degree
            if neighborBank.status == "dead" or neighborBank.status == "failed": solventNeighbors -= 1
            ## reset in both graph and list
            self.solventNeighbors = solventNeighbors

    def updateStatus(self, timestep):
        ## update status for exposed/solvent banks that DO NOT fail
        if (self.status == "solvent" or "exposed") and (self.capacity > self.cumulativeShock > 0): self.status = "exposed"

        ## update status for solvent/exposed banks that have failed
        if (self.cumulativeShock >= self.capacity) and (self.status == "solvent" or self.status == "exposed"): self.status = "fail"

    def killBank(self):
        if self.status == "fail": self.status = "dead"


    def calculateShockToPropagate(self):
        ## We're working with integer division, so we need to multiply the numerator by 1.0 to make it a double/float/decimal
        if self.status == "fail" and self.solventNeighbors > 0:
            self.shockToPropagate = (1.0 * self.cumulativeShock + self.capacity) / self.solventNeighbors

    def propagateToNeighbors(self, Graph, banks):
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborID in range(0, len(neighbors)):
            ## define the neighbor we're looking at
            neighbor = Graph.node[neighborID]
            neighborID = neighbor['bankID']
            neighborBank = banks[neighborID]
            if (neighborBank.status == "solvent" or "exposed"): neighborBank.cumulativeShock += self.shockToPropagate
