"""R13 analysis: guard stress (R13-1), shape ablation from saved W5 logs (R13-2), logs-only REJECT check, drift MVP (R13-3).
usage: python -m analysis.an_r13   (run from the repository root; skips any log that does not exist)"""
import glob, itertools, json, os
import numpy as np
from p3ope.summary import classify, clopper_pearson_upper as cp, load_records

SH = ("lin", "log", "mem7", "tail2")

def agree(vs):
    return "APPROVE" if all(v == "APPROVE" for v in vs) else "REJECT" if all(v == "REJECT" for v in vs) else "NEED"

def fa_ca(rs, col):
    worse = [r for r in rs if classify(r["true10"]) == "worse"]; better = [r for r in rs if classify(r["true10"]) == "better"]
    fa = sum(r[col] == "APPROVE" for r in worse); ca = sum(r[col] == "APPROVE" for r in better); fr = sum(r[col] == "REJECT" for r in better)
    return fa, len(worse), cp(fa, len(worse)), ca, len(better), fr

def line(name, t):
    fa, nw, up, ca, nb, fr = t
    return f"{name:34s} false-approve {fa:3d}/{nw:<3d} (CP95 upper {up:.3f})  correct-approve {ca:3d}/{nb:<3d}  false-reject {fr}/{nb}"

def guard_stress(files):
    rs = [r for f in files for r in load_records(f)]
    if not rs: return
    print(f"## R13-1 guard stress (TN {rs[0]['tn']}), {len(rs)} audits, mean {np.mean([r['sec'] for r in rs]):.1f} s/audit")
    fires = sum(r["guard_fires"] for r in rs); print(f"guard fires: {fires}/{len(rs)} = {fires/len(rs):.3f}; unsupported share mean {np.mean([r['unsup'] for r in rs]):.3f} (min {min(r['unsup'] for r in rs):.3f})")
    for col in ("v5", "v6", "v7"): print(line("rule " + col, fa_ca(rs, col)))
    w = [r for r in rs if classify(r["true10"]) == "worse"]
    print(f"truly-worse runs the four shapes agreed to APPROVE (v5): {sum(r['v5']=='APPROVE' for r in w)}/{len(w)}")

def ablation(path="results/r12_e1.jsonl"):
    if not os.path.exists(path): return
    rs = load_records(path); print(f"\n## R13-2 ablation on saved W5 logs ({len(rs)} audits; post hoc, descriptive)")
    for s in SH:
        x = [dict(true10=r["true10"], c=r[f"{s}_v"]) for r in rs]; print(line(f"single shape {s}", fa_ca(x, "c")))
    def mk(shapes, guard, ff):
        out = []
        for r in rs:
            v = agree([r[f"{s}_v"] for s in shapes])
            if guard and v == "APPROVE" and r["unsup"] > .05: v = "NEED"
            if ff and v == "APPROVE" and r["ff_v"] != "APPROVE": v = "NEED"
            out.append(dict(true10=r["true10"], c=v))
        return out
    print(line("four-shape agreement (v5)", fa_ca(mk(SH, False, False), "c")))
    for left in SH:
        keep = tuple(s for s in SH if s != left)
        print(line(f"drop {left} (3 shapes)", fa_ca(mk(keep, False, False), "c")), "|", line("  + guard + ff veto", fa_ca(mk(keep, True, True), "c")).split("|")[0][34:])
    print(line("four + guard (v6)", fa_ca(mk(SH, True, False), "c"))); print(line("four + guard + ff veto (v7)", fa_ca(mk(SH, True, True), "c")))
    x = [dict(true10=r["true10"], c=r["ff_v"]) for r in rs]; print(line("free-form model alone", fa_ca(x, "c")))

def logs_only(path="results/r8_e1.jsonl"):
    if not os.path.exists(path): return
    rs = load_records(path); print(f"\n## logs-only audit under hidden taste (R8-1, {len(rs)} audits): rule v5 = v4 with APPROVE capped to NEED")
    for m in (1.0, 2.0):
        x = [r for r in rs if r["m"] == m]; b = [r for r in x if classify(r["true10"]) == "better"]; w = [r for r in x if classify(r["true10"]) == "worse"]
        print(f"taste x{m:g}: truly-better {len(b)}: v4 REJECT {sum(r['v4']=='REJECT' for r in b)} (false rejects) ; truly-worse {len(w)}: v4 REJECT {sum(r['v4']=='REJECT' for r in w)} correct, APPROVE {sum(r['v4']=='APPROVE' for r in w)} (capped to NEED by v5)")
    print("mean one-step SNIPS lift minus true 10-round lift (hidden taste x1):", round(float(np.mean([r['s_pt'] - r['true10'] for r in rs if r['m'] == 1.0])), 3))

def drift():
    for f in sorted(glob.glob("results/mvp_drift_*.jsonl")):
        rs = load_records(f); d = os.path.basename(f)[len("mvp_drift_"):-6]
        print(f"\n## R13-3 drift {d}: {len(rs)} runs, truth {rs[0]['truth']:+.4f}, mean before/after {np.mean([r['before_after'] for r in rs]):+.4f}")
        print(f"before/after wrong sign {np.mean([r['ba_wrong_sign'] for r in rs]):.3f} | SNIPS interval covers truth {np.mean([r['snips_cov'] for r in rs]):.3f} | DR {np.mean([r['dr_cov'] for r in rs]):.3f} | mean widths SNIPS {np.mean([r['snips_hi']-r['snips_lo'] for r in rs]):.4f} DR {np.mean([r['dr_hi']-r['dr_lo'] for r in rs]):.4f}")

if __name__ == "__main__":
    guard_stress(sorted(glob.glob("results/r13_e1_*.jsonl"))); ablation(); logs_only(); drift()
