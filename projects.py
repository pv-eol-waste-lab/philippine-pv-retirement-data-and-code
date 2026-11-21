from model import *
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import kron, eye, vstack, csr_matrix

def solve():
    n=len(awards);sizes=awards.mw.to_numpy()
    costs3=costs(2050)[awards.island]*sizes[:,None]
    choices=kron(eye(n),np.ones((1,3)))
    loads=kron(csr_matrix(sizes.reshape(1,-1)),eye(3))
    rows=[];sched=[]
    for r in [.5,1.]:
        target=capacity.sum()*r/3
        cons=LinearConstraint(vstack([choices,loads]).tocsr(),
            np.r_[np.full(n,1 if r==1 else 0),np.repeat(target-1,3)],
            np.r_[np.ones(n),np.repeat(target+1,3)])
        for sign,label in [(1,'low'),(-1,'high')]:
            opt=milp(sign*costs3.ravel(),integrality=np.ones(n*3),bounds=Bounds(0,1),
                constraints=cons,options={'time_limit':25,'mip_rel_gap':0.00003})
            assert opt.x is not None
            x=np.rint(opt.x.reshape(n,3))
            assert np.max(np.abs(x-opt.x.reshape(n,3)))<1e-5 and np.all(x.sum(axis=1)<=1)
            if r==1:assert np.all(x.sum(axis=1)==1)
            built=sizes@x
            assert max(abs(built-target))<1.00001
            value=(costs3*x).sum()
            match=envelope(2050,r,yearloads=built)[0 if sign==1 else 1]
            rows.append([r,label,*built,built.sum(),value,match,abs(value-match),abs(opt.fun-opt.mip_dual_bound)])
            for award,vec in zip(awards.award,x):
                sched.append([r,label,award,int(2027+np.argmax(vec)) if vec.sum() else 0])
    pd.DataFrame(rows,columns=['fraction','bound','mw2027','mw2028','mw2029','totalMW','tonnes','matchedLP','difference','solverboundgap']).to_csv(OUT/'project-bounds.csv',index=False)
    pd.DataFrame(sched,columns=['fraction','bound','award','year']).to_csv(OUT/'schedules.csv',index=False)
if __name__=='__main__':solve()
