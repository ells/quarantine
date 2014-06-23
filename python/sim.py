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

        if (bankToShock.capacity <= totalShockSize):
            currentBankCapacity = bankToShock.capacity
            nextCurrentShockSize = currentShockSize + currentBankCapacity

            if nextCurrentShockSize > totalShockSize: continue
            else:
                banksToShock.append(bankToShock)
                currentShockSize += bankToShock.capacity

    print currentShockSize, len(banksToShock)

def shockBanks():
    for bankID in range(0, len(banksToShock)):
        bank = banksToShock[bankID]
        bankNode = bankGraph.node[bankID]

        ## for now, we've got to make the change to cumulative shock in two places
        ## this will be refactored once I have a sit-down with either Andy or Anna.
        ## As I'm sure that we should be able to set both simultaneously.
        ## To be clear, this is both messy AND dangerous so it's gotta be fixed ASAP.
        bank.cumulativeShock = bank.capacity
        bankNode['cumulativeShock'] = bank.capacity






















