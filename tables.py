from model import *

def tab(name,caption,head,rows,align):
    cells=lambda row:' & '.join(map(str,row))+r' \\'
    return '\n'.join([r'\begin{table}[htbp]\centering\small',r'\caption{'+caption+r'}\label{tab:'+name+'}',r'\begin{tabular}{'+align+r'}\toprule',cells(head),r'\midrule',*[cells(row) for row in rows],r'\bottomrule\end{tabular}\end{table}'])+'\n'

def make():
    read=lambda name:pd.read_csv(OUT/(name+'.csv'))
    tables={}
    a=read('calendars');E=read('annual').query('year<=2050').existing.sum()
    rows=[[f'{x.r*100:.0f}',*[f'{(E+k)/1000:.2f}' for k in x[1:]]] for x in a.itertuples(index=False)]
    tables['cal']=tab('cal','National cumulative module retirements through 2050 (thousand tonnes). All four endpoints include the same existing-fleet contribution.',[r'Built (\%)','Island min.','Island max.','National min.','National max.'],rows,'rrrrr')
    a=read('ordering'); rows=[[f'{v:.2f}' for v in x[:3]]+[f'{v/1000:.2f}' for v in x[3:5]]+[f'{v:+.1f}' for v in x[5:]] for x in a.itertuples(index=False,name=None)]
    tables['ordering']=tab('ordering','All assignments of the three lifetime factors. Widths of the national-calendar interval are in thousand tonnes through 2050. Signed changes are tonnes per 100 MW exchange.',['Luzon','Visayas','Mindanao','Half width$^*$','Full width$^*$',r'$\Delta_{2050}$',r'$\Delta_{2060}$'],rows,'rrrrrrr').replace('Half width$^*$',r'50\% built').replace('Full width$^*$',r'100\% built')
    a=read('project-bounds');rows=[[f'{x.fraction*100:.0f}',x.bound,*[f'{v:,.2f}' for v in [x.mw2027,x.mw2028,x.mw2029,x.totalMW]],f'{x.tonnes:,.1f}',f'{x.solverboundgap:.2f}'] for x in a.itertuples()]
    tables['binary']=tab('binary','Feasible whole-award schedules. Annual and total capacities are in MW. Mass counts pipeline retirements through 2050. Gap is the absolute distance in tonnes between the incumbent and the solver bound.',[r'Built (\%)','End','2027','2028','2029','Total MW','Mass (t)','Gap (t)'],rows,'rlrrrrrr')
    a=read('lifetimes');rows=[[f'{x.earlyMean:.0f}',f'{x.cum2050:,.0f}',f'{x.peak:,.0f}',f'{x.year:.0f}',f'{x.width:,.0f}',f'{x.swap2050:+.0f}',f'{x.swap2060:+.0f}'] for x in a.itertuples()]
    tables['early']=tab('early','Effect of the unstressed early-component mean. Cumulative mass (through 2050), peak (2025--2075) and peak year use full construction. Width is the half-build national-calendar range. Swap columns use a 100 MW exchange.',['Mean (yr)','Mass (t)','Peak (t/yr)','Peak year','Width (t)',r'$\Delta_{2050}$ (t)',r'$\Delta_{2060}$ (t)'],rows,'rrrrrrr')
    a=read('quantiles');rows=[[f'{100*x[0]:.0f}',f'{x[1]:,.0f}',f'{x[2]:,.0f}',f'{x[3]:.0f}',f'{x[4]:,.0f}'] for x in a.itertuples(index=False,name=None)]
    tables['mc']=tab('mc','Marginal percentiles across 3,000 scenarios. Cumulative mass and retired capacity refer to 2025--2050; the peak and its year are computed separately for each trajectory through 2075.',['Percentile','Mass (t)','Peak (t/yr)','Peak year','Retired MWdc'],rows,'rrrrr')
    a=read('reference-curves');rows=[[f'{x[0]:.0f}',f'{100*x[1]:.2f}',f'{100*x[2]:.2f}'] for x in a.itertuples(index=False,name=None)]
    tables['irena']=tab('irena','Reference Weibull cumulative loss (percent of installed capacity) at selected ages for the curves in Figure 6 of IRENA and IEA-PVPS. Both curves have characteristic age 30 years.',['Age (yr)',r'Regular loss ($\beta=5.3759$)',r'Early loss ($\beta=2.4928$)'],rows,'rrr')
    for key,t in tables.items():(OUT/(key+'-table.tex')).write_text(t)
if __name__=='__main__':make()
