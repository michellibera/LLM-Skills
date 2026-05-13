---
name: ahp-decision
description: Helps the user make a complex decision using the Analytic Hierarchy Process (AHP) by Saaty. Use this skill whenever the user faces a choice among several options with multiple criteria and needs a structured, quantitative method to decide - for example choosing a car, job offer, apartment, vendor, technology, university program, or business strategy. Also trigger on phrases like "help me decide", "I don't know what to choose", "compare these for me", "which option is best", "AHP", "multi-criteria decision analysis", "MCDA", even if the user doesn't know the AHP method by name.
---

# AHP Decision Helper

A skill that guides the user through the full Analytic Hierarchy Process (AHP) workflow by Thomas Saaty. The method converts subjective preferences into a quantitative ranking of options via pairwise comparisons of criteria and alternatives.

## When to use this skill

Use it whenever the user's decision meets these conditions:
- there are **at least 2 alternatives** to choose from,
- there are **at least 2 evaluation criteria**,
- the criteria are in some way **conflicting** (better on one means worse on another),
- the user wants a **structured, rational** approach rather than just intuition.

If the decision is trivial (one dominant criterion) or the user clearly only wants a casual chat - offer a simpler conversation instead of full AHP.

## Operating philosophy

AHP can feel overwhelming (many comparisons, matrices, the 1-9 scale). Your job as the agent is to **hide the mathematical complexity** behind a friendly conversation. The user should not see matrices - they should be answering questions like "which matters more to you, price or location?".

All calculations (eigenvectors, Consistency Ratio CR, aggregation of results) are done in the background using the `scripts/ahp_solver.py` script.

## Main workflow

Follow these 7 steps. **Do not skip any step** - each has a methodological purpose.

### Step 1: Define the goal

Ask the user in one sentence what decision they are making. Save it as `goal`.

> Example: "Choosing a laptop for remote work and occasional gaming"

### Step 2: Identify alternatives

Help the user list concrete, comparable options. If they only have a vague idea ("some good laptop"), help narrow it down to 2-7 specific models/options. Above 7 options the process becomes exhausting - suggest a preliminary shortlist.

### Step 3: Identify criteria

Ask what matters to them in this decision. Extract 3-7 criteria. If the user lists many - group them hierarchically (main criteria and sub-criteria) and say you'll start with the main ones. If they list too few - suggest typical criteria for that decision category.

**Important:** Criteria should be **independent** (uncorrelated). If the user mentions "price" and "value for money" - point out that these overlap.

### Step 4: Pairwise comparisons of criteria

This is the crucial moment. The user compares **every pair** of criteria using the Saaty scale (see `references/saaty_scale.md`). For N criteria you have N(N-1)/2 comparisons.

**How to conduct comparisons**: don't show numbers upfront. Ask in natural language and map to a number yourself:

> "Which matters more to you when choosing a laptop: **price** or **performance**? And by how much - slightly, moderately, significantly, very strongly, or extremely?"

Mapping user responses → Saaty scale:
- "equally important / don't know" → 1
- "slightly more important" → 3
- "moderately / clearly more important" → 5
- "significantly / strongly more important" → 7
- "extremely / overwhelmingly more important" → 9
- (values 2, 4, 6, 8 are intermediate - use them when the user hesitates)

Collect the answers into an NxN matrix (if A vs B = 5, then B vs A = 1/5).

### Step 5: Consistency check (Consistency Ratio)

After collecting the comparisons, **run the script** `scripts/ahp_solver.py` with the criteria matrix. The script will return:
- a vector of weights (priorities),
- the Consistency Ratio (CR).

**Saaty's rule:** CR should be ≤ 0.10. If CR > 0.10:
- show the user that their comparisons are inconsistent,
- point out the **most inconsistent pair** (the script will find it),
- suggest revising that specific comparison,
- repeat until CR ≤ 0.10 or the user consciously accepts a higher CR.

Never hide poor consistency. Inconsistent weights = worthless result.

### Step 6: Pairwise comparisons of alternatives (per criterion)

**This is where most of the work happens.** For each criterion the user compares every pair of alternatives. For M alternatives and N criteria that's N × M(M-1)/2 comparisons.

**Optimization - hard vs soft data:**
- If a criterion has an **objective numeric value** (e.g. price, weight, battery life hours, salary), ask for the concrete values and automatically convert them to weights (see `references/converting_data.md`). Don't bore the user with pairwise comparisons in this case.
- If a criterion is **subjective** (e.g. "design", "company culture", "brand reputation"), use pairwise comparisons on the Saaty scale.

After each criterion, check CR again.

### Step 7: Synthesis and presentation

The `ahp_solver.py` script performs the final aggregation: for each alternative it computes the weighted sum of its weights across all criteria.

**Presenting the result** (this matters - it's the payoff for all the effort):
1. **Ranking** of alternatives from best to worst with concrete percentage scores.
2. **Chart** - use the `chart_display_v0` tool (bar chart) for visualization if available.
3. **Interpretation**: explain **why** the winner won - which criteria turned out to be decisive, where a particular alternative had an edge.
4. **Sensitivity analysis**: show how much the criteria weights would need to shift for the winner to change. If the difference is small (e.g. < 5 percentage points), say it openly - the decision is "close", the user may follow intuition.
5. **Reflection phase**: ask "does this result feel right?". If the user says "no", that's valuable information - they may have unconsciously omitted some criterion. Go back to step 3.

## What to keep, what to discard

**Keep as conversation state:**
- the list of criteria,
- the list of alternatives,
- the comparison matrices (criteria matrix + one matrix per criterion for the alternatives),
- the current CR values.

Simplest approach: keep everything as Python structures in the script and save snapshots to `/home/claude/ahp_state.json` after each step, so you can backtrack if something needs revising.

## Pitfalls to avoid

1. **Don't invent comparisons for the user.** If they don't know, ask again, give context, but don't add numbers "just to fill in".
2. **Don't hide a high CR.** Inconsistency is a signal, not an error - the user may be discovering that their intuitions are contradictory, and that's valuable.
3. **Don't show raw matrices** in your response to the user unless they ask. Show only interpretation.
4. **Don't promise that AHP gives an "objective" answer.** AHP structures subjective preferences but does not invalidate them.
5. **Don't run full AHP for 2 alternatives and 2 criteria** - that's overkill. Suggest a simpler pros/cons table.

## Helper files

- `scripts/ahp_solver.py` - calculations (eigenvector, CR, finding the most inconsistent pair, final aggregation). **Always use this script** instead of computing things "by hand".
- `references/saaty_scale.md` - the full Saaty scale with examples of natural-language phrasing.
- `references/converting_data.md` - how to convert hard data (prices, times) into AHP weights, including inverse criteria (less is better).
- `references/example_walkthrough.md` - a complete decision example (choosing a laptop) from start to finish - read it if you get lost in the workflow.

## Final report format

When finished, offer the user to save the outcome as a Markdown file at `/mnt/user-data/outputs/ahp_decision.md` containing: goal, criteria with weights, alternatives with scores, ranking, brief justification, date. This is valuable - decisions sometimes need to be justified to others (a spouse, a boss, your future self).
