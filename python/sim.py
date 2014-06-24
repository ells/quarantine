from random import randint
import networkx as nx

totalShockSize = 0
banks = []
banksToShock = []
bankGraph = nx.Graph()
timestep = 0

def setupShocks(shock, bankList, Graph):
    ## this function is called from netGen
    ## we set globals first, as any instantiation of sim.py is going to be a single outbreak
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
    while currentShockSize < totalShockSize:
        ## first we pick a random bank
        randomBankID = randint(0, len(banks)-1)
        ## save that bank as an object
        bankToShock = banks[randomBankID]

        ## if the current bank's capacity is less than the total shock size...
        if (bankToShock.capacity <= totalShockSize):
            currentBankCapacity = bankToShock.capacity
            ## record the total shock size, assuming we had added that bank to the shock list
            potentialCurrentShockSize = currentShockSize + currentBankCapacity
            ## if the current bank puts us over the shock limit, then forget about it and continue the while loop
            if potentialCurrentShockSize > totalShockSize: continue
            else:
                banksToShock.append(bankToShock)
                currentShockSize += bankToShock.capacity

    ## this just prints the shock size and number of banks being shocked
    print 'total shock size is', currentShockSize, 'distributed between', len(banksToShock), 'banks'

def shockBanks():
    for bankID in range(0, len(banksToShock)):
        banks[bankID].cumulativeShock = banks[bankID].capacity

def countBankruptcies():
    bankruptBanks = 0
    for bankID in range(0, len(banks)):
        banks[bankID].checkSelfSolvency(timestep)
        if banks[bankID].cumulativeShock >= banks[bankID].capacity: bankruptBanks = bankruptBanks + 1
    return bankruptBanks

def countStatusZero():
    statusZero = 0;
    for bankID in range(0, len(banks)):
        banks[bankID].checkSelfSolvency(timestep)
        if banks[bankID].status == 0: statusZero = statusZero + 1
    return statusZero


def countShocks():
    shockedBanks = 0
    for bankID in range(0,len(banks)):
        if banks[bankID].cumulativeShock > 0: shockedBanks = shockedBanks + 1
    return shockedBanks

def countCrippledBanks():
    crippledBanks = 0
    for bankID in range(0,len(banks)):
        if banks[bankID].cumulativeShock < banks[bankID].capacity and banks[bankID].cumulativeShock > 0:
            crippledBanks = crippledBanks + 1
    return crippledBanks

def runTimesteps():
    global timestep
    while running():
        for bankID in range(0, len(banks)):
            banks[bankID].checkSelfSolvency(timestep)
            banks[bankID].checkNeighborSolvency()

        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            bank.calculateShockToPropagate()
            bank.propagateToNeighbors()
        timestep = timestep + 1


def running():
    print 't=', timestep, 'status0=', countStatusZero(), 'bankrupt=', countBankruptcies(), 'crippled=', countCrippledBanks(), 'shocked=', countShocks()

    if countCrippledBanks() == 0 and timestep > 0: return False
    else: return True









