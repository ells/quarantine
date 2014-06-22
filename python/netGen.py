import networkx as nx
from networkx.utils import powerlaw_sequence
import scipy as sp
import numpy as np

numberOfNodes = 100
powerLawAlpha = 2
Graph = nx.Graph()
timestep = 0


def generateNetwork():
    global Graph
    ## use a networkx function to create a degree sequence that follows a power law
    degreeSequence=nx.utils.create_degree_sequence(numberOfNodes,powerlaw_sequence)

    ## use aforementioned degree sequence to configure a pseudograph that contains self-loops & hyper-edges
    pseudoGraph=nx.configuration_model(degreeSequence)
    ## remove hyper (parallel) edges
    Graph = nx.Graph(pseudoGraph)
    ## remove self edges
    Graph.remove_edges_from(Graph.selfloop_edges())

    ## loop through all nodes and set capacity equal to degree
    for i in range(0,len(Graph.node)-1):
        Graph.node[i]['capacity'] = Graph.degree(i)
        ## right now capacity = degree
        Graph.node[i]['cumulativeShock'] = 0
        ## if a bank is solvent, status = 1. When it crashes, status = 0.
        Graph.node[i]['status'] = 1
        ## here we set the timestep that the bank becomes insolvent to a big number
        Graph.node[i]['insolventTimestep'] = 100000000
   
    return Graph
  
def generateConnectedPowerLawNetwork():
    ## Use our generateNetwork function to create a sparse graph w/ power law capacities 
    global Graph
    Graph = generateNetwork()
    
    ## there is no guarantee that the network created above is completely connected
    ## therefore, we'll keep re-making the graph until we get a fully connected one
    while nx.is_connected(Graph) != True:
        Graph = generateNetwork()
        
    nx.write_gexf(Graph, 'connectedGraph.gexf')
    return Graph
    
def calculateDegreeAssortativity(Graph):
    return nx.degree_assortativity_coefficient(Graph)
    
def checkSolvency():
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
            print solventNeighbors
        ## perform solvency calculation    
        if capacity < (cumulativeShock / solventNeighbors): 
            ## if a bank is insolvent, change its status to 0
            Graph.node[nodeID]['status'] = 0
            ## and record the current timestep
            Graph.node[nodeID]['insolventTimestep'] = timestep
        
Graph = generateConnectedPowerLawNetwork()
degreeAssortativity = calculateDegreeAssortativity(Graph)
print degreeAssortativity
