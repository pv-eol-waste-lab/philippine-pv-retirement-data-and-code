from model import *
from itertools import permutations
from scipy.stats import rankdata
import matplotlib.pyplot as plt
from dataclasses import replace
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
def savefig(fig,name):
    fig.savefig(OUT/(name+'.pdf'),metadata={'Author':None,'CreationDate':None,'ModDate':None},bbox_inches='tight')
    plt.close(fig)
def cross(h,s,p):
    c=costs(h,s,p)
    return 100*(c[2,0]+c[0,2]-c[2,2]-c[0,0])
def run():
    base=Params()
    ret,w=trajectories(base,detail=True)
    n=len(plants)
    central=pd.DataFrame({'year':years,'existing':w[:n].sum(0),'pipeline':w[n:].sum(0),'retiredMW':ret.sum(0)})
    central.to_csv(OUT/'annual.csv',index=False)
    prov=plants.groupby('province').mw.sum()/plants.mw.sum()
    pw=pd.DataFrame(w[:n],index=plants.province,columns=years).groupby(level=0).sum()
    pw.to_csv(OUT/'province.csv')
    q=pw[2035];d=pd.DataFrame({'cohort':q,'capacityShare':prov*q.sum()})
    d.to_csv(OUT/'province2035.csv')
    cum=pw.loc[:,2025:2040].sum(axis=1)
    print('central',metrics(base),'cum existing',w[:n,:26].sum(),'spatial',(cum-cum.sum()*prov).abs().sum()/(2*cum.sum()),d.loc['Negros Occidental'])
    print('near',central.nlargest(2,'existing'))
    rows=[];hs=np.arange(2030,2076)
    fig,axes=plt.subplots(1,2,figsize=(8.3,3.2),layout='constrained')
    for sf in permutations(factors):
        vals=[cross(h,sf,base) for h in hs]
        lab='/'.join(f'{x:.2f}' for x in sf)
        axes[0].plot(hs,vals,label=lab,lw=1.5)
        rows.append([*sf,np.diff(envelope(2050,.5,sf))[0],np.diff(envelope(2050,1,sf))[0],cross(2050,sf,base),cross(2060,sf,base)])
    pd.DataFrame(rows,columns=['L','V','M','halfWidth','fullWidth','swap2050','swap2060']).to_csv(OUT/'ordering.csv',index=False)
    axes[0].axhline(0,color='.4',lw=.7);axes[0].set(xlabel='Reporting year',ylabel='Signed change per 100 MW swap (t)',title='a   Changing island assignment')
    axes[0].legend(fontsize=6,ncol=2,loc='lower left',frameon=False)
    for ratio,label in [(1,'25-year early-component mean'),(.48,'12-year early-component mean')]:
        p=replace(base,earlyratio=ratio)
        axes[1].plot(hs,[cross(h,factors,p) for h in hs],label=label)
    axes[1].axhline(0,color='.4',lw=.7);axes[1].set(xlabel='Reporting year',ylabel='Signed change per 100 MW swap (t)',title='b   Changing early retirement');axes[1].legend(fontsize=7,frameon=False)
    savefig(fig,'Vintage-exchange')
    comp=[]
    for ratio in [1,.48]:
        p=replace(base,earlyratio=ratio)
        comp.append([25*ratio,*metrics(p),np.diff(envelope(2050,.5,p=p))[0],cross(2050,factors,p),cross(2060,factors,p)])
    pd.DataFrame(comp,columns=['earlyMean','cum2050','peak','year','retiredMW','width','swap2050','swap2060']).to_csv(OUT/'lifetimes.csv',index=False)
    rng=np.random.default_rng(20261121);N=3000
    raw=pd.DataFrame({'life':rng.uniform(25,30,N),'earlyshape':rng.uniform(2.4928,3.5,N),'alpha':rng.uniform(.1,.3,N),
        'rho':rng.uniform(0,.2,N),'start':rng.integers(12,19,N),'stress':rng.uniform(0,1.5,N),'mass':rng.uniform(.9,1.1,N),
        'completion':rng.uniform(.5,1,N),'meanlead':rng.uniform(2,4,N),'spread':rng.uniform(1/3,1,N),'dc':rng.uniform(1,1.3,N)})
    curves=[];outputs=[]
    for pars in raw.to_dict('records'):
        rt,wt=trajectories(Params(**pars))
        curves.append(wt);outputs.append([wt[:26].sum(),wt.max(),years[wt.argmax()],rt[:26].sum()])
    yy=pd.DataFrame(outputs,columns=['cum2050','peak','peakyear','retiredMW'])
    pd.concat([raw,yy],axis=1).to_csv(OUT/'simulations.csv',index=False)
    yy.quantile([.05,.5,.95]).to_csv(OUT/'quantiles.csv')
    rr=raw.apply(rankdata);X=(rr-rr.mean())/rr.std()
    ry=yy.apply(rankdata);Y=(ry-ry.mean())/ry.std()
    beta=np.linalg.lstsq(X,Y,rcond=None)[0]
    pd.DataFrame(beta,index=raw.columns,columns=yy.columns).to_csv(OUT/'rank-coefficients.csv')
    fig,ax=plt.subplots(1,2,figsize=(8.4,3.1),layout='constrained');l,md,u=np.quantile(curves,[.05,.5,.95],axis=0)/1000
    ax[0].fill_between(years,l,u,color='#b4d8d2');ax[0].plot(years,md,c='#176555',label='Median')
    ax[0].plot(years,w.sum(0)/1000,'--',c='#86452e',label='Central scenario');ax[0].legend(frameon=False,fontsize=7);ax[0].set(xlabel='Calendar year',ylabel='Module retirements (thousand t/year)',title='a   Annual mass')
    for k,label in [(0,'Cumulative mass'),(1,'Annual peak')]:
        idx=[0,7,3,5,8,9]
        ax[1].barh(np.arange(6)+(k-.5)*.34,beta[idx,k],height=.32,label=label,color=['#176555','#bf7950'][k])
    ax[1].set(yticks=np.arange(6),yticklabels=['Lifetime','Completion','Repowering','Stress','Mean lead','Spread'],xlabel='Standardized rank coefficient',title='b   Scenario sensitivity')
    ax[1].axvline(0,c='.5',lw=.5);ax[1].legend(frameon=False,fontsize=7)
    savefig(fig,'Commissioning-uncertainty')
    fig,ax=plt.subplots(1,2,figsize=(8.3,3.1),layout='constrained')
    ax[0].stackplot(years,central.existing/1000,central.pipeline/1000,colors=['#2f6a76','#caa174'],labels=['Existing','Pipeline']);ax[0].legend(frameon=False);ax[0].set(xlabel='Calendar year',ylabel='Thousand tonnes/year',title='a   Central scenario')
    ds=d.nlargest(6,'cohort').sort_values('cohort');i=np.arange(len(ds))
    ax[1].hlines(i,ds.min(axis=1),ds.max(axis=1),color='.65');ax[1].scatter(ds.cohort,i,label='Cohort',c='#2f6a76');ax[1].scatter(ds.capacityShare,i,label='Capacity share',marker='x',color='#945528')
    ax[1].set(yticks=i,yticklabels=ds.index,xlabel='Projected retirements in 2035 (t)',title='b   Existing plants');ax[1].legend(fontsize=7,frameon=False)
    savefig(fig,'Fleet-and-provinces')
    rows=[]
    for r in [0,.25,.5,.75,1]:
        c=costs(2050).mean(1)
        def fill(ix):
            return c[ix]@np.minimum(capacity[ix],np.maximum(0,r*capacity.sum()-np.r_[0,np.cumsum(capacity[ix])[:-1]]))
        rows.append([r,fill(c.argsort()),fill((-c).argsort()),*envelope(2050,r)])
    pd.DataFrame(rows,columns=['r','islandLow','islandHigh','nationalLow','nationalHigh']).to_csv(OUT/'calendars.csv',index=False)
    # IRENA/IEA-PVPS Figure 6 uses a common characteristic age of 30 years.
    age=np.array([10,20,30,40])
    pd.DataFrame({'age':age,**{str(b):1-np.exp(-(age/30.)**b) for b in [5.3759,2.4928]}}).to_csv(OUT/'reference-curves.csv',index=False)
    assert np.allclose(calendar(3,2/3),[0,0,1/3,1/3,1/3,0])
if __name__=='__main__':run()
