# Example AHP walkthrough - choosing a laptop

This document shows the full AHP conversation from start to finish. Read it if you get lost in the workflow or want to see how to guide the user naturally.

## Context

User: "Help me pick a laptop. I have 3 models in mind but can't decide."

## Step 1: Goal

> **Assistant:** Sure, I'll help you structure this decision using AHP - which means we'll break the choice into factors step by step, compare them, and at the end you'll see a ranking. Don't worry - I'll do all the math in the background.
>
> Let's start with the basics - state the goal in one sentence. What should this laptop be for you? "Work laptop", "gaming", "studying"?

> **User:** Remote work, lots of Python programming, occasional gaming in the evening.

→ Goal: "Laptop for remote work (programming) with occasional gaming"

## Step 2: Alternatives

> **Assistant:** Great. Which 3 models are you considering?

> **User:** MacBook Pro M3, Dell XPS 15, ThinkPad X1 Carbon.

→ Alternatives: [MBP M3, Dell XPS 15, ThinkPad X1]

## Step 3: Criteria

> **Assistant:** What matters most to you when choosing? List what comes to mind - price, performance, looks, anything.

> **User:** Price, performance for programming, screen quality, mobility (I commute a lot), battery life.

→ Criteria: [Price, Performance, Screen, Mobility, Battery]
*5 criteria = 10 pairwise comparisons. OK, doable.*

## Step 4: Pairwise comparisons of criteria

> **Assistant:** Now the trickiest part - we'll compare these criteria against each other. I'll ask 10 simple questions of the form "which matters more to you, A or B?". Don't overthink - intuition is fine here.
>
> First: **price vs performance** - which matters more to you when picking a laptop? And by how much - slightly, clearly, significantly, or completely?

> **User:** Performance, but only slightly - price hurts too.

→ A_12 = 1/3 (performance slightly more important than price)

> **Assistant:** OK. **Price vs screen quality**?

> **User:** Price. Clearly.

→ A_13 = 5

*...continue until you have all 10 comparisons...*

Final matrix (5x5):
```
              Price  Perf   Screen  Mobil  Battery
Price          1    1/3    5       3      4
Performance    3     1     5       3      3
Screen        1/5  1/5     1      1/3    1/2
Mobility      1/3  1/3     3       1      2
Battery       1/4  1/3     2      1/2     1
```

## Step 5: Consistency check

You run `compute_priorities(matrix)`:
- Weights: [Price 0.27, Performance 0.40, Screen 0.05, Mobility 0.16, Battery 0.12]
- CR = 0.04 ✅ (below 0.10, consistent)

> **Assistant:** Your comparisons are consistent. The criteria weights came out as:
> - Performance: 40%
> - Price: 27%
> - Mobility: 16%
> - Battery: 12%
> - Screen: 5%
>
> Does this match your intuition?

→ If the user agrees, we move on. If not - that's a sign they may have answered inconsistently, so we revisit.

## Step 6: Alternative comparisons per criterion

### Price - we have concrete numbers!

> **Assistant:** Do you know exactly what these models cost?

> **User:** MBP - 2400, Dell - 1800, ThinkPad - 2200.

→ Use `normalize_hard_data([2400, 1800, 2200], benefit=False)` (cost)
→ Price weights: MBP 0.272, Dell 0.362, ThinkPad 0.296 (Dell wins - cheapest)

### Performance - subjective

> **Assistant:** On performance for programming - which is the best? Let's compare them in pairs.
> **MBP M3 vs Dell XPS 15** - which is more powerful?

→ Collect 3 comparisons (MBP-Dell, MBP-ThinkPad, Dell-ThinkPad).

### Screen, mobility, battery - analogously

→ Battery - hard data again (battery hours).
→ Mobility - weight + thickness, hard data again.
→ Screen - subjective.

## Step 7: Synthesis and presentation

You run `aggregate(crit_weights, [m_price, m_perf, m_screen, m_mobil, m_battery])`.

Result (example):
- MacBook Pro M3: 0.395
- ThinkPad X1: 0.328
- Dell XPS 15: 0.277

> **Assistant:** We have a result! 🏆
>
> 1. **MacBook Pro M3** - 39.5%
> 2. ThinkPad X1 Carbon - 32.8%
> 3. Dell XPS 15 - 27.7%
>
> The MacBook won mainly thanks to performance (which has a 40% weight for you) and battery. The ThinkPad came close on mobility. Dell won on price, but screen and performance dragged it down.
>
> For comparison - if price were about 15 percentage points more important to you, Dell would jump to first place. So the gap between the MacBook and Dell isn't "crushing" - more "clear but debatable".
>
> Does this result feel right to you? Sometimes the AHP outcome reveals that our stated priorities don't match what we actually want.

## Summary - lessons from this example

1. **Natural language.** Nowhere did the words "matrix" or numbers from the Saaty scale appear.
2. **Adapt to data type.** Price and battery - hard data. Performance and screen - pairwise comparisons.
3. **Check consistency.** After a critical step, pause, check CR, and ask the user "does this match?".
4. **Explain the winner.** Don't just give a number - say **why** the winner won.
5. **Sensitivity analysis.** Show how "stable" the decision is.
