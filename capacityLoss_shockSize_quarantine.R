require(ggplot2)
require(grid)

## note that this requires the python console outputs, exactly as they are printed while simulation is running
## import this file as a dataframe and name it "data"
## If you're using pyCharm, you'll need to remove the very first and last lines of the output after cut & paste

## shockSize vs lostCapacity
base = ggplot(imperfect, aes(x=shockSize, y=lostCapacity))
points = base + geom_point(aes(size=shockCount,color=knowledgeState, alpha=1))
labeled = points + labs(title="Self Quarantine", x="Shock Size", y="Capacity Loss")
themed = labeled + theme_bw() + theme(legend.position="bottom")
faceted = themed + facet_grid(selfQuarantine~regulate)
faceted

## timestep vs shockCount
base = ggplot(exploreMultiplier, aes(x=timestep, y=lostCapacity))
points = base + geom_point(aes(size=shockCount, color=interaction(selfQuarantine, regulate)))
smooth = points + geom_smooth(aes(color=interaction(selfQuarantine, regulate)))
labeled = smooth + labs(title="Self Quarantine", x="Duration", y="Lost Capacity")
themed = labeled + theme_bw() + theme(legend.position="bottom")
themed

## shockSize vs shockCount
base = ggplot(budgetRatio, aes(x=shockCount, y=shockSize))
points = base + geom_point(aes(size=lostCapacity, color=interaction(selfQuarantine, regulate)), alpha=0.25)
smooth = points + geom_smooth(aes(color=interaction(selfQuarantine, regulate)))
labeled = smooth + labs(title="Self Quarantine", x="Shock Count", y="Shock Size")
facets = labeled + facet_grid(.~budgetRatio)
themed = facets + theme_bw() + theme(legend.position="bottom")
themed

## shockSize vs shockCount
base = ggplot(budgetRatio, aes(x=shockCount, y=lostCapacity))
points = base + geom_point(aes(size=shockSize, color=interaction(selfQuarantine, regulate)), alpha=0.0)
smooth = points + geom_smooth(aes(color=interaction(selfQuarantine, regulate)))
labeled = smooth + labs(title="Budget Ratios", x="Shock Count", y="Lost Capacity")
facets = labeled + facet_grid(.~budgetRatio)
themed = facets + theme_bw() + theme(legend.position="bottom")
themed





## shockCount vs lostCapacity
base = ggplot(budgetRatio, aes(x=shockCount,y=lostCapacity))
points = base + geom_point(aes(size=shockSize, color=interaction(selfQuarantine, regulate)), alpha=0.5)
smooth = points + geom_smooth(aes(group=interaction(selfQuarantine, regulate)))
labeled = smooth + labs(title="Self Quarantine", x="Shock Count", y="Capacity Loss")
facets = labeled + facet_grid(.~budgetRatio)
themed = facets + theme_bw() + theme(legend.position="bottom")
themed
