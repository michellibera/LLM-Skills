# Saaty scale - mapping natural language to numbers

The 1-9 scale is the heart of AHP. Your job: translate between the user's natural language and that scale. The user should never pick a number themselves - you listen and map.

## Base table

| Number | Meaning | User's phrasing |
|--------|---------|-----------------|
| 1 | Equal importance | "equally important", "don't know", "similar", "doesn't matter" |
| 3 | Slight preference | "a bit more important", "slightly", "marginally", "a touch" |
| 5 | Clear preference | "more important", "clearly", "moderately", "definitely" |
| 7 | Strong preference | "much more important", "very", "strongly", "by a lot" |
| 9 | Extreme preference | "absolutely critical", "extremely", "incomparably", "overwhelmingly" |
| 2, 4, 6, 8 | Intermediate values | when the user hesitates between two levels |

## Reciprocal values

If A vs B = 5, then automatically B vs A = 1/5 = 0.2. Never ask the user about the other side of the comparison - it follows mathematically.

## Example questions in natural language

Instead of: "Give a value for A vs B on a 1-9 scale"
Ask: "Which matters more to you - A or B? And by how much: slightly, clearly, significantly, or extremely?"

Other good phrasings:
- "If you had to pick only one - price or location? And is the difference obvious or rather hard?"
- "Imagine option A has a great price and option B has a great location. Which tempts you more?"
- "How much is price a dealbreaker, and how much is location?"

## Ambiguity signals

If the user says:
- "it depends" → ask for context to clarify
- "both matter" → ask which they would sacrifice first if forced
- "don't know" → use 1 (equal importance) - that's a legitimate answer
- "these are completely different things" → warning: criteria may not be comparable, consider reformulating

## What not to do

- Don't push toward 9 if the user says "a bit" - use 3.
- Don't suggest numbers to the user ("Maybe 7?") - it biases their answer.
- Don't explain the scale every time - do it once at the start, then just ask naturally.
