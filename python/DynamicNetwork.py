# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 18:31:16 2014

@author: linnlii
"""
import sys
sys.path.append('pygexf/gexf')
from _gexf import Gexf, GexfImport
import networkx as nx
import cPickle as pickle

def diff(a, b):
        b = set(b)
        return [aa for aa in a if aa not in b]

def convertGraphs(G,EdgeList):
    graph=gexf.addGraph("undirected","dynamic","Dynamic Networks")
    for node in G.nodes():
        if not graph.nodeExists(node):
            graph.addNode(node,'',start="0",end="",startopen=False,endopen=False,pid="",r="84",g="84",b="84",spells=[]) 
            graph.addNodeAttribute(title='',defaultValue=None, type="integer",mode="static", force_id="capacity")             
            graph.nodes[node].addAttribute('capacity',value = G0.node[node]['capacity'])            
            graph.addNodeAttribute(title='',defaultValue=None, type="integer",mode="dynamic", force_id="state")      
    E = G.edges()
    for e in E:
        [n1,n2] = [e[0],e[1]]
        if e in EdgeList:
            graph.addEdge(e,n1,n2,weight = 1,start="0",end=str(EdgeList[e]))
            #graph.addEdgeAttribute(title='',defaultValue=None,type="integer",mode="dynamic", force_id="time interval")
        else:
            graph.addEdge(e,n1,n2,weight = 1,start="0",end="")
        graph.addDefaultAttributesToEdge(e)
    return graph
    
# Change the state value
def addAttributes(graph,List):
    Loc_time = 0
    Loc_bank = 1
    Loc_state = 2
    i = 0
    bankList = dict()
    while i < len(List):
        #start = List[i][Loc_time] # time that state transition occured
        bankID = List[i][Loc_bank]
        if bankID in bankList:
            graph.nodes[bankID].addAttribute('state',value = bankList[bankID][1], start =str(bankList[bankID][0]), end=str(List[i][Loc_time]))
            bankList[bankID] = (List[i][Loc_time], List[i][Loc_state])
        else:
            graph.nodes[bankID].addAttribute('state',value = 1, start ='0', end=str(List[i][Loc_time]))
            bankList[bankID] = (List[i][Loc_time], List[i][Loc_state])
        #graph.nodes[bankID].addAttribute('state',value = List[i][Loc_state], start =str(List[i][Loc_time]), end='')
        #graph.nodes[bankID].addAttribute('state',value = List[i][Loc_state], start ='', end='6')   
        i+=1
    EndTime = i
    if len(bankList.keys())!=0:
        for bankID in bankList:
            graph.nodes[bankID].addAttribute('state',value = bankList[bankID][1], start =str(bankList[bankID][0]), end=str(EndTime))
    for bankID in diff(range(len(graph.nodes.keys())),bankList.keys()):
        graph.nodes[bankID].addAttribute('state',value = 1, start ='0', end=str(EndTime))
    return graph

# Creating toy example 
# state = 1 => solvant
# state = 2 => exposed
# state = 3 => feail
# state = 4 => dead
List = [] # It is important that the list is ordered by time
List.append((1,0,1)) #(time, bankID, state)
List.append((1,1,4))
List.append((2,0,4))
List.append((3,2,2))
List.append((4,2,3))
List.append((5,2,4))
# Creating list of edges to be cut at a specific time
EdgeList = {}
EdgeList[(2,20)]=3
EdgeList[(2,21)]=4
EdgeList[(2,6)]=5

gexf = Gexf("Financial Contagion","A dynamic network model")
G0 = pickle.load(open('/Users/linnlii/Documents/GitHub/pygexf/test/ToyGraph.p', 'rb')) 
graph = convertGraphs(G0,EdgeList)
graph = addAttributes(graph,List)
output_file=open("DynamicNetworks.gexf","w")
gexf.write(output_file)