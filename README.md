# CS568 — LLM Decision-Making Study

Research project studying how LLM personas (expert vs. novice photographers) make camera-purchasing decisions across varying complexity levels.

## How to Run the Experiment Notebook

The notebook `Gemini_API_cs568.ipynb` is designed to run on **Google Colab** with **paid Gemini API credits**. The work is split across 5 teammates running in parallel.

### Runner Assignments

| Runner | `RUNNER_ID` | Personas |
|--------|-------------|----------|
| 1 | `1` | EXP_01 (Marcus Chen), EXP_02 (Priya Nair), EXP_03 (James Okafor) |
| 2 | `2` | EXP_04 (Sofia Rosenberg), EXP_05 (Riku Tanaka), EXP_06 (Amara Osei) |
| 3 | `3` | EXP_07 (Liam Fitzgerald), NOV_01 (Maya Thompson), NOV_02 (Kevin Park) |
| 4 | `4` | NOV_03 (Daniela Ruiz), NOV_04 (Aisha Patel), NOV_05 (Tom Bridges) |
| 5 | `5` | NOV_06 (Chloe Nakamura), NOV_07 (Ryan Okonkwo) |

### Step-by-step

1. Open `Gemini_API_cs568.ipynb` in Google Colab
2. Run **cell 0** — mount Google Drive
3. Run **cell 1** — clone this repo (enter your GitHub token when prompted)
4. Run **cell 3** — install SDK and enter your Gemini API key when prompted
5. Run **cell 5** — load personas and attributes
6. **Edit cell 7** before running it:
   - Set `RUNNER_ID` to **your assigned number** (1–5)
   - Set `N_ITERATIONS = 30` for the full run
   - Leave `NUM_RUNNERS = 5`
7. Run **cells 8–11** — this starts the experiment

### What to expect

- Each session = 16 API calls (1 ranking + 15 camera pairs)
- Runners 1–4 have 3 personas x 30 iterations = **90 sessions** each
- Runner 5 has 2 personas x 30 iterations = **60 sessions**
- Estimated time: **1–2 hours** per runner with paid API

### Resume support

If Colab disconnects mid-run, just **re-run cells 5 through 11**. The notebook detects the existing output file and skips completed sessions automatically. You won't lose progress or waste API credits.

### After all runners finish

1. Collect all 5 output files (`llm_persona_outputs_runner1.json` through `runner5.json`) into the `results/` folder
2. One person runs **cell 13** (the merge helper) to combine them into `llm_persona_outputs_merged.json`
3. Run `scoring.ipynb` on the merged file for analysis

### Output format

Each runner produces `results/llm_persona_outputs_runner{ID}.json` containing a list of session objects:

```json
{
  "persona_id": "EXP_01",
  "persona_name": "Marcus Chen",
  "persona_label": "expert",
  "generation_id": 1,
  "priority_order": ["raw_format_support", "image_quality_score", ...],
  "simple": {"1": {"choice": "B", "raw_response": "Choice: Brikon S2"}, ...},
  "moderate": {"1": {"choice": "B", "raw_response": "Choice: Lumion B2"}, ...},
  "complex": {"1": {"choice": "B", "raw_response": "Choice: Vantrix L3"}, ...},
  "priority_order_raw": "1. raw_format_support\n2. image_quality_score\n..."
}
```

## Repository Structure

```
data/
  attributes.json          — 11 camera attributes with descriptions and directions
  cameras_simple.json      — 5 pairs, 3 visible attributes each
  cameras_moderate.json    — 5 pairs, 6 visible attributes each
  cameras_complex.json     — 5 pairs, all 11 attributes visible
  personas.py              — 14 persona definitions (7 expert + 7 novice)
results/                   — per-runner output files and merged results
Gemini_API_cs568.ipynb     — main experiment notebook (Gemini API)
scoring.ipynb              — post-hoc scoring and analysis notebook
```
