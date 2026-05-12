# Do LLM Personas Decide Like Real Users?

A CS568 research project comparing how persona-conditioned LLMs and screened human participants make multi-attribute decisions on a camera-purchasing task. We measure **value-choice alignment** (do choices match stated priorities?), **consistency degradation** (does alignment drop as more attributes appear?), and the **human-LLM persona gap** across expert and novice users at three complexity levels.

The paper write-up lives in `paper/`. A summary of the experiment, the data, and how to reproduce everything is below.

## Headline finding

Aggregate scores look fine — LLM and human populations match at **similarity = 0.953**, mean absolute gap of 0.047. But the cross-condition Pearson correlation is **near zero (r = 0.066)** and the patterns *diverge in direction*:

| | Simple | Moderate | Complex |
| --- | ---: | ---: | ---: |
| LLM expert    | 0.506 | 0.558 | **0.605** ↑ |
| Human expert  | 0.590 | 0.527 | 0.518 ↓ |
| LLM novice    | 0.657 | 0.541 | 0.558 |
| Human novice  | 0.590 | 0.535 | 0.549 |

- **LLM experts *improve* with complexity**, inverting the established human-expert degradation pattern.
- **The expert–novice gap reverses sign at complex**: human novices outscore experts; LLM experts outscore novices.
- **LLM novice personas are a reasonable proxy** for human novices (gaps of +0.006 and +0.009 at moderate and complex); **LLM expert personas are not** — they show the largest mismatches in the dataset.
- Within-label correlations make the cancellation explicit: **r<sub>novice</sub> = +0.993, r<sub>expert</sub> = −0.927**, near-equal-and-opposite, which is what collapses the pooled correlation to zero.

The takeaway: a one-shot similarity score can be high while underlying decision processes are entirely different (we call this the *single-number trap*). HCI evaluation of LLM-based synthetic users needs condition-level, process-oriented comparison — not aggregate alignment alone.

## Experiment at a glance

- **14 LLM personas** (7 expert + 7 novice photographers) on **Gemini 2.5 Flash-Lite**, 10 runs each → 140 sessions. Personas use biographical backstories rather than label-and-attribute prompting, so priorities emerge from context.
- **14 screened human participants** (7 expert + 7 novice) recruited from two campus photography clubs, completing the same task via Google Form.
- **Stimuli:** 11 camera attributes, 15 fixed pairs (5 per complexity level), 3 visible attributes at simple → 6 at moderate → 11 at complex. Camera names are fictional ("Alvex T1", "Brikon S2", …) to avoid brand bias.
- **Session order is fixed:** rank all 11 attributes by priority first, then 5 simple → 5 moderate → 5 complex pairs. Eliciting priorities before choices prevents post-hoc rationalization.
- **Scoring:** for each pair, weight the visible *differing* attributes by the persona's stated rank and score whether the chosen camera wins on each, producing a `[0,1]` alignment score per pair. Per-session and per-group means follow.

Full details are in `paper/paper.tex` (§ Methodology and § Evaluation Metrics). The exact prompts used are embedded in `experiment/Gemini_API_cs568.ipynb` (Turn 1 ranking template) and `data/personas.py` (system prompts).

## Repository structure

```
.
├── paper/                            Paper write-up
│   ├── paper.tex                       Final ~6-page version (submission)
│   ├── paper-draft.tex                 Longer earlier draft (kept for reference)
│   ├── CITATION.cff                    Citation metadata
│   └── figures/
│       └── vca-by-complexity.png       Main results plot
│
├── data/                             Stimulus and persona definitions
│   ├── attributes.json                 11 attributes with descriptions + directionality
│   ├── cameras_simple.json             5 pairs, 3 visible attributes each
│   ├── cameras_moderate.json           5 pairs, 6 visible attributes each
│   ├── cameras_complex.json            5 pairs, all 11 attributes visible
│   └── personas.py                     14 persona system prompts (7 expert + 7 novice)
│
├── experiment/
│   └── Gemini_API_cs568.ipynb        Experiment driver (Colab + Gemini API)
│
├── results/                          Raw experiment outputs
│   ├── llm_persona_outputs_runner{1..5}.json   Per-runner LLM sessions
│   ├── llm_persona_outputs_merged.json         All five runners combined (140 sessions)
│   └── Camera Preference Study (Responses).csv Human participant responses
│
├── metrics/                          Scoring and analysis
│   ├── METRICS.md                      Metric-by-metric math reference
│   ├── llm-scoring.py                  Computes VCA + consistency degradation for LLM
│   ├── human-scoring.py                Same for human participants
│   ├── gap-similarity.py               Computes human–LLM gap, similarity, Pearson r
│   ├── plot-vca-by-complexity.py       Regenerates the main results figure
│   └── results/                        Scored JSON outputs (LLM, human, and gap)
│
└── README.md
```

