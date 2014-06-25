from random import randint
class Simulation:
    def __init__(self, id, banks, graph, shockSize, banksToShock, timestep, assortativity):
        self.id = id
        self.banks = banks
        self.graph = graph
        self.shockSize = shockSize
        self.banksToShock = banksToShock
        self.timestep = timestep
        self.assortativity = assortativity

    def setupShocks(self, shock, bankList, Graph):
        ## this function is called from netGen
        ## we set globals first, as any instantiation of sim.py is going to be a single outbreak
        global totalShockSize
        global banks
        global bankGraph
        bankGraph = Graph
        totalShockSize = shock
        banks = bankList
        ## Then we select the banks to shock based on the shock size
        self.selectBanksToShock()
        ## Finally, we actually shock the banks
        self.shockBanks()

    def selectBanksToShock(self):
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
                    self.banksToShock.append(bankToShock)
                    currentShockSize += bankToShock.capacity

        ## this just prints the shock size and number of banks being shocked
        #print 'total shock size is', currentShockSize, 'distributed between', len(self.banksToShock), 'banks'

    def shockBanks(self):
        for bankID in range(0, len(self.banksToShock)):
            bank = banks[bankID]
            bank.cumulativeShock = bank.capacity

    def countBankruptcies(self):
        global bankruptBanks
        bankruptBanks = 0
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            bank.checkSelfSolvency(self.timestep)
            if bank.cumulativeShock >= bank.capacity: bankruptBanks = bankruptBanks + 1
        return bankruptBanks

    def countShocks(self):
        shockedBanks = 0
        for bankID in range(0,len(banks)):
            bank = banks[bankID]
            if bank.cumulativeShock > 0: shockedBanks = shockedBanks + 1
        return shockedBanks

    def countCrippledBanks(self):
        crippledBanks = 0
        for bankID in range(0,len(banks)):
            bank = banks[bankID]
            if bank.cumulativeShock < bank.capacity and bank.cumulativeShock > 0:
                crippledBanks = crippledBanks + 1
        return crippledBanks

    def runTimesteps(self, timestep):
        print "yay for timesteps"

    # def runTimesteps(self, timestep):
    #     while self.running(timestep):
    #         for bankID in range(0, len(banks)):
    #             bank = banks[bankID]
    #             bank.checkNeighborSolvency(self.graph, self.banks)
    #             bank.checkSelfSolvency(timestep)
    #             bank = banks[bankID]
    #             bank.calculateShockToPropagate()
    #             bank.propagateToNeighbors(self.graph, self.banks)
    #         timestep = timestep + 1
    #         self.updateGraph()
    #     print timestep, self.countBankruptcies(), self.shockSize, len(self.banksToShock), self.countGlobalCumulativeShock(), self.assortativity

    def updateGraph(self):
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            bankInGraph = bankGraph.node[bankID]
            bankInGraph['cumulativeShock'] = bank.cumulativeShock
            bankInGraph['status'] = bank.status
            bankInGraph['insolventTimestep'] = bank.insolventTimestep
            bankInGraph['solventNeighbors'] = bank.solventNeighbors

    def countGlobalCumulativeShock(self):
        globalShock = 0
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            globalShock = globalShock + bank.cumulativeShock
        return globalShock


