import sys, time
from p3ope import r4_lib as W2
t=time.time()
for kind,ks in (("lin",(.2,.4,.6,.8,1.0,1.5,2.0)),("quad",(.05,.1,.2,.4,.8)),("convex",(.2,.4,.6,.9,1.5))):
    print(kind,[(k,round(W2.true_lift_w2(kind,k),4)) for k in ks],flush=True)
print("homogeneous probit lin",[(k,round(W2.true_lift_w2("lin",k,sig=0),4)) for k in (.4,.8,1.2)]); print("sec",round(time.time()-t))