## Reproducibility

### 1. Collect LLM data (split across 5 teammates on Colab)

The notebook is designed for **Google Colab with paid Gemini API credits**, split across 5 runners in parallel.

| Runner | `RUNNER_ID` | Personas |
| --- | --- | --- |
| 1 | 1 | EXP_01 (Marcus Chen), EXP_02 (Priya Nair), EXP_03 (James Okafor) |
| 2 | 2 | EXP_04 (Sofia Rosenberg), EXP_05 (Riku Tanaka), EXP_06 (Amara Osei) |
| 3 | 3 | EXP_07 (Liam Fitzgerald), NOV_01 (Maya Thompson), NOV_02 (Kevin Park) |
| 4 | 4 | NOV_03 (Daniela Ruiz), NOV_04 (Aisha Patel), NOV_05 (Tom Bridges) |
| 5 | 5 | NOV_06 (Chloe Nakamura), NOV_07 (Ryan Okonkwo) |

Open `experiment/Gemini_API_cs568.ipynb` in Colab and:

1. Run **cell 0** — mount Google Drive.
2. Run **cell 1** — clone the repo (GitHub token prompt).
3. Run **cell 3** — install SDK; paste Gemini API key.
4. Run **cell 5** — load personas and attributes.
5. **Edit cell 7**: set `RUNNER_ID` to your assigned number (1–5); leave `NUM_RUNNERS = 5` and `N_ITERATIONS = 10`.
6. Run **cells 8–11** — kicks off the experiment.
7. Run **cell 12** — auto-commits and pushes your runner's JSON to `results/llm_persona_outputs_runner{ID}.json`.

Each session is 16 API calls (1 ranking + 15 camera pairs). Runners 1–4 produce 30 sessions each, runner 5 produces 20 — roughly 20–40 min/runner on the paid API. If Colab disconnects mid-run, re-run cells 5–11; the notebook detects existing output and resumes without burning credits.

After all five runners finish, one teammate runs **cell 14** to merge the five JSONs into `results/llm_persona_outputs_merged.json`.

### 2. Collect human data

Distribute the Google Form (mirroring the LLM session structure described in `paper/paper.tex` § Methodology); export responses as `results/Camera Preference Study (Responses).csv`.

### 3. Score and analyze

From the repo root:

```bash
python metrics/llm-scoring.py          # → metrics/results/llm/*.json
python metrics/human-scoring.py        # → metrics/results/human/*.json
python metrics/gap-similarity.py       # → metrics/results/persona-gap-similarity.json
python metrics/plot-vca-by-complexity.py   # → paper/figures/vca-by-complexity.png
```

`metrics/METRICS.md` documents each formula end-to-end.

### 4. Build the paper

`paper/paper.tex` uses the `acmart` class. Upload the `paper/` folder to Overleaf (or compile locally with `pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex`). The `figures/vca-by-complexity.png` path is set relative to the `.tex` file.

> One image (`google-form-screenshots.png`) is uploaded directly in Overleaf rather than tracked here, since it's a screenshot composite of the human-participant form.

## Citation

See `paper/CITATION.cff`.

## Authors

Ritik Hariani, Anil Muthigi, Saurav Nayak, Jyoti Rawat, Rashi Tyagi — University of Illinois Urbana-Champaign. All authors contributed equally.
