from random import randint
import networkx as nx
totalShockSize = 0
banks = []
banksToShock = []
bankGraph = nx.Graph()

def run(shock, bankList, Graph):
    ## this function is called from netGen
    ## we set globals first, as any instantiation of simulation is going to be a SINGLE RUN
    global totalShockSize
    global banks
    global bankGraph
    bankGraph = Graph
    totalShockSize = shock
    banks = bankList
    ## Then we select the banks to shock based on the shock size
    selectBanksToShock()
    ## Finally, we actually shock the banks
    shockBanks()

def selectBanksToShock():
    currentShockSize = 0
    ## this isn't robust yet, as its possible to infinite loop
    ## That being said, I've run it 1000x without a single hang-up
    while currentShockSize < totalShockSize:
        ## first we pick a random bank
        randomBankID = randint(0, len(banks)-1)
        ## save that bank as an object
        bankToShock = banks[randomBankID]

        ## if the current bank's capacity is less than the total shock size...
        if (bankToShock.capacity <= totalShockSize):
            currentBankCapacity = bankToShock.capacity
            ## record the total shock size, assuming we had added that bank to the shock list
            nextCurrentShockSize = currentShockSize + currentBankCapacity
            ## if the current bank puts us over the shock limit, then forget about it and continue the while loop
            if nextCurrentShockSize > totalShockSize: continue
            ## otherwise, add that bank to the list of banks to shock
            ## and adjust the currentShockSize to account for the newly added bank
            else:
                banksToShock.append(bankToShock)
                currentShockSize += bankToShock.capacity
    ## this just prints the shock size and number of banks being shocked
    print currentShockSize, len(banksToShock)

def shockBanks():
    ## loop over all banks in the list of banks to be shocked
    for bankID in range(0, len(banksToShock)):
        ## store each bank in the list as an object
        bank = banksToShock[bankID]
        ## store each bank in the graph as another object
        bankNode = bankGraph.node[bankID]

        ## for now, we've got to make the change to cumulative shock in two places
        ## this will be refactored once I have a sit-down with either Andy or Anna.
        ## As I'm sure that we should be able to set both simultaneously.
        ## To be clear, this is both messy AND dangerous so it's gotta be fixed ASAP.

        ## update BOTH the bank list and the graph
        banks[bankID].cumulativeShock = bank.capacity
        bankNode['cumulativeShock'] = bank.capacity

        print banks[bankID].cumulativeShock, bankNode['cumulativeShock']