import json, numpy as np, pandas as pd, sys
e3=pd.DataFrame([json.loads(l) for f in ("results/r2_e3_a.jsonl","results/r2_e3_b.jsonl") for l in open(f)])
e5=pd.DataFrame([json.loads(l) for l in open("results/r2_e5.jsonl")])
def bars(df,keycol,keys,y0,label,x0=0,w=440):
    """stacked verdict bars: one row per key."""
    out=[]; h=26; gap=10
    for i,k in enumerate(keys):
        x=df[df[keycol]==k]; n=len(x); ap=(x.v3=="APPROVE").mean(); ne=(x.v3=="NEED").mean(); re=(x.v3=="REJECT").mean()
        y=y0+i*(h+gap); cx=x0+205
        out.append(f'<text x="{x0}" y="{y+18}" class="lab">{label(k,x)}</text>')
        for frac,col in ((ap,"#0b7a5a"),(ne,"#a05a00"),(re,"#b93220")):
            wd=frac*w; 
            if wd>0: out.append(f'<rect x="{cx}" y="{y}" width="{wd:.1f}" height="{h}" fill="{col}"/>'); 
            if wd>28: out.append(f'<text x="{cx+wd/2:.1f}" y="{y+18}" class="bt" text-anchor="middle">{frac*100:.0f}%</text>')
            cx+=wd
        out.append(f'<text x="{x0+205+w+8}" y="{y+18}" class="sm">n={n}</text>')
    return "\n".join(out)
A=e3[e3.kind=="lin"]
ka=sorted(A.kappa.unique())
lab_a=lambda k,x:f'κ={k:g}  {x.true10.iloc[0]:+.3f} '+('better' if x.true10.iloc[0]>0.002 else ('worse' if x.true10.iloc[0]<-0.002 else 'marginal'))
pa=bars(A,"kappa",ka,0,lab_a)
S=e5[e5.m==1.0]; ks=sorted(S.kappa.unique())
lab_s=lambda k,x:f'κ={k:g}  {x.true10.iloc[0]:+.3f} '+('better' if x.true10.iloc[0]>0.002 else ('worse' if x.true10.iloc[0]<-0.002 else 'marginal'))
ps=bars(S,"kappa",ks,0,lab_s)
nA=len(A); nS=len(S)
html=open("figures/diagram_template.html").read().replace("{{PANEL_A}}",pa).replace("{{PANEL_S}}",ps).replace("{{HA}}",str(len(ka)*36)).replace("{{HS}}",str(len(ks)*36))
open("figures/diagram.html","w").write(html); print("ok",nA,nS)
