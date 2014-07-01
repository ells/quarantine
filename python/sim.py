import random
from random import randint
import networkx as nx

class Simulation:
    def __init__(self, id, banks, graph, shockSize, timestep, assortativity, totalCapacity, capacityMultiplier, shockMultiplier, initialShockCount, lossFraction, selfQuarantine, budget):
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
        self.selfQuarantine = selfQuarantine
        self.budget = budget

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
                ## run global regulator function prior to status updates from propagations at last timestep
                self.globalRegulator()
                ## update new statuses, again, based on the last timestep's propagations
                bank.updateStatus(timestep)
                ## after we've updated the statuses, we check the solvency of the neighboring banks
                bank.updateSolventNeighbors(self.graph, self.banks)
                ## now that we know how many neighbors the bank can spread to, we check calculate that banks shock size
                bank.calculateShockToPropagate(self.capacityMultiplier, self.shockMultiplier)
                ## now that we've calculated and set the bank's shock size, we propagate to its neighbors
                bank.propagateToNeighbors(self.graph, self.banks)
                self.lossFraction = self.calculateLossFraction()
                ## if self.selfQuarantine is on, execute, otherwise continue as normal
                if self.selfQuarantine == True: self.selfQuarantineIntervention()
            timestep += 1
            ## here we update the networkx graph object to reflect any changes to the banks in the banks list
            ## this is handy for outputting, head to sim.updateGraph() for more details
            self.updateGraph()

        ## at this stage, the simulation is over, so we print the files
        ## this will likely be changed to output to files rather than print
        ## this is because printing to console is actually relatively resource intensive and can slow down sims substantially
        quarantineState = 0
        if self.selfQuarantine == True: quarantineState = "quarantine"
        else: quarantineState = "noQuarantine"

        print timestep, quarantineState, shockSize, self.initialShockCount, self.countDead(), '{0:.4g}'.format(self.lossFraction), '{0:.4g}'.format(self.assortativity)

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
            bank = self.banks[bankID]
            if bank.status == "exposed": exposedBanks += 1
        return exposedBanks

    def selfQuarantineIntervention(self):
        selfQuarantineList = self.populateQuarantineList()
        random.shuffle(selfQuarantineList)
        self.selfQuarantineRecursion(selfQuarantineList)
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            bank.updateStatus(self.timestep)

    def populateQuarantineList(self):
        selfQuarantineList = []
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            ## if bank has not failed and has degree >= 2
            if (bank.status == "solvent" or bank.status == "exposed") and (bank.solventNeighbors >= 2):
                ## and the remaining capacity > 1
                if bank.capacity - bank.cumulativeShock > 1:
                    ## and if the inverse connectedness is less than the loss fraction
                    if (1.0 / bank.solventNeighbors) < self.lossFraction:
                        selfQuarantineList.append(bank)
        return selfQuarantineList

    def selfQuarantineRecursion(self, selfQuarantineList):
        ## grab the first bank in the shuffled list
        if len(selfQuarantineList) == 0: return
        bankToCheckID = selfQuarantineList[0].id
        bankToCheck = self.banks[bankToCheckID]
        ## confirm its self-quarantine criteria
        if (bankToCheck.status == "solvent" or bankToCheck.status == "exposed") and (bankToCheck.solventNeighbors >= 2):
                ## and the remaining capacity > 1
                if bankToCheck.capacity - bankToCheck.cumulativeShock > 1:
                    ## and if the inverse connectedness is less than the loss fraction
                    if (1.0 / bankToCheck.solventNeighbors) < self.lossFraction:
                        ## find all edges of the self quarantining node
                        listOfEdges = self.graph.edges(bankToCheckID)
                        ## of those edges, compile a list of edges that can be removed
                        validEdges = []
                        for listIndex in range(0,len(listOfEdges)):
                            ## annoying indexing stuff...first we pick the edge in the listOfEdges
                            edge = listOfEdges[listIndex]
                            ## then we pull out the ID of the target of the edge (to find the source, edge[0])
                            randomNeighborID = edge[1]
                            ## we then use that ID to find the bank in the master banks list
                            randomNeighborBank = self.banks[randomNeighborID]
                            ## then we determine if that edge should be cut (not leading to an already failed node)
                            if randomNeighborBank.status == "solvent" or randomNeighborBank.status == "exposed": validEdges.append(edge)
                        ## if there are edges added to the validEdges list
                        if len(validEdges) > 0:
                            ## then randomly select the edge to be removed
                            edgeToRemove = random.choice(validEdges)
                            ## and remove that edge from the graph
                            ## note that here is some weird notation, an edge is a "tuple" that combines:
                            ## ## (source node, target node, edge weight)
                            ## Therefore, we need to "unpack" that tuple for networkX to recognize it
                            ## Which is done with this wonky and cryptic asterisks prior to the relevant tuple
                            self.graph.remove_edge(*edgeToRemove)
                            ## increment cumulative shock for both banks by 1
                            bankToCheck.cumulativeShock += 1
                            randomNeighborBank.cumulativeShock += 1
                            ## recurse, but do NOT shuffle the list so that we can reconsider it until its ineligible for self-quarantine
                            self.selfQuarantineRecursion(selfQuarantineList)
        ## if we've made it this far, the bank can no longer self quarantine, so it is removed
        if bankToCheck in selfQuarantineList: selfQuarantineList.remove(bankToCheck)
        ## we then reshuffle the list so that the 0th index is a new bank [super important, on the 2nd line of actual code of this fxn]
        random.shuffle(selfQuarantineList)
        ## recurse the shuffled list with the ineligible node removed
        self.selfQuarantineRecursion(selfQuarantineList)

    def globalRegulator(self):
        atRiskBanks = []
        for bankID in range(0, len(self.banks)):
            bank = self.banks[bankID]
            if bank.status == "solvent" or bank.status == "exposed":
                if bank.cumulativeShock > bank.capacity:
                    atRiskBanks.append(bank)

        impendingShock = 0
        if len(atRiskBanks) == 0: return
        else:
            for atRiskBankID in range(0, len(atRiskBanks)):
                atRiskBank = atRiskBanks[atRiskBankID]
                liability = atRiskBank.cumulativeShock - atRiskBank.capacity
                impendingShock += liability

        if impendingShock >= self.budget: self.insufficientBudgetRegulation(atRiskBanks, impendingShock)
        else: self.sufficientBudgetRegulation(atRiskBanks, impendingShock)


    def sufficientBudgetRegulation(self, atRiskBanks, impendingShock):
        for bankID in range(0, len(atRiskBanks)):
            bankToSave = atRiskBanks[bankID]
            budgetProvided = self.budget * ((1.0 * (bankToSave.cumulativeShock - bankToSave.capacity)) / impendingShock)
            bankToSave.cumulativeShock -= budgetProvided

    def insufficientBudgetRegulation(self, atRiskBanks, impendingShock):
        overage = 0.10
        atRiskBanks.sort(key=lambda x: x.capacity, reverse=True)
        allocationK = self.budget

        bailoutCandidates = []
        for bankID in range(0, len(atRiskBanks)):
            if allocationK == 0: break
            bank = atRiskBanks[bankID]
            if bank.cumulativeShock - bank.capacity < self.budget:
                bailoutCandidates.append(bank)
                atRiskBanks.remove(bank)
                allocationK -= (bank.cumulativeShock - bank.capacity + (overage * bank.capacity))

        for bailoutCandidateID in range(0, len(bailoutCandidates)):
            bailedOutBank = bailoutCandidates[bailoutCandidateID]
            recapitalization = bailedOutBank.cumulativeShock - bailedOutBank.capacity + (overage * bailedOutBank.capacity)
            bailedOutBank.cumulativeShock -= recapitalization

        self.budget -= allocationK

        if self.budget > 0: atRiskBanks[0].cumulativeShock -= self.budget

