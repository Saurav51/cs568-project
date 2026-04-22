import csv
import json
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR     = PROJECT_ROOT / "data"
INPUT_CSV    = PROJECT_ROOT / "results" / "Camera Preference Study (Responses).csv"
RESULTS_DIR  = Path(__file__).parent / "results" / "human"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Use only the first 14 participants (7 expert + 7 novice)
N_PARTICIPANTS = 14

# CSV column name -> canonical attribute key from data/attributes.json
CSV_TO_ATTR_KEY = {
    "price":                         "price_usd",
    "image_quality":                 "image_quality_score",
    "battery_life":                  "battery_life_hours",
    "optical_zoom_capability":       "optical_zoom_x",
    "weight":                        "weight_grams",
    "ease_of_use":                   "ease_of_use_score",
    "manual_controls_availability":  "has_manual_controls",
    "raw_image_format_support":      "raw_format_support",
    "burst_shooting_speed":          "burst_speed_fps",
    "weather_sealing":               "weather_sealed",
    "4K_video_recording":            "video_resolution_4k",
}

print(f"Input CSV: {INPUT_CSV}")
print(f"Output dir: {RESULTS_DIR}")

# ============================================================
# Load stimulus data (attributes + camera pairs)
# ============================================================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

attributes = load_json(DATA_DIR / "attributes.json")
ATTR_POOL  = attributes["attribute_pool"]
ATTR_DIR   = attributes["attribute_direction"]

STIMULI = {
    "simple":   load_json(DATA_DIR / "cameras_simple.json")["pairs"],
    "moderate": load_json(DATA_DIR / "cameras_moderate.json")["pairs"],
    "complex":  load_json(DATA_DIR / "cameras_complex.json")["pairs"],
}

PAIR_LOOKUP = {}
for level, pairs in STIMULI.items():
    for pair in pairs:
        PAIR_LOOKUP[(level, str(pair["pair_id"]))] = pair

print(f"Attributes: {len(ATTR_POOL)}")
print(f"Pairs loaded: {len(PAIR_LOOKUP)} (5 simple + 5 moderate + 5 complex)")

