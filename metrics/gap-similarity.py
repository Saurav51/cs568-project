import json
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
METRICS_DIR = Path(__file__).parent
LLM_VCA     = METRICS_DIR / "results" / "llm"   / "value-choice-alignment.json"
HUMAN_VCA   = METRICS_DIR / "results" / "human" / "value-choice-alignment.json"
OUTPUT      = METRICS_DIR / "results" / "persona-gap-similarity.json"

# ============================================================
# Load VCA summaries
# ============================================================
def load_json(path):
    with open(path) as f:
        return json.load(f)

llm_data   = load_json(LLM_VCA)
human_data = load_json(HUMAN_VCA)

def index_summary(records):
    return {(r["persona_label"], r["complexity"]): r["score"] for r in records}

llm_scores   = index_summary(llm_data["summary"])
human_scores = index_summary(human_data["summary"])

LABELS       = ["expert", "novice"]
COMPLEXITIES = ["simple", "moderate", "complex"]

print("LLM VCA scores:")
for (label, complexity), score in sorted(llm_scores.items()):
    print(f"  {label:8s} {complexity:10s}  {score:.4f}")
print("\nHuman VCA scores:")
for (label, complexity), score in sorted(human_scores.items()):
    print(f"  {label:8s} {complexity:10s}  {score:.4f}")

# ============================================================
# Per-condition gap: LLM score − Human score
# ============================================================
per_condition = []
for label in LABELS:
    for complexity in COMPLEXITIES:
        llm_s   = llm_scores.get((label, complexity))
        human_s = human_scores.get((label, complexity))
        if llm_s is None or human_s is None:
            continue
        per_condition.append({
            "label":        label,
            "complexity":   complexity,
            "llm_score":    round(llm_s, 6),
            "human_score":  round(human_s, 6),
            "signed_gap":   round(llm_s - human_s, 6),   # positive = LLM > human
            "absolute_gap": round(abs(llm_s - human_s), 6),
        })

print("\nPer-condition gaps (LLM − Human):")
for r in per_condition:
    print(f"  {r['label']:8s} {r['complexity']:10s}  LLM={r['llm_score']:.4f}  "
          f"Human={r['human_score']:.4f}  gap={r['signed_gap']:+.4f}")

# ============================================================
# Per-label summary (averaged across complexities)
# ============================================================
label_summary = []
for label in LABELS:
    llm_vals_l   = [llm_scores[(label, c)]   for c in COMPLEXITIES if (label, c) in llm_scores]
    human_vals_l = [human_scores[(label, c)] for c in COMPLEXITIES if (label, c) in human_scores]
    llm_mean     = float(np.mean(llm_vals_l))
    human_mean   = float(np.mean(human_vals_l))
    label_summary.append({
        "label":      label,
        "llm_mean":   round(llm_mean, 6),
        "human_mean": round(human_mean, 6),
        "signed_gap": round(llm_mean - human_mean, 6),
        "absolute_gap": round(abs(llm_mean - human_mean), 6),
    })

print("\nPer-label summary (averaged across complexities):")
for r in label_summary:
    print(f"  {r['label']:8s}  LLM={r['llm_mean']:.4f}  "
          f"Human={r['human_mean']:.4f}  gap={r['signed_gap']:+.4f}")

# ============================================================
# Expert–novice gap comparison per complexity
# ============================================================
en_gap_comparison = []
for complexity in COMPLEXITIES:
    llm_exp   = llm_scores.get(("expert", complexity))
    llm_nov   = llm_scores.get(("novice", complexity))
    human_exp = human_scores.get(("expert", complexity))
    human_nov = human_scores.get(("novice", complexity))
    if any(v is None for v in [llm_exp, llm_nov, human_exp, human_nov]):
        continue
    llm_gap   = llm_exp   - llm_nov
    human_gap = human_exp - human_nov
    en_gap_comparison.append({
        "complexity":         complexity,
        "llm_expert_score":   round(llm_exp, 6),
        "llm_novice_score":   round(llm_nov, 6),
        "llm_en_gap":         round(llm_gap, 6),
        "human_expert_score": round(human_exp, 6),
        "human_novice_score": round(human_nov, 6),
        "human_en_gap":       round(human_gap, 6),
        # positive = LLM expert–novice gap is larger than human expert–novice gap
        "gap_difference":     round(llm_gap - human_gap, 6),
    })

print("\nExpert–novice gap comparison:")
print(f"  {'Complexity':12s}  {'LLM E-N':>9s}  {'Human E-N':>10s}  {'Difference':>11s}")
for r in en_gap_comparison:
    print(f"  {r['complexity']:12s}  {r['llm_en_gap']:+.4f}     {r['human_en_gap']:+.4f}      {r['gap_difference']:+.4f}")

# ============================================================
# Summary statistics
# ============================================================
abs_gaps    = [r["absolute_gap"] for r in per_condition]
signed_gaps = [r["signed_gap"]   for r in per_condition]
llm_vals    = [r["llm_score"]    for r in per_condition]
human_vals  = [r["human_score"]  for r in per_condition]

# Pearson correlation between LLM and human scores across all 6 (label × complexity) conditions
pearson_r = float(np.corrcoef(llm_vals, human_vals)[0, 1])

mean_abs_gap  = float(np.mean(abs_gaps))
mean_sign_gap = float(np.mean(signed_gaps))

# Similarity score in [0,1]: 1 = perfect LLM–human match
similarity_score = float(1.0 - mean_abs_gap)

# Overall expert–novice gaps averaged across complexities
llm_overall_en_gap   = float(np.mean([r["llm_en_gap"]   for r in en_gap_comparison]))
human_overall_en_gap = float(np.mean([r["human_en_gap"] for r in en_gap_comparison]))

summary = {
    "mean_absolute_gap":   round(mean_abs_gap, 6),
    "mean_signed_gap":     round(mean_sign_gap, 6),
    "similarity_score":    round(similarity_score, 6),
    "pearson_correlation": round(pearson_r, 6),
}

print("\nSummary:")
for k, v in summary.items():
    print(f"  {k}: {v}")

# ============================================================
# Export
# ============================================================
output = {
    "summary": summary,
    "label_summary": label_summary,
    "per_condition": per_condition,
    "expert_novice_gap_comparison": en_gap_comparison,
}

with open(OUTPUT, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nExported to {OUTPUT}")
