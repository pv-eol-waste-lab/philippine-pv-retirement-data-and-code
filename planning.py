from math import ceil
from model import *

def run():
    national=Params()
    exchanges=[]
    for early,late in [(2027,2028),(2028,2029),(2026,2030),(2027,2029)]:
        for horizon in [2050,2053,2054,2060]:
            def island_difference(year):
                at_age=horizon-year
                return mass(year)*(cdf(at_age,.90,national)-cdf(at_age,.95,national))
            shift=100*(island_difference(early)-island_difference(late))
            exchanges.append([early,late,horizon,shift])
    pd.DataFrame(exchanges,columns=['earlyYear','lateYear','horizon','swapTonnes']).to_csv(OUT/'year-exchanges.csv',index=False)
    allocation=pd.read_csv(OUT/'province2035.csv').set_index('province').loc['Negros Occidental']
    rows=[]
    for fraction in [.8,1.]:
        for rule,tonnes in allocation.items():
            trips=ceil(fraction*tonnes/20)
            rows.append([fraction,rule,tonnes,20,trips,max(0,trips-40)])
    pd.DataFrame(rows,columns=['collectedFraction','allocation','retiredTonnes','payload','minimumTrips','excessOver40']).to_csv(OUT/'collection-trips.csv',index=False)
    assert np.ptp(envelope(2050,.5,order=np.ones(3)))<1e-6
if __name__=='__main__':run()
