import networkx as nx
from networkx.utils import powerlaw_sequence
import scipy as sp
import numpy as np

def generateNetwork(numberOfNodes, powerLawAlpha):
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
  
def generateConnectedPowerLawNetwork(numberOfNodes, powerLawAlpha):
    ## Use our generateNetwork function to create a sparse graph w/ power law capacities 
    Graph = generateNetwork(numberOfNodes, powerLawAlpha)
    
    ## there is no guarantee that the network created above is completely connected
    ## therefore, we'll keep re-making the graph until we get a fully connected one
    while nx.is_connected(Graph) != True:
        Graph = generateNetwork(numberOfNodes, powerLawAlpha)
        
    nx.write_gexf(Graph, 'connectedGraph.gexf')
    return Graph
    
def calculateDegreeAssortativity(Graph):
    return nx.degree_assortativity_coefficient(Graph)
    
def checkSolvency(Graph, timestep):
    for nodeID in range(0, numberOfNodes-1):
        capacity = Graph.node[nodeID]['capacity']
        cumulativeShock = Graph.node[nodeID]['cumulativeShock']
        solventNeighbors = 0;
        neighbors = Graph.neighbors(nodeID)
        for neighborID in range(0, len(neighbors)):
            neighbor = Graph.node[neighborID]
            if neighbor['status'] == 1: solventNeighbors = solventNeighbors + 1
            
        if capacity < (cumulativeShock / solventNeighbors): 
            Graph.node[nodeID]['status'] = 0
            Graph.node[nodeID]['insolventTimestep'] = timestep
        

        
        
        
     
            
        
        
    
numberOfNodes = 250
powerLawAlpha = 2
Graph = generateConnectedPowerLawNetwork(numberOfNodes, powerLawAlpha)
degreeAssortativity = calculateDegreeAssortativity(Graph)
print degreeAssortativity
