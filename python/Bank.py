class Bank:
    def __init__(self, id, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate):
        self.id = id
        self.capacity = capacity
        self.cumulativeShock = cumulativeShock
        self.solventNeighbors = solventNeighbors
        self.status = status
        self.insolventTimestep = insolventTimestep
        self.shockToPropagate = shockToPropagate

    def checkNeighborSolvency(self, Graph, banks):
        solventNeighbors = 0
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborID in range(0, len(neighbors)):
            ## define the neighbor we're looking at
            neighbor = Graph.node[neighborID]
            neighborBank = banks[neighbor['bankID']]
            ## if that neighbor's status is 1, increment the solventNeighbors variable by 1
            if neighborBank.status == 1: solventNeighbors = solventNeighbors + 1

            ## reset in both graph and list
            self.solventNeighbors = solventNeighbors

    def checkSelfSolvency(self, timestep):
        if self.cumulativeShock >= self.capacity and self.status == 1:
            self.status = 0
            self.insolventTimestep = timestep

    def calculateShockToPropagate(self):
        ## We're working with integer division, so we need to multiply the numerator by 1.0 to make it a double/float/decimal
        if self.status == 0 and self.solventNeighbors > 0:
            self.shockToPropagate = (1.0 * self.cumulativeShock + self.capacity) / self.solventNeighbors

    def propagateToNeighbors(self, Graph, banks):
        solventNeighbors = 0
        ## acquire all neighbors for the current nodeID
        neighbors = Graph.neighbors(self.id)
        ## loop through all neighbors of current nodeID
        for neighborID in range(0, len(neighbors)):
            ## define the neighbor we're looking at
            neighbor = Graph.node[neighborID]
            neighborID = neighbor['bankID']
            neighborBank = banks[neighborID]
            if neighborBank.status == 0: continue
            else:
                neighborBank.cumulativeShock += self.shockToPropagate
