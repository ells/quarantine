import networkx as nx
from networkx.utils import powerlaw_sequence
import scipy as sp
import numpy as np
import matplotlib.pyplot as plt

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
        Graph.node[i]['cumulativeShock'] = 0
        Graph.node[i]['status'] = 1
   
    return Graph
  
def generateConnectedPowerLawNetwork(numberOfNodes, powerLawAlpha):
    ## Use our generateNetwork function to create a sparse graph w/ power law capacities 
    Graph = generateNetwork(numberOfNodes, powerLawAlpha)
    
    ## there is no guarantee that the network created above is completely connected
    ## therefore, we'll keep re-making the graph until we get a fully connected one
    while nx.is_connected(Graph) != True:
        Graph = generateNetwork(numberOfNodes, powerLawAlpha)
        
    nx.write_gexf(Graph, 'connectedGraph.gexf')
    
numberOfNodes = 500
powerLawAlpha = 2
generateConnectedPowerLawNetwork(numberOfNodes, powerLawAlpha)
    





