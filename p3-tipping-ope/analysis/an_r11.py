import json, numpy as np, pandas as pd
from scipy.stats import beta as Be
def cp(x, n): return 1.0 if x >= n else float(Be.ppf(.95, x + 1, n - x))
d = pd.DataFrame([json.loads(l) for l in open("results/r11_e1.jsonl")]); d["cls"] = np.where(d.true10 < -.002, "worse", np.where(d.true10 > .002, "better", "marg"))
print("guard: csup", sorted(d.csup.unique()), "unsupported share", d.unsup.round(3).unique()[:5], "pass(<=5%) rate", round((d.unsup <= .05).mean(), 3))
for gen in ("W4", "W3"):
    g = d[d.gen == gen]
    if not len(g): continue
    print(f"\n== {gen} n={len()} " if False else f"\n== {gen} runs {len(g)}")
    print(g.groupby(["kind", "kappa", "true10"]).v6.value_counts().unstack(fill_value=0).round(4).to_string())
    w = g[g.cls == "worse"]; nb = w[w.true10.abs() <= .01]; b = g[g.cls == "better"]
    for tag, col in (("v6 (with guard)", "v6"), ("v5 (no guard, same slice)", "v5")):
        fa = int((w[col] == "APPROVE").sum()); fn = int((nb[col] == "APPROVE").sum()); fr = int((b[col] == "REJECT").sum()); ca = int((b[col] == "APPROVE").sum())
        print(f"{tag}: FA {fa}/{len(w)} CP95 upper {cp(fa, len(w)):.3f} | near-boundary FA {fn}/{len(nb)} upper {cp(fn, len(nb)):.3f} | false rejects {fr}/{len(b)} | correct-approve {ca}/{len(b)}")
