# Manual Experiment Protocol

## Structure

Each **session** = one conversation covering all 15 pairs across all three complexity levels for a single persona:

1. **System prompt** — sets the persona (once per session)
2. **Turn 1** — priority ranking of all 11 attributes (once per session, before seeing any cameras)
3. **Turns 2–6** — 5 simple pairs (3 attributes each, one per turn)
4. **Turns 7–11** — 5 moderate pairs (6 attributes each, one per turn)
5. **Turns 12–16** — 5 complex pairs (11 attributes each, one per turn)

Total sessions: **2 personas = 2 sessions per run**.
Repeat N times (e.g., 30 runs = 60 sessions total) for statistical power.

The priority ranking from Turn 1 covers all 11 attributes and is shared across all 15 pairs in that session. Because each pair shows a different attribute subset (3, 6, or 11 attributes), the same ranking is used to evaluate all of them — the complexity level controls how many attributes are visible per pair, not which attributes are ranked.

> **Note:** Because all 15 pairs share one conversation, earlier pairs may influence later ones (order effects). Keep pair order fixed and complexity order fixed (simple → moderate → complex) across all sessions so any order effects are consistent and controllable.

---

## Step 1 — Set the System Prompt

Paste this as the **system prompt** before starting each session.

### Expert persona

```
You are an experienced photographer with over 10 years of shooting experience. You own three cameras: a full-frame DSLR, a mirrorless system camera, and a compact travel camera. You have purchased camera gear multiple times in the past two years and actively follow photography communities and review sites.

You understand technical concepts like aperture, ISO, shutter speed, depth of field, RAW format, burst shooting speed, weather sealing, and lens ecosystems. You shoot in a variety of conditions including low light, outdoor events, and studio settings. You edit your photos in post-processing software and have published work in online galleries and local exhibitions.
```

### Novice persona

```
You are a casual photographer who primarily uses your smartphone camera. You have never owned a dedicated camera and have no experience evaluating camera specifications. You take photos at family events, vacations, and social gatherings.

You do not know technical photography terms like aperture, ISO, shutter speed, RAW format, or burst speed. You have never read a camera review or visited a photography forum. When friends discuss camera gear, the conversation feels overwhelming and unfamiliar. You have occasionally thought about buying a dedicated camera as a gift or for a trip but have never followed through.
```

---

## Step 2 — Turn 1: Priority Ranking

Send this as the **first user message** of the session, before showing any cameras. The attribute list is always the full set of 11 attributes, regardless of complexity level.

```
You are considering purchasing a new digital camera. Before seeing any specific products, please rank the following camera attributes from most to least important based on YOUR personal priorities.

The attributes are:
  - price_usd: Price in US dollars
  - image_quality_score: Image quality on a scale of 1-10 as rated by independent reviewers
  - battery_life_hours: Battery life in hours of continuous shooting
  - optical_zoom_x: Optical zoom level (e.g., 10x means 10 times optical magnification)
  - weight_grams: Camera weight in grams (body only)
  - ease_of_use_score: Ease of use on a scale of 1-10 based on user testing with first-time camera buyers
  - has_manual_controls: Whether the camera has full manual controls (aperture, shutter speed, ISO) — Yes or No
  - raw_format_support: Whether the camera can save photos in RAW format for post-processing — Yes or No
  - burst_speed_fps: Continuous burst shooting speed in frames per second
  - weather_sealed: Whether the camera body is sealed against dust and moisture — Yes or No
  - video_resolution_4k: Whether the camera can record video in 4K resolution — Yes or No

Return your ranking as a numbered list, with one attribute name per line, from most important (1) to least important. Use the exact attribute names as shown above (the part before the colon).

Example format:
1. attribute_name 
2. attribute_name
3. attribute_name

Your ranked list:
```

---

## Steps 3–17 — Turns 2–16: Camera Pairs (one per turn)

After receiving the priority ranking, present all 15 pairs one at a time in order: 5 simple pairs (Turns 2–6), then 5 moderate pairs (Turns 7–11), then 5 complex pairs (Turns 12–16). Replace `[CAMERA A SPECS]` and `[CAMERA B SPECS]` with the attributes listed in each pair's `pair_attributes` field.

```
Based on your priority ranking above, evaluate this next pair of cameras.

Camera A:
[CAMERA A SPECS]

Camera B:
[CAMERA B SPECS]

Which camera do you choose? Reply in exactly this format:

Choice: [camera name]
Decisive attribute: [attribute name]

Use the exact camera name and the exact attribute name from your ranking above.
```

The **decisive attribute** is the single attribute that most influenced the final decision for this pair. Recording it alongside the choice lets you compare:
- What the persona *said* mattered most (priority rank #1 from Turn 1)
- What *actually* drove each individual decision (decisive attribute per pair)

A mismatch between the two is itself a finding.

### Formatting camera specs

Pull values directly from the stimulus JSON and format as follows:

```
Camera A:
  Veloxa X1
    - Price in US dollars: 299
    - Image quality on a scale of 1-10 as rated by independent reviewers: 9
    - Battery life in hours of continuous shooting: 20

Camera B:
  Strikon Z3
    - Price in US dollars: 499
    - Image quality on a scale of 1-10 as rated by independent reviewers: 7
    - Battery life in hours of continuous shooting: 12
```

Use the full attribute descriptions (not the raw key names) so the persona sees human-readable labels.

