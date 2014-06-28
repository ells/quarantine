from random import randint
import networkx as nx

class Simulation:
    def __init__(self, id, banks, graph, shockSize, timestep, assortativity, totalCapacity, capacityMultiplier, shockMultiplier, initialShockCount, lossFraction):
        self.id = id
        self.banks = banks
        self.graph = graph
        self.shockSize = shockSize
        self.timestep = timestep
        self.assortativity = assortativity
        self.totalCapacity = totalCapacity
        self.capacityMultiplier = capacityMultiplier
        self.shockMultiplier = shockMultiplier
        self.initialShockCount = initialShockCount
        self.lossFraction = (1.0 * self.shockSize) / self.totalCapacity

    def shockBanks(self):
        totalShockSize = self.shockSize
        currentShockSize = 0
        potentialShockList = []
        shockList = []

        ## first, we add all viable banks to a list (capacity < totalShock)
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.capacity <= totalShockSize: potentialShockList.append(bank)

        ## then we enter a while loop
        while currentShockSize < totalShockSize:
            ## keep picking banks randomly
            randomIndex = randint(0, len(potentialShockList) - 1)
            bankToTest = potentialShockList[randomIndex]

            ## test to make sure that bank wont put us over our target shockSize
            if currentShockSize + bankToTest.capacity <= totalShockSize:
                ## since we know the bank works, we change the name
                bankToShock = bankToTest
                ## shock the bank
                bankToShock.cumulativeShock = bankToShock.capacity
                ## add it to the shock list
                shockList.append(bankToShock)
                ## remove it from the potential shock list
                potentialShockList.remove(bankToShock)
                ## change the currentShockSize to reflect that we've shocked the bank
                currentShockSize += bankToShock.capacity
        ## set the initialShockCount (# of externally-shocked banks) so that it can be reported at the end of the simulation
        self.initialShockCount = len(shockList)

    def processInitialShocks(self, timestepStart):
        ## We were having issues with initially-shocked banks propagating to their neighboring (also initially-shocked) banks.
        ## Therefore, we elected to process the initial shocks in a separate loop that has now been pulled out into a fxn.
        ## The primary difference here is the ordering of when we kill the banks.
        ## If you'd like to see what each of these steps do, see their usage in sim.runTimesteps() below
        timestep = timestepStart
        for bankID in range(0,len(self.banks)):
            bank = self.banks[bankID]
            bank.updateStatus(timestep)
            bank.updateSolventNeighbors(self.graph, self.banks)
            bank.calculateShockToPropagate(self.capacityMultiplier, self.shockMultiplier)
            bank.propagateToNeighbors(self.graph, self.banks)
            bank.killBank()
        timestep += 1
        return timestep

    def calculateLossFraction(self):
        lostCapacity = 0
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.status == "dead": lostCapacity += self.graph.degree(bank.id)

        return (1.0 * lostCapacity) / self.totalCapacity

    def runTimesteps(self, timestepStart):
        shockSize = self.countGlobalCumulativeShock()

        ## here we process the initial perturbation to the financial network
        timestep = self.processInitialShocks(timestepStart)

        ## this effectively says : while(true) enter the timestep loop
        ## when the stop conditions are met (see sim.running() below) it reads: while(false) and exits the loop
        while self.running(timestep):
            ## first we loop through all the banks
            for bankID in range(0, len(self.banks)):
                ## set the bank in question based on the master banks list
                bank = self.banks[bankID]
                ## kill banks that failed at last timestep
                bank.killBank()
                ## update new statuses, again, based on the last timestep's propagations
                bank.updateStatus(timestep)
                ## after we've updated the statuses, we check the solvency of the neighboring banks
                bank.updateSolventNeighbors(self.graph, self.banks)
                ## now that we know how many neighbors the bank can spread to, we check calculate that banks shock size
                bank.calculateShockToPropagate(self.capacityMultiplier, self.shockMultiplier)
                ## now that we've calculated and set the bank's shock size, we propagate to its neighbors
                bank.propagateToNeighbors(self.graph, self.banks)
                self.lossFraction = self.calculateLossFraction()
            timestep += 1
            ## here we update the networkx graph object to reflect any changes to the banks in the banks list
            ## this is handy for outputting, head to sim.updateGraph() for more details
            self.updateGraph()

        ## at this stage, the simulation is over, so we print the files
        ## this will likely be changed to output to files rather than print
        ## this is because printing to console is actually relatively resource intensive and can slow down sims substantially
        print timestep, shockSize, self.initialShockCount, self.countDead(), '{0:.4g}'.format(self.lossFraction), '{0:.4g}'.format(self.assortativity)

        ## this is the output command to write the networkx graph to a gephi-specific readable format (super handy software for figures and data exploration)
        ## note that this will overwrite each time because the filename is not dynamically set
        nx.write_gexf(self.graph, "gephiOutput.gexf")


    def updateGraph(self):
        ## because all the variable changes are stored in the banks list, to output to gephi the graph needs updating
        ## the ordering/timing does not matter here, as we do not use the graph dictionaries for anything
        ## While this is possible, the code to do so DENSE...so for speed/readability/debugging I've gone this route.
        ## If you're interested in learning how to do it "the proper way" I have code examples for our specific situation
        ## provided by Andy.
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            bankInGraph = self.graph.node[bankID]
            bankInGraph['cumulativeShock'] = bank.cumulativeShock
            bankInGraph['status'] = bank.status
            bankInGraph['insolventTimestep'] = bank.insolventTimestep
            bankInGraph['shockToPropagate'] = bank.shockToPropagate
            bankInGraph['solventNeighbors'] = bank.solventNeighbors
            bankInGraph['statusID'] = bank.statusID

            if bank.status == "dead": bank.statusID = 4
            if bank.status == "fail": bank.statusID = 3
            if bank.status == "exposed": bank.statusID = 2
            if bank.status == "solvent": bank.statusID = 1



    def countGlobalCumulativeShock(self):
        ## pretty self explanatory, we loop through all the banks and sum up their cumulative shocks
        globalShock = 0
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            globalShock = globalShock + bank.cumulativeShock
        return globalShock

    def running(self, timestep):
        ## this runs the timesteps while loop
        ## when the count of failed banks reaches zero (and the simulation is running, aka timestep > 1)
        ## this function returns false and kills the while loops in the timesteps
        if self.countFailed() == 0 and timestep > 2: return False
        ## otherwise, returning true will keep it in an infinite loop
        else: return True

    def countSolvent(self):
        ## self explanatory, loop through all banks and add up the solvent ones
        solventBanks = 0
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.status == "solvent": solventBanks += 1
        return solventBanks

    def countFailed(self):
        ## self explanatory, loop through all banks and add up the failed ones
        ## note that failed banks stay in this state for only the timestep that they propagate
        failedBanks = 0
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.status == "fail": failedBanks += 1
        return failedBanks

    def countDead(self):
        ## self explanatory, loop through all banks and add up the dead ones
        ## banks that have failed will enter (and remain) in this state for the rest of the simulation
        deadBanks = 0
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.status == "dead": deadBanks += 1
        return deadBanks

    def countExposed(self):
        ## self explanatory, loop through all banks and add up the dead ones
        ## banks that have been shocked but have not yet failed because the cumulativeShock < capacity
        exposedBanks = 0
        for bankID in range(0, len(self.banks)):
            bank = self.anks[bankID]
            if bank.status == "exposed": exposedBanks += 1
        return exposedBanks