import networkx as nx
from networkx.utils import powerlaw_sequence
import numpy as np
import copy as cp
from bank import Bank
from sim import Simulation

numberOfNodes = 250
powerLawAlpha = 2
targetAssort = -0.20
targetReplicates = 5
assortThresh = 0.01
banks = []
timestep = 1
simCount = 100
simulations = []
capacityMultipler = 0.5
shockMultiplier = 0.5
budgetRatio = 1

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
    for bankID in range(0, len(Graph.node)):
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
        Graph.node[bankID]['insolventTimestep'] = 50
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
        bank = Bank(bankID, capacity, cumulativeShock, solventNeighbors, status, insolventTimestep, shockToPropagate, "solvent")
        banks.append(bank)
    return banks
             
def calculateDegreeAssortativity(graph):
    return nx.degree_assortativity_coefficient(graph)

def generateMultipleNetworks():
    listsOfBanks = []
    ListsOfNetworks = []
    ListsOfAssortativities = []
    ## while we still need to find more networks...
    while len(listsOfBanks) < targetReplicates:
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
            ## add the list of banks to a master list of banks
            listsOfBanks.append(banks)
            ## and add the network to a master list of networks
            ListsOfNetworks.append(graph)
            ## and add the assortativity of the network to a master list
            ListsOfAssortativities.append(assortativity)

    return listsOfBanks, ListsOfNetworks, ListsOfAssortativities

banks_nets_lists = generateMultipleNetworks()

listsOfBanks = banks_nets_lists[0]
listsOfNetworks = banks_nets_lists[1]
listsOfAssorts = banks_nets_lists[2]

print 'timestep', 'regulate', 'budgetRatio', 'selfQuarantine', 'shockSize', 'shockCount', 'failedBanks', 'lostCapacity', 'assortativity'

for netID in range(0, targetReplicates):
    ## set assortativity for each network
    assortativity = listsOfAssorts[netID]

    ## below is (shockSizes * 2 * 2 * simCount) simulations (e.g., 15 x 2 x 2 x 100 = 6k)
    for regulate in range(0, 2):
        if regulate == 0: regulate = False
        else: regulate = True

        for quarantine in range(1, 2):
            if quarantine == 0: selfQuarantine = False
            else: selfQuarantine = True

            ## count from 10 to 75 in steps of 5
            for shockSize in range(50, 750, 50):
                budget = budgetRatio * shockSize
                ## wipe out the simulations list after each network
                simulations = []
                ## run sims!
                for simID in range(0, simCount):
                    timestep = 1
                    ## make copies of banks and nets so they don't change
                    banks = cp.deepcopy(listsOfBanks[netID])
                    network = cp.deepcopy(listsOfNetworks[netID])
                    ## count of the total capacity of the financial network
                    totalCapacity = 0
                    for bankID in range(0, len(banks)):
                        totalCapacity += banks[bankID].capacity

                    ## init the simulation class
                    simulation = Simulation(id, banks, network, shockSize, timestep, assortativity, totalCapacity, capacityMultipler, shockMultiplier, 0, 0, selfQuarantine, budget, regulate)
                    ## append the simulation instance to the list of simulations
                    simulations.append(simulation)
                    ## setupShocks by referencing the simulation in the list of simulations
                    simulations[simID].shockBanks()
                    ## run timeteps by referencing the simulation in the list of simulations
                    simulations[simID].runTimesteps(timestep)


