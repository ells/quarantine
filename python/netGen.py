import networkx as nx
from networkx.utils import powerlaw_sequence
import numpy as np
import sim

numberOfNodes = 250
powerLawAlpha = 2
shockSize = 2
targetAssort = -0.2
targetReplicates = 1
assortThresh = 0.01
Graph = nx.Graph()
banks = []
ListsOfBanks = []
ListsOfNetworks = []
timestep = 0

class Bank:
    def __init__(self, id, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate):
        self.id = id
        self.capacity = capacity
        self.cumulativeShock = cumulativeShock
        self.solventNeighbors = solventNeighbors
        self.status = status
        self.insolventTimestep = insolventTimestep
        self.shockToPropagate = shockToPropagate

    def checkNeighborSolvency(self):
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
        if self.cumulativeShock >= self.capacity:
            self.status = 0
            self.insolventTimestep = timestep

    def calculateShockToPropagate(self):
        ## We're working with integer division, so we need to multiply the numerator by 1.0 to make it a double/float/decimal
        if self.status == 0 and self.solventNeighbors > 0:
            self.shockToPropagate = (1.0 * self.cumulativeShock + self.capacity) / self.solventNeighbors

    def propagateToNeighbors(self):
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

def generateNetwork():
    global Graph
    ## use a networkx function to create a degree sequence that follows a power law
    degreeSequence=nx.utils.create_degree_sequence(numberOfNodes,powerlaw_sequence, 100)
    ## use aforementioned degree sequence to configure a pseudograph that contains self-loops & hyper-edges
    pseudoGraph=nx.configuration_model(degreeSequence)
    ## remove hyper (parallel) edges
    Graph = nx.Graph(pseudoGraph)
    ## remove self edges
    Graph.remove_edges_from(Graph.selfloop_edges())
    ## loop through all nodes and set capacity equal to degree
    for bankID in range(0,len(Graph.node)):
        Graph.node[bankID]['bankID'] = bankID;
        Graph.node[bankID]['capacity'] = Graph.degree(bankID)
        Graph.node[bankID]['solventNeighbors'] = Graph.degree(bankID)
        ## right now capacity = degree
        Graph.node[bankID]['cumulativeShock'] = 0
        ## if a bank is solvent, status = 1. When it crashes, status = 0.
        Graph.node[bankID]['status'] = 1
        ## here we set the timestep that the bank becomes insolvent to a big number
        Graph.node[bankID]['insolventTimestep'] = 100000000
        ## here we set the size of the shock to be propagated (zero at sim start)
        Graph.node[bankID]['shockToPropagate'] = 0
    return Graph
  
def generateConnectedPowerLawNetwork():
    ## Use our generateNetwork function to create a sparse graph w/ power law capacities 
    global Graph
    Graph = generateNetwork()

    ## there is no guarantee that the network created above is completely connected
    ## therefore, we'll keep re-making the graph until we get a fully connected one
    while nx.is_connected(Graph) != True:
        Graph = generateNetwork()

def generateBanks():
    global banks
    banks = []
    for nodeID in range(0, numberOfNodes):
        ## for each node, record properties
        bankID = nodeID
        capacity = Graph.node[nodeID]['capacity']
        cumulativeShock = Graph.node[nodeID]['cumulativeShock']
        solventNeighbors = Graph.degree(nodeID)
        status = Graph.node[nodeID]['status']
        insolventTimestep = Graph.node[nodeID]['insolventTimestep']
        shockToPropagate = Graph.node[nodeID]['shockToPropagate']

        ## make the bank according to those properties
        bank = Bank(bankID, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate)
        banks.append(bank)
             
def calculateDegreeAssortativity():
    return nx.degree_assortativity_coefficient(Graph)

def checkGlobalSolvency():
    for nodeID in range(0, numberOfNodes):
        banks[nodeID].checkNeighborSolvency()
        banks[nodeID].checkSelfSolvency(timestep)

def generateMultipleNetworks():
    global banks
    global Graph
    global ListsOfBanks
    global ListsOfNetworks
    ## while we still need to find more networks...
    while len(ListsOfBanks) < targetReplicates:
        ## here we wipe out the existing banks list to get ready for the next bank
        banks = []
        ## and to be safe, we wipe out the existing Graph to make room for the next
        Graph = nx.Graph()

        ## generate a power law network that is connected
        generateConnectedPowerLawNetwork()
        ## make a bank list to match nodes in the power law network we just made
        generateBanks()
        ## globally set the number of solvent neighbors via the fxn specific to the Bank class
        checkGlobalSolvency()
        assortativity = calculateDegreeAssortativity()
        ## measure assortativity of the network and compare to target assortativity
        deltaAssort = np.abs(np.abs(assortativity) - np.abs(targetAssort))

        ## as long as the difference between assortativity and the target assortativity is smaller than a threshold
        if (deltaAssort < assortThresh):
            ## print the assortativity
            print "assortativity =", assortativity
            ## add the list of banks to a global list of banks
            ListsOfBanks.append(banks)
            ## and add the network to a global list of networks
            ListsOfNetworks.append(Graph)


## here is where the code actually executes
generateMultipleNetworks()
## once the banks are made, we start the simulation
sim.setupShocks(shockSize, ListsOfBanks[0], ListsOfNetworks[0])
sim.runTimesteps()

