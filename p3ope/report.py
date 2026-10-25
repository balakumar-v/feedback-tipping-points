"""Build a single self-contained HTML dashboard (no JavaScript, no external requests) from the run logs.

    python -m p3ope report            # writes docs/dashboard.html

Every number on the page is computed from results/*.jsonl at build time; nothing is typed in by hand.
"""
from __future__ import annotations

import base64
import os
from html import escape

from p3ope import summary as S

LOGS = (("W5", "results/r12_e1.jsonl", "Fresh held-out generator W5 (pre-registered target)"),
        ("W4", "results/r12_e1_w4.jsonl", "Earlier delayed-onset generator W4 (retro, descriptive)"))
CSS = """
:root{color-scheme:light dark;--bg:#fafaf7;--fg:#1b1f23;--mut:#5b636b;--card:#fff;--bd:#d9dcd6;--ok:#0b6b4f;--warn:#8a4b00;--bad:#a8301f;--acc:#1f4e8c}
@media (prefers-color-scheme:dark){:root{--bg:#14171a;--fg:#e8eaec;--mut:#9aa3ab;--card:#1c2024;--bd:#33393f;--ok:#4cc79d;--warn:#e0a24a;--bad:#f0877a;--acc:#8ab4f0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1000px;margin:0 auto;padding:1.5rem 1rem 4rem}h1{font-size:1.7rem;margin:.2rem 0}h2{font-size:1.2rem;margin:2rem 0 .6rem}
.lead{color:var(--mut);max-width:70ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.8rem}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:.9rem 1rem}.card b{display:block;font-size:1.7rem;line-height:1.2}
.card span{color:var(--mut);font-size:.88rem}.ok b{color:var(--ok)}.bad b{color:var(--bad)}.verd{display:flex;gap:.6rem;flex-wrap:wrap;margin:.8rem 0}
.pill{border:1px solid currentColor;border-radius:999px;padding:.15rem .7rem;font-weight:600;font-size:.9rem}.p-a{color:var(--ok)}.p-n{color:var(--warn)}.p-r{color:var(--bad)}
.wrap{overflow-x:auto;border:1px solid var(--bd);border-radius:10px;background:var(--card)}table{border-collapse:collapse;width:100%;min-width:640px;font-size:.92rem}
caption{text-align:left;padding:.6rem .8rem;color:var(--mut)}th,td{padding:.45rem .8rem;border-top:1px solid var(--bd);text-align:left;white-space:nowrap}
th{font-weight:600;background:transparent}td.n{font-variant-numeric:tabular-nums}.bar{display:inline-flex;width:90px;height:.7rem;border-radius:3px;overflow:hidden;vertical-align:middle;margin-right:.5rem;background:var(--bd)}
.bar i{display:block;height:100%}.i-a{background:var(--ok)}.i-n{background:var(--warn)}.i-r{background:var(--bad)}.worse{color:var(--bad)}.better{color:var(--ok)}
img{max-width:100%;height:auto;border:1px solid var(--bd);border-radius:10px;background:#fff}ul{padding-left:1.2rem}code{background:var(--card);border:1px solid var(--bd);border-radius:4px;padding:0 .3rem}
:focus-visible{outline:3px solid var(--acc);outline-offset:2px}footer{margin-top:2.5rem;color:var(--mut);font-size:.85rem}
"""


def _card(value: str, label: str, cls: str = "") -> str:
    return f'<div class="card {cls}"><b>{escape(value)}</b><span>{escape(label)}</span></div>'


def _bar(counts: dict, n: int) -> str:
    seg = "".join(f'<i class="i-{k[0].lower()}" style="width:{100 * counts.get(k, 0) / n:.1f}%"></i>'
                  for k in ("APPROVE", "NEED", "REJECT") if counts.get(k))
    txt = " / ".join(f"{counts.get(k, 0)} {lab}" for k, lab in (("APPROVE", "approve"), ("NEED", "need data"), ("REJECT", "reject")))
    return f'<span class="bar" role="img" aria-label="{txt}">{seg}</span>{txt}'


