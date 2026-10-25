import json, os, numpy as np, pandas as pd
from scipy.stats import beta as Be
def cp(x, n): return 1.0 if x >= n else float(Be.ppf(.95, x + 1, n - x))
def rep(path, tag):
    if not os.path.exists(path): return
    d = pd.DataFrame([json.loads(l) for l in open(path)]); d["cls"] = np.where(d.true10 < -.002, "worse", np.where(d.true10 > .002, "better", "marg"))
    print(f"\n== {tag} runs {len(d)}"); print(d.groupby(["kind", "kappa", "true10"]).v7.value_counts().unstack(fill_value=0).round(4).to_string())
    w = d[d.cls == "worse"]; nb = w[w.true10.abs() <= .01]; b = d[d.cls == "better"]
    for col in ("v6", "v7"):
        fa = int((w[col] == "APPROVE").sum()); fn = int((nb[col] == "APPROVE").sum()); fr = int((b[col] == "REJECT").sum()); ca = int((b[col] == "APPROVE").sum())
        print(f"{col}: FA {fa}/{len(w)} CP95 upper {cp(fa, len(w)):.3f} | near-boundary FA {fn}/{len(nb)} upper {cp(fn, len(nb)):.3f} | false rejects {fr}/{len(b)} | correct-approve {ca}/{len(b)} = {ca/max(len(b),1):.2f}")
    return d
rep("results/r12_e1.jsonl", "W5 (held-out, pre-registered P55)"); rep("results/r12_e1_w4.jsonl", "W4 retro (descriptive)")
