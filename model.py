from dataclasses import dataclass
from pathlib import Path
from math import gamma
import numpy as np
import pandas as pd
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
plants = pd.read_csv(ROOT / 'data/plants.csv')
awards = pd.read_csv(ROOT / 'data/awards.csv')
capacity = awards.groupby('island').mw.sum().to_numpy()
years = np.arange(2025, 2076)
factors = np.array([.95, .93, .90])
assert len(plants)==67 and len(awards)==98
assert np.isclose(awards.mw.sum(),9244.012) and np.isclose(plants.mw.sum(),2811.07)

@dataclass
class Params:
    life: float=25
    earlyshape: float=3.5
    alpha: float=.2
    rho: float=.1
    start: int=15
    stress: float=1
    mass: float=1
    completion: float=1
    meanlead: float=3
    spread: float=2/3
    dc: float=1
    earlyratio: float=1

def mass(y):
    return 2.72e25*np.exp(-np.asarray(y)/37.11)

def cdf(age,factor,p):
    a=np.maximum(age,0)
    def wb(mean,shape):
        return -np.expm1(-(a*gamma(1+1/shape)/(mean*factor))**shape)
    return ((1-p.alpha-p.rho)*wb(p.life,5.3759)+p.alpha*wb(p.life*p.earlyratio,p.earlyshape)
            +p.rho*np.clip((a-p.start+1)/6,0,1))

def calendar(mean,spread):
    lower=int(np.floor(mean))
    shift=mean-lower
    weights=np.zeros(6)
    for j,b in [(lower,1-shift),(lower+1,shift)]:
        if b:
            weights[[j-1,j,j+1]]+=b*np.array([spread/2,1-spread,spread/2])
    assert np.isclose(weights.sum(),1) and np.isclose(weights@np.arange(6),mean)
    return weights

def trajectories(p,order=factors,detail=False):
    sf=1-p.stress*(1-np.array(order))
    w=calendar(p.meanlead,p.spread)
    y=np.r_[plants.year,np.tile(2025+np.arange(1,6),3)]
    g=np.r_[plants.g,np.repeat(np.arange(3),5)]
    mw=np.r_[plants.mw,(capacity[:,None]*w[1:]*p.completion*p.dc).ravel()]
    end=cdf(np.arange(2024,2076)[None,:]-y[:,None],sf[g,None],p)
    ret=mw[:,None]*np.diff(end,axis=1)
    tonnes=ret*mass(y[:,None])*p.mass
    if detail:return ret,tonnes
    return ret.sum(axis=0),tonnes.sum(axis=0)

def costs(h,order=factors,p=None):
    if p is None:p=Params()
    y=np.arange(2027,2030)
    return cdf(h-y[None,:],np.asarray(order)[:,None],p)*mass(y)*p.mass

def envelope(h,r,order=factors,p=None,yearloads=None):
    c=costs(h,order,p)
    b=capacity.sum()*r*np.ones(3)/3 if yearloads is None else np.array(yearloads)
    upper=np.kron(np.eye(3),np.ones((1,3)))
    cols=np.tile(np.eye(3),(1,3))
    ans=[]
    for sign in [1,-1]:
        opt=linprog(sign*c.ravel(),A_ub=upper,b_ub=capacity,A_eq=cols,b_eq=b,bounds=(0,None),method='highs')
        assert opt.success
        ans.append(sign*opt.fun)
    return np.array(ans)

def metrics(p):
    ret,w=trajectories(p)
    return [w[:26].sum(),w.max(),years[w.argmax()],ret[:26].sum()]
