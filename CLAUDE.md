# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS568 research project studying LLM decision-making behavior through a camera-purchasing experiment. The experiment measures how LLM personas (expert vs. novice photographers) rank attributes and choose between camera pairs across varying complexity levels, then analyzes consistency between stated priorities and actual choices.

## Experiment Design

- **Personas:** 14 named personas (7 domain experts + 7 novices) defined in `data/personas.py` as `EXPERT_PERSONAS` and `NOVICE_PERSONAS`. Each persona has a biographical system prompt describing experience, gear, capabilities, and purchase context — priorities should emerge from the persona's situation rather than from explicit instructions. The 7 experts span wedding/portrait, wildlife, street/documentary, commercial product, landscape/astro, fashion/editorial, and sports photography. The 7 novices span casual college, family-event, food blogging, retiree beginner, travel, fitness-content, and event-planning contexts.
- **Complexity levels:** Complexity is manipulated within-session as the number of visible attributes per camera pair — simple (3 visible attributes), moderate (6), complex (all 11).
- **Session structure:** One session = one conversation per persona covering all 15 pairs. The system prompt sets the persona (once), Turn 1 elicits a single priority ranking over all 11 attributes, and Turns 2–16 present the 15 pairs in fixed order (5 simple → 5 moderate → 5 complex). The same priority ranking is used to score every pair regardless of how many attributes are visible.
- **Sessions per run:** 14 (one session per persona). Repeat N runs per persona for statistical power.
- **Stimulus design:** 5 pairs per complexity level (15 total) stored in `data/cameras_{simple,moderate,complex}.json`. Each pair's `pair_attributes` field lists exactly which attributes are visible for that pair, and only those attributes are shown to the LLM/participant. Different pairs within a complexity level probe different attribute subsets so no single tradeoff dominates the design.
- **Key metric (Value–Choice Alignment):** For each pair, identify the attributes that differ between the two cameras. The predicted choice is the camera that wins on the *highest-ranked differing attribute* according to the persona's Turn 1 ranking (lexicographic over visible differing attributes). Score 1 if the actual choice matches the prediction, 0 otherwise. Per-session alignment = mean over the 15 pairs.
- **Human baseline:** Recruited human participants complete the same protocol for direct LLM-vs-human comparison. Screening criteria mirror the LLM persona labels (expert: owns 3+ cameras, has purchased gear in the last 2 years, can explain technical concepts; novice: primarily uses phone cameras, has never bought a dedicated camera).
- **Analysis:** Mixed-effects logistic regression with persona label (expert vs. novice), complexity, and their interaction as fixed effects; session (and persona nested within label) as random intercepts.

## Data Files

- `data/attributes.json` — shared metadata: the 11-attribute pool, human-readable descriptions, and directionality (`higher_is_better` / `lower_is_better`)
- `data/cameras_simple.json` — 5 pairs, 3 visible attributes per pair (attribute subset varies across pairs)
- `data/cameras_moderate.json` — 5 pairs, 6 visible attributes per pair (attribute subset varies across pairs)
- `data/cameras_complex.json` — 5 pairs, all 11 attributes visible per pair
- `data/personas.py` — 14 persona dicts (`EXPERT_PERSONAS`, `NOVICE_PERSONAS`, `ALL_PERSONAS`) with `id`, `name`, `label`, `background`, and `system_prompt` fields

Camera JSON files contain `pairs`, where every pair has a `pair_attributes` list (the attributes visible for that pair) and the two cameras' values for only those attributes. Attribute descriptions and directionality live in `data/attributes.json`. Camera names are fabricated to avoid brand-recognition bias.

## Key Files

- `Abstract.md` — the original project abstract (preserved as-is for reference)
- `Abstract - Revised.md` — the revised abstract reflecting the current experiment design
- `Experiment Prompts.md` — session structure, Turn 1 priority ranking prompt, and pair-presentation prompt
- `data/personas.py` — canonical source of persona system prompts (do not mix content across personas or edit at run time)

## Experiment Protocol

Full prompt templates are in `Experiment Prompts.md`. Key details:
- Persona system prompts are loaded verbatim from `data/personas.py`
- Camera specs must use full human-readable attribute descriptions (from `data/attributes.json`), not raw key names, when presented to the LLM
- For each pair, only the attributes listed in its `pair_attributes` field are shown
- Pair order is fixed within sessions: simple (pairs 1–5) → moderate (pairs 1–5) → complex (pairs 1–5)
- Response format requires exactly: `Choice: [camera name]` and `Decisive attribute: [attribute name]`
