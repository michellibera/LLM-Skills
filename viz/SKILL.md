---
name: viz
description: Render the last answer, a topic, or the git diff as a one-screen, self-contained HTML infographic and open it in the browser.
argument-hint: "[topic | diff | #N change]"
disable-model-invocation: true
allowed-tools: Read Glob Edit(./.viz/**) Bash(git diff) Bash(git diff *) Bash(start *) Bash(open *) Bash(xdg-open *) PowerShell(Start-Process *)
---

# /viz: one infographic, one idea

Request: `$ARGUMENTS`

## 1. Subject

- Empty: the main point of your previous answer in this conversation. If there is none yet, say so in one sentence and stop.
- `diff`: run `git diff HEAD --stat` and `git diff HEAD` (plain `git diff` when the repo has no commits). Show what changed and why it matters: files touched, the shape of the change, risks. No changes: say so in one sentence and stop, creating no file.
- `#N …` or a request to change an existing infographic ("the last one", "make it a table"): edit that file; see section 3.
- Anything else: that topic, grounded in this conversation and the code.

## 2. Form

The form follows the content, not habit: pick from this alphabet by the kind of information, never default to prose. Combine several forms when the content has several kinds.

Choose the form with the DSRP lens (Cabrera): meaning is information plus how it is structured, so ask four questions of the subject and let the answers pick the form.

- **D**istinction: what is it, and what is it not? Name the boundary.
- **S**ystem: what are its parts, and what is it a part of?
- **R**elationship: what acts on what, and with what effect?
- **P**erspective: who looks from where, and what changes from another view?

| Form | DSRP | Content | Build with |
|---|---|---|---|
| Thesis | D | definition, conclusion, assumption, short idea | `h1` + `.callout`; say what it is not |
| Flow | R | process, sequence, causality, data flow | `.flow` (`.vertical` for long ones) |
| Relation map | R, S | dependencies, impact, part-whole, systems | inline SVG: nodes, edges typed by style (depends on, impacts, part of) |
| Table / matrix | P, D | comparison, criteria, trade-offs, alternatives | `.table`; columns are perspectives or options |
| Hierarchy | S | decomposition into parts | nested `ul`, or `.grid` of `.card`s |
| Mind map | D, S | gather thoughts: brainstorm, open questions, unsorted ideas | centre `.node.accent`, branches around it (SVG or `.grid`); links unlabeled |
| Concept map | S, R | organize understanding: concepts joined by stated propositions | inline SVG; every edge labeled with a verb phrase ("causes", "requires") |
| System map | S, R | map the system: parts, boundary, flows, feedback loops | inline SVG; boundary box, parts inside, outside actors beyond it, loops marked |
| Mental model | P | what a given person believes about how it works, to understand and communicate it | two `.card`s side by side: their model vs the actual one; gaps as `.tag.warn` |
| Conceptual model | S, R, P | a new way to think about a complex system: a reframing or metaphor | few elements and a name; `.callout` states the reframing in one sentence |
| Source | none | code, file, doc excerpt, input data | `pre` + `.muted` path (`file:line`) |

Pick the map by what the thinking is for: gather → mind map; organize → concept map; map the system → system map; communicate someone's understanding → mental model; offer a new way to think about a complex system → conceptual model. A relation map is the light version: dependencies without stated propositions or system boundary.

- Add facts only when they sharpen the structure. A list of new facts with the same structure teaches less than one changed structure (a new boundary, a regrouping, a hidden relation, another viewpoint).
- When the subject has real trade-offs, show at least two perspectives side by side (for example readability, testability, risk, maintenance, scale) instead of the first two that come to mind.
- No `.card` frame when the content reads fine without one; use it to group parallel items, not to wrap everything.
- Show only the relations the one idea needs; leave the rest out.
- Mark epistemic status where it matters: observed fact, decision, conclusion, hypothesis. Use `.tag` (`.ok` fact, `.warn` hypothesis, `.bad` risk) and keep contradictions visible but quiet.
- Provenance stays subtle: a `.muted` source line under the claim, not a banner.
- Changing the form never changes the meaning: the same idea as a table instead of a flow keeps the same claims.

## 3. File name

In parallel: Glob `.viz/*.html` in `${CLAUDE_PROJECT_DIR}` and Read `${CLAUDE_SKILL_DIR}/assets/template.html`.

Write to `${CLAUDE_PROJECT_DIR}/.viz/NNN-slug.html`: NNN is the highest existing number + 1, zero-padded to 3 digits (the first is `001`); slug is 2-5 lowercase ASCII words joined with `-`.

To change an existing infographic (`#N`, or the latest one when the request refers to it), Read `.viz/NNN-*.html` and Edit it in place: keep its number, name and the template's `<style>` block. A new subject is always a new file.

## 4. HTML contract

- Start from `template.html`: replace `{{lang}}` with the conversation's language code, `{{title}}` with a short title, `{{body}}` with the content. Keep its `<style>` block verbatim: every file carries all its styles, so it opens straight from disk, needs no server and no other file. Extra rules go in a second `<style>` after it, never by changing the template's.
- Nothing external: no CDN, libraries, web fonts, remote images or network calls; the infographic must work offline. Inline `<script>` is fine; no `<link>` stylesheets.
- Diagrams from flexbox, grid and inline SVG.
- One main idea that fits about one screen (~1000×700 px). All text in the language of this conversation.
- Light and dark themes come from the template's `<style>` via `prefers-color-scheme`. Give every custom color (CSS or SVG `style="fill:…"`) as a variable, never a literal: `--bg --surface --fg --muted --line --accent --ok --warn --bad`, each color also with a `-soft` tint (e.g. `--accent-soft`).
- No `vh`/`vw` heights: let the content set the height.

Classes in the template's `<style>`:

| Class | Use |
|---|---|
| `.card` | Bordered box; put several in a `.grid` |
| `.flow` | Row of `.node` and `.arrow`; `.flow.vertical` stacks top to bottom |
| `.node` | Box in a flow; `<small>` for a sub-label; variants `.accent` `.ok` `.warn` `.bad` |
| `.arrow` | Connector between nodes; its text is the edge label |
| `.table` | Data table; `td.num` right-aligns numbers |
| `.callout` | The key takeaway; variants `.ok` `.warn` `.bad` |
| `.tag` | Small pill label; same variants |
| `.muted` | Secondary text |

`{{body}}` example:

```html
<h1>Auth flow</h1>
<p class="muted">One sentence of context.</p>
<div class="flow">
  <div class="node">Browser</div>
  <div class="arrow">POST /login</div>
  <div class="node accent">API<small>issues JWT</small></div>
  <div class="arrow">verify</div>
  <div class="node">DB</div>
</div>
<div class="callout">The one thing to remember.</div>
```

## 5. Open and reply

When the file is finished, open it in the default browser by its absolute path: on Windows `Start-Process "<path>"` in PowerShell or `start "" "<path>"` in Bash, `open <path>` on macOS, `xdg-open <path>` on Linux. If that fails, skip it.

Don't open it again when it is already open: you opened this same file earlier in this conversation (typically when editing `#N`), or the user says it is open. Then tell the user to refresh the page instead.

Reply with exactly one sentence in the conversation's language: `Done: #N <title> — <path>`, plus a short refresh note when the page was already open, e.g. `Done: #3 Auth flow — /home/me/app/.viz/003-auth-flow.html` (in Polish: `Gotowe: #3 Przepływ autoryzacji — …`).
