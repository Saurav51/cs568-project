# Do LLM Personas Decide Like Real Users? Evaluating Value–Decision Coherence Across Expertise Levels

**Team:** Rashi Tyagi [rtyagi4], Jyoti Rawat [jrawat2], Ritik Hariani [ritikh2], Anil Muthigi [muthigi2], Saurav Nayak [sgnayak2]

## Abstract

Large language models (LLMs) are increasingly used to simulate user personas in design and market research. For example, researchers may prompt a model to behave as an experienced photographer to predict how real photography enthusiasts might evaluate a new camera. While prior work has shown that LLM personas can mimic human-like language and surface-level preferences, a critical question remains unanswered: do these personas make decisions the way real users do, or do they just talk like them?

We investigate this through the concept of **value–decision coherence**, which measures whether a persona's actual product choices align with the priorities it previously stated as important. For instance, if a persona says "image quality matters most to me," does it consistently choose the camera with better image quality when forced to trade off against other features like price or portability? We then examine whether this consistency differs between domain experts (experienced photographers who have purchased and used multiple cameras, follow photography communities, and understand technical specifications) and novice users (casual phone photographers with little experience evaluating dedicated cameras and no familiarity with technical terms like sensor size or dynamic range).

We focus on a single product domain, digital cameras, to enable controlled analysis of product tradeoffs. We design fictional products (to avoid LLM bias from pre-existing knowledge of real brands) with **carefully isolated attribute tradeoffs** at three levels of feature complexity: simple (3 attributes), moderate (6 attributes), and complex (11 attributes). Critically, each product pair is constructed so that exactly two attributes are in conflict — one camera is better on attribute X while the other is better on attribute Y — and all remaining attributes are held roughly equal. This controlled tradeoff design ensures that each choice has a clear "ground truth" for which attribute was decisive, enabling precise measurement of whether the persona's stated priority ranking predicts its actual choice. One additional pair per complexity level serves as a dominance check (one camera is superior on all attributes) to verify basic attentiveness. For each condition, LLM personas first state their ranked decision priorities, then choose between two competing products. We run 30 sessions per persona per condition to capture the distribution of behavior rather than single outputs.

We evaluate two leading commercial LLMs — GPT-4o and Claude 3.5 Sonnet — both sampled at temperature 1.0 to ensure meaningful variation across generations. Persona system prompts describe each persona's **experience and behavior** (e.g., the expert owns multiple cameras, shoots in varied conditions, and edits photos in post-processing software) without explicitly stating what the persona should value, so that the priority ranking emerges from the persona's inferred expertise rather than from prompt-following. We additionally include a **no-persona baseline** condition (identical evaluation prompts without any expert/novice system prompt) to isolate the effect of persona framing from the LLM's default decision behavior.

To evaluate whether LLM personas reflect real human decision patterns, we run an identical study with **30 recruited human participants** (15 experts screened as individuals who own 3+ cameras, have purchased camera gear in the last 2 years, and can explain technical concepts like aperture and ISO; and 15 novices screened as individuals who primarily use phone cameras and have never purchased a dedicated camera), drawn from university photography communities and online photography forums. Both groups complete the same product evaluation tasks in the same format, allowing direct comparison of decision consistency across humans and simulated users.

We evaluate persona behavior using three metrics:

1. **Value–Choice Alignment (per-pair):** For each non-dominance pair, the two differing attributes define a forced tradeoff. We check whether the persona's relative ranking of those two attributes correctly predicts which camera was chosen. Overall alignment equals the fraction of pairs where the choice matches the prediction. This metric does not assume the global top priority drives every decision — it tests whether the persona's own pairwise preference ordering is internally consistent.

2. **Consistency Degradation under Feature Complexity:** Measures the change in value–choice alignment as product attributes increase from 3 to 6 to 11. The metric captures the slope of alignment across complexity levels, indicating how well evaluators maintain coherent decision-making as the number of product attributes (and thus potential distractors) increases.

3. **Human–LLM Persona Gap:** Measures the absolute difference in mean value–choice alignment between LLM personas and matched human participants at each complexity level, reported with 95% confidence intervals and Cohen's d effect size. A smaller gap indicates that the persona more closely mirrors real human decision patterns.

We analyze results using **mixed-effects logistic regression** with persona type (expert vs. novice), complexity level (simple, moderate, complex), and their interaction as fixed effects, and participant/session as random intercepts, to account for the repeated-measures structure (multiple choices nested within sessions).

To summarize, this study addresses two research questions:

1. Do expert LLM personas show higher value–choice alignment than novice personas, and does the expert–novice gap resemble the gap observed between real human experts and novices?

2. Does value–choice alignment degrade as product descriptions become more complex, and do expert personas maintain stronger alignment under increasing feature complexity, similar to real human experts?
