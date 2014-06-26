import networkx as nx
from networkx.utils import powerlaw_sequence
import numpy as np
import copy as cp
from bank import Bank
from sim import Simulation

numberOfNodes = 100
powerLawAlpha = 2
shockSize = 25
targetAssort = -0.2
targetReplicates = 1
assortThresh = 0.01
assortativity = 0
banks = []
timestep = 0
simCount = 1000
simulations = []
capacityMultipler = 0.25
shockMultiplier = 0.25

def generateNetwork():
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
        Graph.node[bankID]['bankID'] = bankID
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
    graph = generateNetwork()

    ## there is no guarantee that the network created above is completely connected
    ## therefore, we'll keep re-making the graph until we get a fully connected one
    while nx.is_connected(graph) != True:
        graph = generateNetwork()
    return graph

def generateBanks(graph):
    banks = []
    for nodeID in range(0, numberOfNodes):
        ## for each node, record properties
        bankID = nodeID
        capacity = graph.node[nodeID]['capacity']
        cumulativeShock = graph.node[nodeID]['cumulativeShock']
        solventNeighbors = graph.degree(nodeID)
        status = graph.node[nodeID]['status']
        insolventTimestep = graph.node[nodeID]['insolventTimestep']
        shockToPropagate = graph.node[nodeID]['shockToPropagate']

        ## make the bank according to those properties
        bank = Bank(bankID, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate)
        banks.append(bank)
    return banks
             
def calculateDegreeAssortativity(graph):
    return nx.degree_assortativity_coefficient(graph)

def generateMultipleNetworks():
    ListsOfBanks = []
    ListsOfNetworks = []
    ## while we still need to find more networks...
    while len(ListsOfBanks) < targetReplicates:
        ## here we wipe out the existing banks list to get ready for the next bank
        banks = []
        ## and to be safe, we wipe out the existing Graph to make room for the next
        graph = nx.Graph()
        ## generate a power law network that is connected
        graph = generateConnectedPowerLawNetwork()
        ## make a bank list to match nodes in the power law network we just made
        banks = generateBanks(graph)
        ## set the number of solvent neighbors via the fxn specific to the Bank class
        assortativity = calculateDegreeAssortativity(graph)
        ## measure assortativity of the network and compare to target assortativity
        deltaAssort = np.abs(np.abs(assortativity) - np.abs(targetAssort))

        ## as long as the difference between assortativity and the target assortativity is smaller than a threshold
        if (deltaAssort < assortThresh):
            ## add the list of banks to a global list of banks
            ListsOfBanks.append(banks)
            ## and add the network to a global list of networks
            ListsOfNetworks.append(graph)

    return ListsOfBanks, ListsOfNetworks


banks_nets_lists = generateMultipleNetworks()
ListsOfBanks = banks_nets_lists[0]
ListsOfNetworks = banks_nets_lists[1]

print 'timestep', 'shockSize', 'shockCount', 'failedBanks', 'lostCapacity', 'assortativity'

for simID in range(0,simCount):
    timestep = 0
    ## make copies of banks and nets so they don't change
    banksCopy = cp.deepcopy(ListsOfBanks[0])
    networkCopy = cp.deepcopy(ListsOfNetworks[0])

    ## count of the total capacity of the financial network
    totalCapacity = 0
    for bankID in range(0, len(banksCopy)):
        totalCapacity += banksCopy[bankID].capacity

    ## init the simulation class
    simulation = Simulation(id, banksCopy, networkCopy, shockSize, timestep, assortativity, totalCapacity, capacityMultipler, shockMultiplier, 0)
    ## append the simulation instance to the list of simulations
    simulations.append(simulation)
    ## shock banks by referencing the function housed inside the simulation (which is stored in the list of simulations)
    simulations[simID].shockBanks(shockSize)
    ## run timeteps by referencing the function housed inside the simulation (which is stored in the list of simulations)
    simulations[simID].runTimesteps(timestep)