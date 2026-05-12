import json
from pathlib import Path

import matplotlib.pyplot as plt

METRICS_DIR = Path(__file__).parent
INPUT_JSON  = METRICS_DIR / "results" / "persona-gap-similarity.json"
OUTPUT_PNG  = Path(__file__).parent.parent / "vca-by-complexity.png"

with open(INPUT_JSON) as f:
    data = json.load(f)

COMPLEXITIES = ["simple", "moderate", "complex"]
COMPLEXITY_LABELS = ["Simple\n(3 attributes)", "Moderate\n(6 attributes)", "Complex\n(11 attributes)"]

scores = {(r["label"], r["complexity"]): (r["llm_score"], r["human_score"]) for r in data["per_condition"]}

llm_expert   = [scores[("expert", c)][0] for c in COMPLEXITIES]
llm_novice   = [scores[("novice", c)][0] for c in COMPLEXITIES]
human_expert = [scores[("expert", c)][1] for c in COMPLEXITIES]
human_novice = [scores[("novice", c)][1] for c in COMPLEXITIES]

fig, ax = plt.subplots(figsize=(7.5, 5.0))

x = list(range(len(COMPLEXITIES)))

ax.plot(x, llm_expert,   color="#E07A2E", marker="o", linewidth=2.2, markersize=8,
        label="LLM Expert")
ax.plot(x, llm_novice,   color="#E2B62C", marker="o", linewidth=2.2, markersize=8,
        label="LLM Novice")
ax.plot(x, human_expert, color="#1F3A5F", marker="s", linewidth=2.2, markersize=8,
        label="Human Expert")
ax.plot(x, human_novice, color="#5BA8D8", marker="s", linewidth=2.2, markersize=8,
        label="Human Novice")

ax.set_xticks(x)
ax.set_xticklabels(COMPLEXITY_LABELS, fontsize=11)
ax.set_xlabel("Task Complexity", fontsize=12, labelpad=10)
ax.set_ylabel("Value–Choice Alignment Score", fontsize=12, labelpad=10)

ax.set_ylim(0.45, 0.70)
ax.set_yticks([0.45, 0.50, 0.55, 0.60, 0.65, 0.70])
ax.grid(True, axis="y", linestyle="-", linewidth=0.6, color="#E5E5E5", zorder=0)
ax.set_axisbelow(True)

for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
for spine in ("left", "bottom"):
    ax.spines[spine].set_color("#666666")

ax.tick_params(axis="both", colors="#333333", labelsize=10)

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.18),
    ncol=4,
    frameon=False,
    fontsize=11,
    handlelength=2.5,
    columnspacing=1.8,
)

plt.tight_layout()
fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Saved {OUTPUT_PNG}")
