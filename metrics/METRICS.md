# Metric Math

Reference document for how each metric in `llm-scoring.py` is calculated.
All metrics are computed from `results/llm/pairwise-scores.json` (Step 1 output).

---

## Inputs

- **14 personas** (7 expert, 7 novice), **10 generations each** → 140 sessions
- **15 pairs per session** (5 simple, 5 moderate, 5 complex)
- Each pair produces one `score_linear ∈ [0, 1]`

---

## Step 1 — Pairwise Score (`pairwise-scores.json`)

For each pair trial, score how well the persona's choice aligns with their stated priority ranking.

**1. Filter to visible differing attributes**
Only consider attributes in `pair_attributes` where camera A and camera B have different values. Call this set D, with `n = |D|`.

**2. Local re-rank within the pair**
Sort D by the persona's global priority rank (most important first). Assign local ranks `1, 2, …, n`.

**3. Determine the winner on each attribute**
Using `attribute_direction` (`higher_is_better` / `lower_is_better`), identify which camera (A or B) is objectively better on each attribute.

**4. Compute weighted alignment score**

Weight function (linear): `w = n − rank + 1`  
(top-ranked attribute gets weight n, bottom-ranked gets weight 1)

```
correct(attr) = 1  if the chosen camera is better on attr, else 0

score_linear = Σ w(local_rank) × correct(attr)  /  Σ w(local_rank)
               for attr in D                         for attr in D
```

**Range:** `[0, 1]` per pair. Each pair is independently normalised so every pair contributes equally regardless of how many differing attributes it has.

**Output:** One row per `(persona_id, generation_id, complexity, pair_id)` → 2100 rows.

---

## Step 2 — Value-Choice Alignment (`value-choice-alignment.json`)

Aggregates pairwise scores up to a single normalised score per `(label, complexity)` combination.

**Aggregation path:**

```
pair scores [0,1]
    ↓  sum 5 pairs per session × complexity
session_score [0,5]
    ↓  mean across 10 generations per persona × complexity
persona_score [0,5]
    ↓  mean across 7 personas per label × complexity
    ↓  divide by 5
final score [0,1]
```

**Formula:**

```
session_score(persona, gen, complexity)  = Σ score_linear  over 5 pairs

persona_score(persona, complexity)       = mean of 10 session_scores

label_score(label, complexity)           = mean of 7 persona_scores  /  5
```

**Output:** `summary` — 6 rows (2 labels × 3 complexity levels), each with `score ∈ [0, 1]`.  
`individual_records` — 42 rows (14 personas × 3 complexity levels) with `persona_score ∈ [0, 5]`.

---

## Step 3 — Consistency Degradation (`consistency-degradation.json`)

Measures how alignment score changes across adjacent complexity levels.
A negative value = score drops at that transition (degradation).

**Two transitions per session:**

```
simple → moderate:   score_moderate − score_simple
moderate → complex:  score_complex  − score_moderate
```

Since complexity codes are evenly spaced (1, 2, 3), Δx = 1 at each step, so the difference equals the slope: `slope = Δy / Δx = Δy`.

**Aggregation path:**

```
per session (persona, gen): pivot to get score at each complexity level
    ↓  compute two differences per session
    ↓  mean across 10 sessions per persona
    ↓  mean across 7 personas per label
```

**Interpretation:**
- Positive → alignment improves as more attributes are shown
- Negative → alignment degrades as more attributes are shown
- The two transitions can diverge: novices degrade sharply simple→moderate but stabilise moderate→complex

**Output:** `summary` — 4 rows (2 labels × 2 transitions) with `simple_to_moderate` and `moderate_to_complex` slopes.  
`individual_records` — 14 rows (one per persona) with both transition slopes.

---

## Metric 3 — Human–LLM Persona Gap Similarity (`persona-gap-similarity.json`)

Measures how closely LLM persona VCA scores match human participant VCA scores across all label × complexity conditions.

**Inputs:** `results/llm/value-choice-alignment.json` and `results/human/value-choice-alignment.json` (the Step 2 summaries for each population).

**Computed quantities:**

- `per_condition` — for each (label, complexity): LLM score, human score, signed gap (LLM − Human), absolute gap
- `label_summary` — LLM vs human scores averaged across the 3 complexity levels, per label
- `expert_novice_gap_comparison` — for each complexity: the expert−novice gap within each population (`en_gap = expert_score − novice_score`) and the difference between them (`gap_difference = llm_en_gap − human_en_gap`)
- `summary` — `mean_absolute_gap`, `mean_signed_gap`, `similarity_score` (= 1 − mean_absolute_gap), `pearson_correlation` across all 6 conditions

---

### Findings

**Surface similarity is misleading.**
`mean_absolute_gap = 0.047` and `similarity_score = 0.953` suggest LLM and human scores are numerically close. But `pearson_correlation = 0.066` (near zero) means they do not follow the same pattern across conditions — they happen to land in the same range without tracking the same trends.

**LLM experts show an inverted complexity trend vs humans.**
Human experts score highest at simple (0.590) and lowest at complex (0.518) — consistent degradation with complexity. LLM experts do the opposite: lowest at simple (0.506), highest at complex (0.605). This is the sharpest divergence in the dataset.

**LLM novices track humans more closely than LLM experts do.**
Novice gaps at moderate (+0.006) and complex (+0.009) are negligible. LLM novice personas are a reasonable proxy for human novices; LLM expert personas are not.

**The expert–novice gap goes in opposite directions at complex.**
At complex: LLM experts outscore novices (+0.046 gap), while human experts score *below* novices (−0.031 gap). The direction is reversed — the LLM expert persona does not replicate expert human behavior.

**Largest single mismatch: expert/simple (gap = −0.085).**
LLM experts score 8.5 pp below human experts at simple complexity. At the same level, human experts and novices are tied (0.590 each), while LLM novices massively outscore LLM experts.

**Overall conclusion for RQ1.**
LLM personas do not replicate the human expertise effect. The expert–novice gap in LLMs is not directionally consistent with the human gap, and the effect of complexity on alignment runs opposite to human behavior — particularly for expert personas.

---

## File Structure

```
metrics/
├── llm-scoring.py              ← Steps 1–3 for LLM sessions
├── human-scoring.py            ← Steps 1–3 for human participants (same logic)
├── gap-similarity.py           ← Metric 3: Human–LLM gap
├── METRICS.md                  ← this file
└── results/
    ├── llm/
    │   ├── pairwise-scores.json          ← Step 1: 2100 rows, one per pair trial
    │   ├── value-choice-alignment.json   ← Step 2: aggregated alignment scores
    │   └── consistency-degradation.json  ← Step 3: pairwise complexity slopes
    ├── human/
    │   ├── pairwise-scores.json
    │   ├── value-choice-alignment.json
    │   └── consistency-degradation.json
    └── persona-gap-similarity.json       ← Metric 3: Human–LLM gap similarity
```
