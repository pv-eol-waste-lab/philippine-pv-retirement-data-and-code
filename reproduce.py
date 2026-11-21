import analysis
import figures
import projects
import benchmarks
import planning
import tables
from model import *
from itertools import combinations

def check_bounds():
    A=np.vstack([np.kron(np.eye(3),np.ones((1,4))),np.tile(np.eye(4)[:3],(1,3))])
    bases=[]
    for T in combinations(range(12),6):
        matrix=A[:,T]
        if abs(np.linalg.det(matrix))>.5:bases.append((T,np.linalg.inv(matrix)))
    for r in [0,.25,.5,.75,1]:
        b=np.r_[capacity,[r*sum(capacity)/3]*3]
        c=np.column_stack([costs(2050),np.zeros(3)]).ravel()
        feasible=[]
        for T,inv in bases:
            x=inv@b
            if x.min()>=-1e-8:feasible.append(c[list(T)]@x)
        assert np.allclose(envelope(2050,r),[min(feasible),max(feasible)],rtol=0,atol=1e-6)
if __name__=='__main__':
    analysis.run()
    figures.run()
    benchmarks.run()
    planning.run()
    projects.solve()
    tables.make()
    check_bounds()
