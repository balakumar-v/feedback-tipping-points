from p3ope import r2_lib as R, r4_lib as W2
print("W2 lin ",[(k,round(W2.true_lift_w2("lin",k),4)) for k in (.2,.4,.6,.8,1.0,1.2,1.5,2.0,3.0)])
print("W2 quad",[(k,round(W2.true_lift_w2("quad",k),4)) for k in (.05,.1,.2,.3,.4,.6,.8)])
print("W2 cvx ",[(k,round(W2.true_lift_w2("convex",k),4)) for k in (.2,.4,.6,.9,1.2,1.5)])
print("taste x1 lin",[(k,round(R.true_lift("lin",k,0,.5,.8),4)) for k in (.2,.25,.3,.35,.4,.5)])
print("R3-3 truths: lin",[(k,round(R.true_lift("lin",k,0,0,0),4)) for k in (.4,.8,1.0)],"convex",[(k,round(R.true_lift("convex",k,0,0,0),4)) for k in (.2,.6,.9)],"quad",[(k,round(R.true_lift("quad",k,0,0,0),4)) for k in (.05,.2,.4,.8)])
