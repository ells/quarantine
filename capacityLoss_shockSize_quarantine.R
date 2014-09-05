require(ggplot2)
require(grid)

## note that this requires the python console outputs, exactly as they are printed while simulation is running
## import this file as a dataframe and name it "data"
## If you're using pyCharm, you'll need to remove the very first and last lines of the output after cut & paste

## shockSize vs lostCapacity
base = ggplot(imperfect, aes(x=shockSize, y=lostCapacity))
points = base + geom_point(aes(size=shockCount,color=regulate, alpha=0.25))
smooth = points + geom_smooth(aes(color=regulate))
labeled = smooth + labs(title="Imperfect Knowledge x Self Quarantine", x="Shock Size", y="Capacity Loss")
themed = labeled + theme_bw() + theme(legend.position="bottom")
faceted = themed + facet_grid(selfQuarantine~knowledgeState)
faceted

## duration
base = ggplot(imperfect, aes(x=shockCount, y=lostCapacity))
points = base + geom_point(aes(size=shockSize,color=regulate, alpha=0.05))
smooth = points + geom_smooth(aes(color=regulate))
labeled = smooth + labs(title="Imperfect Knowledge x Self Quarantine", x="Shock Count", y="Capacity Loss")
themed = labeled + theme_bw() + theme(legend.position="bottom")
faceted = themed + facet_grid(selfQuarantine~knowledgeState) + scale_x_continuous(limits = c(0,20))
faceted


## shockCount vs lostCapacity
base = ggplot(imperfect, aes(x=shockCount,y=lostCapacity))
points = base + geom_point(aes(size=shockSize, color=regulate), alpha=0.25)
smooth = points + geom_smooth(aes(group=regulate))
labeled = smooth + labs(title="Self Quarantine", x="Shock Count", y="Capacity Loss")
faceted = themed + facet_grid(selfQuarantine~knowledgeState)
faceted
themed = faceted + theme_bw() + theme(legend.position="bottom")
themed
