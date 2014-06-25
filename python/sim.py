from random import randint
import networkx as nx

class Simulation:
    def __init__(self, id, banks, graph, shockSize, banksToShock, timestep, assortativity, totalCapacity):
        self.id = id
        self.banks = banks
        self.graph = graph
        self.shockSize = shockSize
        self.banksToShock = banksToShock
        self.timestep = timestep
        self.assortativity = assortativity
        self.totalCapacity = totalCapacity

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

    def countSolvent(self):
        solventBanks = 0;
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            if bank.status == "solvent": solventBanks += 1
        return solventBanks

    def countFailed(self):
        failedBanks = 0
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            if bank.status == "fail": failedBanks += 1
        return failedBanks

    def countDead(self):
        deadBanks = 0
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            if bank.status == "dead": deadBanks += 1
        return deadBanks

    def countExposed(self):
        exposedBanks = 0
        for bankID in range(0,len(banks)):
            bank = banks[bankID]
            if bank.status == "exposed": exposedBanks += 1
        return exposedBanks

    def runTimesteps(self, timestepStart):
        global timestep
        timestep = timestepStart
        while self.running(timestep):
            for bankID in range(0, len(banks)):
                bank = banks[bankID]
                ## kill banks that failed at last timestep
                bank.killBank()
                ## update new statuses
                bank.updateStatus(timestep)
                bank.updateSolventNeighbors(self.graph, self.banks)
                bank.calculateShockToPropagate()
                bank.propagateToNeighbors(self.graph, self.banks)
            timestep += 1
            #print timestep, self.countSolvent(), self.countExposed(), self.countFailed(), self.countDead()
            self.updateGraph()

        # shockProp = self.countGlobalCumulativeShock()/self.totalCapacity
        # if shockProp > 1:
        #     nx.write_gexf(self.graph, "shockProp_greaterThan1.gexf")
        #     return

        print timestep, self.shockSize, len(self.banksToShock), self.countDead(), '{0:.4g}'.format(self.countGlobalCumulativeShock()/self.totalCapacity), '{0:.4g}'.format(self.assortativity)
        nx.write_gexf(self.graph, "shockProp_greaterThan1.gexf")


    def updateGraph(self):
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            bankInGraph = bankGraph.node[bankID]
            bankInGraph['cumulativeShock'] = bank.cumulativeShock
            bankInGraph['status'] = bank.status
            bankInGraph['insolventTimestep'] = bank.insolventTimestep
            bankInGraph['shockToPropagate'] = bank.shockToPropagate
            bankInGraph['solventNeighbors'] = bank.solventNeighbors

    def countGlobalCumulativeShock(self):
        globalShock = 0
        for bankID in range(0, len(banks)):
            bank = banks[bankID]
            globalShock = globalShock + bank.cumulativeShock
        return globalShock

    def running(self, timestep):
        if self.countFailed() == 0 and timestep > 0: return False
        else: return True