def _table(tag: str, recs: list) -> str:
    rows = []
    for c in S.cells(recs):
        rows.append(f'<tr><td>{escape(c["kind"])}</td><td class="n">{c["kappa"]:g}</td>'
                    f'<td class="n {c["cls"]}">{c["true10"]:+.4f} ({c["cls"]})</td><td class="n">{c["n"]}</td>'
                    f'<td>{_bar(c["v6"], c["n"])}</td><td>{_bar(c["v7"], c["n"])}</td></tr>')
    return (f'<div class="wrap" tabindex="0" role="region" aria-label="{tag} per-cell verdicts"><table>'
            "<caption>Verdicts per scenario. A truly worse policy (negative lift) must not be approved.</caption>"
            "<thead><tr><th scope=col>Fatigue shape</th><th scope=col>kappa</th><th scope=col>True 10-round lift</th>"
            "<th scope=col>Runs</th><th scope=col>Rule v6</th><th scope=col>Rule v7 (final)</th></tr></thead>"
            f'<tbody>{"".join(rows)}</tbody></table></div>')


def build(out: str = "docs/dashboard.html") -> str:
    data = {tag: S.load_records(path) for tag, path, _ in LOGS}
    h5, h4 = S.headline(data["W5"], "v7"), S.headline(data["W4"], "v7")
    h5_6 = S.headline(data["W5"], "v6")
    img = ""
    if os.path.exists("figures/p3_diagram.png"):
        with open("figures/p3_diagram.png", "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode()
        img = f'<h2>Pipeline</h2><img alt="Pipeline diagram: logs and randomised slice feed four fatigue models, then a verdict" src="data:image/png;base64,{b64}">'
    cards = "".join([
        _card(f"{h5['false_approve']}/{h5['n_worse']}", f"false approvals, final rule v7, fresh generator (95% upper bound {h5['fa_upper']:.3f}; target 0.05)", "ok"),
        _card(f"{h5_6['false_approve']}/{h5_6['n_worse']}", f"false approvals without the free-form veto (rule v6, upper bound {h5_6['fa_upper']:.3f})", "bad"),
        _card(f"{h5['correct_approve']}/{h5['n_better']}", f"truly better policies approved (rate {h5['correct_approve_rate']:.2f}; target 0.50)", "ok"),
        _card(f"{h4['false_approve']}/{h4['n_worse']}", f"false approvals on the earlier delayed-onset generator W4 (upper bound {h4['fa_upper']:.3f}; misses its 0.05 target)", "bad"),
    ])
    sections = "".join(f"<h2>{escape(title)}</h2>{_table(tag, data[tag])}" for tag, _, title in LOGS)
    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Measured Feedback Tipping Points - results dashboard</title><style>{CSS}</style></head><body><main>
<h1>Did the policy actually work, or did it just look like it?</h1>
<p class="lead">A pre-rollout audit for ranking policies. It compares a measured user-fatigue coefficient with the <em>tipping point</em> where the new policy's forecast lift becomes zero, and returns one of three verdicts.</p>
<div class="verd"><span class="pill p-a">APPROVE</span><span class="pill p-r">REJECT</span><span class="pill p-n">NEED RANDOMIZED DATA</span></div>
<h2>Headline results (simulator, computed from the raw logs)</h2><div class="grid">{cards}</div>
<p class="lead">All results come from our own simulators, not production traffic. Failed targets are shown as they are, not hidden.</p>
{img}{sections}
<h2>Known limits</h2><ul><li>Fatigue that starts only at the third or later repeat is not fully covered (rounds R8-2 and R9-1 failed their targets).</li>
<li>Rule v7 was validated on simulators we wrote; real dynamics data (KuaiRand) was a stretch goal and was not done.</li>
<li>Always abstaining would also pass the false-approval target, which is why correct-approve is reported beside it.</li></ul>
<footer>Generated by <code>python -m p3ope report</code> from <code>results/*.jsonl</code>. Full pass/fail record: <code>docs/RESULTS.md</code>.</footer>
</main></body></html>"""
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out
