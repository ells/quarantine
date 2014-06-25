import networkx as nx
from networkx.utils import powerlaw_sequence
import numpy as np
import copy as cp
from bank import Bank
from sim import Simulation

numberOfNodes = 250
powerLawAlpha = 2
shockSize = 25
targetAssort = -0.2
targetReplicates = 1
assortThresh = 0.01
assortativity = 0
Graph = nx.Graph()
banks = []
ListsOfBanks = []
ListsOfNetworks = []
timestep = 0
simCount = 100
simulations = []
bankruptBanks = 0

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
        ## solvent = normal
        ## exposed = cumulative shock is less than capacity
        ## fail = recently failed, about to spread
        ## dead = can no longer spread or receive shocks
        Graph.node[bankID]['status'] = 'solvent'
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

def generateMultipleNetworks():
    global assortativity
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
        assortativity = calculateDegreeAssortativity()
        ## measure assortativity of the network and compare to target assortativity
        deltaAssort = np.abs(np.abs(assortativity) - np.abs(targetAssort))

        ## as long as the difference between assortativity and the target assortativity is smaller than a threshold
        if (deltaAssort < assortThresh):
            ## add the list of banks to a global list of banks
            ListsOfBanks.append(banks)
            ## and add the network to a global list of networks
            ListsOfNetworks.append(Graph)


generateMultipleNetworks()
print 'timestep', 'shockSize', 'shockCount', 'failedBanks', 'lostCapacity' , 'assortativity'

for simID in range(0,simCount):
    timestep = 0
    banksCopy = cp.deepcopy(ListsOfBanks[0])
    networkCopy = cp.deepcopy(ListsOfNetworks[0])

    totalCapacity = 0
    for bankID in range(0, len(banksCopy)): totalCapacity += banksCopy[bankID].capacity

    simulation = Simulation(id, banksCopy, networkCopy, shockSize, [], timestep, assortativity, totalCapacity)
    simulations.append(simulation)
    simulations[simID].setupShocks(shockSize, banksCopy, networkCopy)
    simulations[simID].runTimesteps(timestep)