# ============================================================
# Load human responses → list of session dicts
# Each row = one participant = one session covering all 15 pairs.
# ============================================================
sessions = []
with open(INPUT_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        if idx > N_PARTICIPANTS:
            break

        label = "expert" if row["is_expert"].strip().lower() == "yes" else "novice"
        pid = f"{'EXP' if label == 'expert' else 'NOV'}_{idx:02d}"

        # Build priority_order from the 11 rank columns (rank 1 = most important)
        ranked = []
        for csv_col, attr_key in CSV_TO_ATTR_KEY.items():
            try:
                rank = int(row[csv_col])
            except (TypeError, ValueError):
                continue
            ranked.append((rank, attr_key))
        ranked.sort()
        priority_order = [attr for _, attr in ranked]

        # Map chosen camera names to A/B per pair
        per_level = {"simple": {}, "moderate": {}, "complex": {}}
        for level in ["simple", "moderate", "complex"]:
            for pair_id in range(1, 6):
                col = f"{level}_pair{pair_id}"
                chosen_name = (row.get(col) or "").strip()
                pair = PAIR_LOOKUP[(level, str(pair_id))]
                a_name = pair["camera_a"]["name"]
                b_name = pair["camera_b"]["name"]
                if chosen_name == a_name:
                    choice = "A"
                elif chosen_name == b_name:
                    choice = "B"
                else:
                    choice = ""
                per_level[level][str(pair_id)] = {
                    "choice": choice,
                    "chosen_name": chosen_name,
                }

        sessions.append({
            "persona_id":     pid,
            "persona_name":   pid,            # CSV is anonymous
            "persona_label":  label,
            "generation_id":  1,              # one response per participant
            "priority_order": priority_order,
            "simple":   per_level["simple"],
            "moderate": per_level["moderate"],
            "complex":  per_level["complex"],
        })

print(f"\nLoaded {len(sessions)} sessions (participants)")
for s in sessions:
    n_ranked = len(set(s["priority_order"]) & set(ATTR_POOL))
    empty = sum(
        1 for lvl in ["simple", "moderate", "complex"]
        for p in s[lvl].values() if not p["choice"]
    )
    total = sum(len(s[lvl]) for lvl in ["simple", "moderate", "complex"])
    flag = ""
    if n_ranked < 11:
        flag += f" [WARN: only {n_ranked}/11 attrs in ranking]"
    if empty > 0:
        flag += f" [WARN: {empty}/{total} unmapped choices]"
    print(f"  {s['persona_id']} label={s['persona_label']} "
          f"ranked={n_ranked}/11 empty={empty}/{total}{flag}")

# ============================================================
# Weight functions (linear)
# ============================================================
N_ATTRS = len(ATTR_POOL)

def weight_linear(rank, n):
    return n - rank + 1

# ============================================================
# Core scoring (same logic as metrics/llm-scoring.py)
# ============================================================
def to_numeric(val):
    if isinstance(val, str):
        return 1 if val.strip().lower() == "yes" else 0
    return val


def score_pair_weighted(choice, pair, priority_order, weight_fn):
    """Weighted alignment score using local re-ranking within the pair."""
    if not choice or choice not in ("A", "B"):
        return None

    rank_of = {attr: i + 1 for i, attr in enumerate(priority_order)}
    cam_a, cam_b = pair["camera_a"], pair["camera_b"]

    differing = []
    for attr in pair["pair_attributes"]:
        val_a = to_numeric(cam_a[attr])
        val_b = to_numeric(cam_b[attr])
        if val_a != val_b:
            differing.append((rank_of.get(attr, N_ATTRS), attr, val_a, val_b))

    if not differing:
        return None

    differing.sort()
    n = len(differing)

    numerator = denominator = 0.0
    for local_rank, (_, attr, val_a, val_b) in enumerate(differing, start=1):
        direction = ATTR_DIR[attr]
        winner = "A" if (val_a > val_b if direction == "higher_is_better" else val_a < val_b) else "B"
        w = weight_fn(local_rank, n)
        numerator += w * (1.0 if choice == winner else 0.0)
        denominator += w

    return numerator / denominator

# ============================================================
# Score all sessions → long-form DataFrame (one row per session × pair)
# ============================================================
rows = []
for session in sessions:
    pid    = session["persona_id"]
    pname  = session["persona_name"]
    label  = session["persona_label"]
    gen    = session["generation_id"]
    porder = session["priority_order"]

    for level in ["simple", "moderate", "complex"]:
        for pair_id_str, result in session[level].items():
            choice   = result.get("choice", "")
            pair_key = (level, pair_id_str)
            if pair_key not in PAIR_LOOKUP:
                print(f"  WARNING: pair {pair_key} not found, skipping")
                continue
            pair = PAIR_LOOKUP[pair_key]

            row = {
                "persona_id":    pid,
                "persona_name":  pname,
                "persona_label": label,
                "generation_id": gen,
                "complexity":    level,
                "pair_id":       int(pair_id_str),
                "choice":        choice,
                "chosen_name":   result.get("chosen_name", ""),
                "choice_valid":  choice in ("A", "B"),
            }
            row["score_linear"] = score_pair_weighted(choice, pair, porder, weight_linear)
            rows.append(row)

df = pd.DataFrame(rows)
complexity_code = {"simple": 1, "moderate": 2, "complex": 3}
df["complexity_code"] = df["complexity"].map(complexity_code)

print(f"\nScored {len(df)} pair trials across {df['persona_id'].nunique()} participants")
print(f"Empty/unmapped choices excluded: {(~df['choice_valid']).sum()} / {len(df)}")

# ============================================================
# Session-level scores — one row per (participant, complexity)
# ============================================================
session_means = (
    df[df["choice_valid"]]
    .groupby(["persona_id", "persona_name", "persona_label", "generation_id",
              "complexity", "complexity_code"])[["score_linear"]]
    .mean()
    .reset_index()
)

print(f"\nSession-level rows: {len(session_means)}")
print(session_means.groupby(["persona_label", "complexity"])["score_linear"]
      .count().rename("n_sessions").to_string())

summary = (
    session_means
    .groupby(["persona_label", "complexity"])["score_linear"]
    .agg(["mean", "std", "count"])
)
print("\nMean alignment (linear) by label × complexity:")
print(summary.to_string())

per_persona = (
    session_means
    .groupby(["persona_id", "persona_label", "persona_name"])
    .agg(
        mean_linear=("score_linear", "mean"),
        std_linear= ("score_linear", "std"),
        n_sessions= ("score_linear", "count"),
    )
    .sort_values("mean_linear", ascending=False)
)
print("\nPer-participant alignment (linear):")
print(per_persona.to_string())

per_complexity = (
    session_means
    .groupby(["persona_label", "complexity", "complexity_code"])
    .agg(
        mean_score=("score_linear", "mean"),
        std_score= ("score_linear", "std"),
        n_sessions=("score_linear", "count"),
    )
    .sort_values(["persona_label", "complexity_code"])
)
print("\nMean weighted alignment (linear) by label × complexity:")
print(per_complexity.to_string())
print()

for label in ["expert", "novice"]:
    subset = session_means[session_means["persona_label"] == label]
    if len(subset) < 3:
        continue
    corr = subset[["complexity_code", "score_linear"]].corr().iloc[0, 1]
    print(f"{label}: correlation(complexity, score) = {corr:.3f} "
          f"({'degradation' if corr < 0 else 'no degradation'})")

# ============================================================
# STEP 1 — Export pairwise scores
# ============================================================
output_json = RESULTS_DIR / "pairwise-scores.json"
df.to_json(output_json, orient="records", indent=2)
print(f"\nExported {len(df)} rows to {output_json}")

# ============================================================
# STEP 2 — Value-Choice Alignment
# ============================================================
session_complexity = (
    df[df["choice_valid"]]
    .groupby(["persona_id", "persona_name", "persona_label", "generation_id", "complexity"])
    ["score_linear"].sum()
    .reset_index()
    .rename(columns={"score_linear": "session_score"})
)

# For humans there is exactly 1 session per participant, so the "mean across
# generations" step from llm-scoring.py is a no-op here.
persona_complexity = (
    session_complexity
    .groupby(["persona_id", "persona_name", "persona_label", "complexity"])
    ["session_score"].mean()
    .reset_index()
    .rename(columns={"session_score": "persona_score"})
)

label_complexity = (
    persona_complexity
    .groupby(["persona_label", "complexity"])["persona_score"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={"mean": "raw_score", "count": "n_personas"})
)
label_complexity["score"] = label_complexity["raw_score"] / 5
label_complexity = label_complexity.drop(columns=["raw_score"])

print("\nValue-Choice Alignment (normalised [0, 1]):")
print(label_complexity.to_string(index=False))

vca_output = RESULTS_DIR / "value-choice-alignment.json"
with open(vca_output, "w") as f:
    json.dump({
        "summary":            label_complexity.to_dict(orient="records"),
        "individual_records": persona_complexity.to_dict(orient="records"),
    }, f, indent=2)
print(f"Exported to {vca_output}")

# ============================================================
# STEP 3 — Consistency Degradation under Feature Complexity
# ============================================================
session_pivot = session_means.pivot_table(
    index=["persona_id", "persona_name", "persona_label", "generation_id"],
    columns="complexity",
    values="score_linear"
).reset_index()

session_pivot["simple_to_moderate"]  = session_pivot["moderate"] - session_pivot["simple"]
session_pivot["moderate_to_complex"] = session_pivot["complex"]  - session_pivot["moderate"]

persona_degradation = (
    session_pivot
    .groupby(["persona_id", "persona_name", "persona_label"])
    [["simple_to_moderate", "moderate_to_complex"]]
    .mean()
    .reset_index()
)

label_degradation = (
    persona_degradation
    .groupby("persona_label")
    [["simple_to_moderate", "moderate_to_complex"]]
    .agg(["mean", "count"])
    .reset_index()
)
label_degradation.columns = [
    "_".join(c).strip("_") for c in label_degradation.columns
]
label_degradation = label_degradation.rename(columns={
    "simple_to_moderate_mean":  "simple_to_moderate",
    "moderate_to_complex_mean": "moderate_to_complex",
    "simple_to_moderate_count": "n_personas",
}).drop(columns=["moderate_to_complex_count"])

print("\nConsistency Degradation (pairwise score differences):")
print("  Negative = score drops at that transition")
print(label_degradation[["persona_label", "simple_to_moderate", "moderate_to_complex", "n_personas"]].to_string(index=False))
print()
print(persona_degradation[["persona_id", "persona_label", "simple_to_moderate", "moderate_to_complex"]].to_string(index=False))

cd_output = RESULTS_DIR / "consistency-degradation.json"
with open(cd_output, "w") as f:
    json.dump({
        "summary":            label_degradation[["persona_label", "simple_to_moderate", "moderate_to_complex", "n_personas"]].to_dict(orient="records"),
        "individual_records": persona_degradation.to_dict(orient="records"),
    }, f, indent=2)
print(f"\nExported to {cd_output}")
