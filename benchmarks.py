from model import *
from math import ceil

def run():
    rows=[]
    for vintage in [False,True]:
        for split in [False,True]:
            r,_=trajectories(Params(meanlead=3 if split else 2,spread=2/3 if split else 0),detail=True)
            y=np.r_[plants.year,np.tile(2025+np.arange(1,6),3)]
            c=r*(mass(y[:,None]) if vintage else 76)
            rows.append(['Installation-year' if vintage else 'Fixed 76',
                         '2027--2029' if split else '2027',c[:,:26].sum(),r[:,:26].sum()])
    df=pd.DataFrame(rows,columns=['massModel','installation','waste','retiredMW'])
    df.to_csv(OUT/'mass-timing.csv',index=False)
    refrows=[]
    for beta in [5.3759,2.4928]:
        y=np.r_[plants.year,np.tile(np.arange(2027,2030),3)]
        sizes=np.r_[plants.mw,np.repeat(capacity/3,3)]
        age=np.maximum(np.arange(2024,2076)[None,:]-y[:,None],0)
        f=-np.expm1(-(age/30)**beta)
        tonnes=(np.diff(f)*sizes[:,None]*mass(y[:,None])).sum(0)
        refrows.append([beta,tonnes[:26].sum(),tonnes.max(),years[tonnes.argmax()]])
    pd.DataFrame(refrows,columns=['shape','cum2050','peak','peakyear']).to_csv(OUT/'reference-fleet.csv',index=False)
if __name__=='__main__':run()
