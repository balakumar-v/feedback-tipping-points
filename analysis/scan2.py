import time
from p3ope import r2_lib as R
t=time.time(); print("standin taste x1 lin:",[(k,round(R.true_lift("lin",k,0,.5,.8),4)) for k in (0,.1,.2,.25,.3,.35,.4,.5,.6)])
print("sec",round(time.time()-t))
# audit timing
from experiments import r2_e5 as E5, r3_e3 as E3, r2_e3 as E
t=time.time(); r=E5.audit(1.0,.4,3000,500,-0.01); print("slice audit s",round(time.time()-t,1),r["v3"])
t=time.time(); r=E.audit("lin",.4,300,R.true_lift("lin",.4,0,0,0),0); print("logs audit s (B=30, 4 shapes)",round(time.time()-t,1),r["lin_v"])
