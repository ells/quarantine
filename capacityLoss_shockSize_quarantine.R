require(ggplot2)
require(grid)

## note that this requires the python console outputs, exactly as they are printed while simulation is running
## import this file as a dataframe and name it "data"
## If you're using pyCharm, you'll need to remove the very first and last lines of the output after cut & paste
base = ggplot(data, aes(x=shockSize,y=lostCapacity))
points = base + geom_jitter(aes(size=shockCount, color=selfQuarantine), alpha=0.50)
smooth = points + geom_smooth(aes(group=selfQuarantine))
labeled = smooth + labs(title="Self Quarantine", x="Shock Size", y="Capacity Loss")
facets = labeled + facet_grid(.~assortativity)
themed = facets + theme_bw() + theme(legend.position="bottom")
themed