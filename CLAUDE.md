# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS568 research project studying LLM decision-making behavior through a camera-purchasing experiment. The experiment measures how LLM personas (expert vs. novice photographers) rank attributes and choose between camera pairs across varying complexity levels, then analyzes consistency between stated priorities and actual choices.

## Experiment Design

- **Personas:** Expert photographer (experience-based prompt describing shooting conditions, gear ownership, post-processing) and Novice photographer (behavior-based prompt describing smartphone-only usage, unfamiliarity with camera culture). Prompts describe experience/behavior, not preferences — priorities should emerge from the persona.
- **LLMs under test:** GPT-4o and Claude 3.5 Sonnet, both at temperature 1.0. A no-persona baseline (no system prompt) is also run.
- **Complexity levels:** Simple (3 attributes), Moderate (6 attributes), Complex (11 attributes)
- **Session structure:** System prompt sets persona, Turn 1 elicits priority ranking, Turns 2-11 present 10 camera pairs for pairwise choice. 30 sessions per persona per condition.
- **Stimulus design:** Each pair isolates a conflict between exactly 2 attributes (all others held roughly equal). Pair 10 at each complexity level is a dominance check (one camera better on all attributes).
- **Key metric (Value-Choice Alignment):** For each non-dominance pair, the persona's relative ranking of the two conflicting attributes predicts which camera should be chosen. Alignment = fraction of pairs where the choice matches.
- **Human baseline:** 30 participants (15 expert, 15 novice) complete the same protocol for direct LLM-vs-human comparison.
- **Analysis:** Mixed-effects logistic regression with persona type, complexity, and their interaction as fixed effects; session as random intercept.

## Data Files

- `data/cameras_simple.json` — 10 pairs, 3 attributes (price, image quality, battery life)
- `data/cameras_moderate.json` — 10 pairs, 6 attributes (adds optical zoom, weight, ease of use)
- `data/cameras_complex.json` — 10 pairs, 11 attributes (adds manual controls, RAW support, burst speed, weather sealing, 4K video)

Each JSON contains `attribute_direction` (whether higher or lower is better), `attribute_descriptions` (human-readable labels for prompts), and `pairs` with fictional camera names and `tradeoff` metadata. Camera names are fabricated to avoid brand-recognition bias. Each pair's `tradeoff` field records the conflict type, which two attributes differ, and which camera wins on which attribute (or marks the pair as a dominance check).

## Key Files

- `Abstract.md` — current project abstract with research questions, metrics, and analysis plan
- `Experiment Prompts.md` — full prompt templates for system prompts, priority ranking, and pairwise choice turns

## Experiment Protocol

Full prompt templates are in `Experiment Prompts.md`. Key details:
- Camera specs must use full human-readable attribute descriptions (not raw key names) when presented to the LLM
- Pair order is fixed (1-10) across sessions to control for order effects
- Response format requires exactly: `Choice: [camera name]` and `Decisive attribute: [attribute name]`
