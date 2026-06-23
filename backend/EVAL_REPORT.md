# RosaBot Evaluation Report

How I measured whether RosaBot actually works — and improved its accuracy from
**44% to 81%** by building an evaluation suite, finding real failures, and fixing
them.

---

## Why evaluate at all?

Anyone can build a chatbot and show a few cherry-picked good answers. The harder,
more honest question is: *how often is it actually right, and where does it fail?*
For a tool that answers staff questions about allergens and menu items in a real
restaurant, "it seemed fine when I tried it" is not good enough. A wrong allergen
answer has real consequences.

So I built an automated evaluation suite that runs a fixed set of real questions
through RosaBot, grades each answer against known-correct facts, and produces a
score I can track over time.

## Method

**Dataset.** 16 test cases drawn from real questions staff and guests actually ask,
spanning seven categories: ingredient lookups, allergen safety, dietary filters,
recommendations, special requests, menu listings, and out-of-menu ("do you have
pizza?") hallucination traps. Each case defines the *key facts* a correct answer
must contain and *must-not* rules it has to obey (e.g. never declare a dish
definitively allergen-safe; never invent a menu item).

**Grading.** Each answer is scored by an LLM-judge (GPT-4o-mini, temperature 0)
given the question, RosaBot's answer, the grading criteria, and the complete real
menu so it can distinguish real items from invented ones. The judge returns a
pass/fail plus whether any must-not rule was violated (the hallucination/safety
signal).

**Tracing.** Every run is logged to LangSmith, capturing per-query latency, token
cost, and the full tool-call trace, so performance and cost are observable, not
guessed.

![LangSmith trace view of an evaluation run](docs/images/langsmith-eval-run.png)

*Every eval run is traced in LangSmith. Each question produces two runs: the
`LangGraph` run is RosaBot answering; the `ChatOpenAI` run is the LLM-judge grading
it. The view captures per-call latency, token count, and cost. Note that the slow
calls (6-12s) are the multi-item recommendation queries — the telemetry makes the
latency cost-center visible at a glance.*

**Reproducibility.** The whole suite runs with one command (`python -m eval.run_eval`)
and writes a JSON record of every question, answer, and verdict.

## Baseline result: 44%

The first run scored **44% accuracy** (7/16), with these category scores:

| Category | Baseline |
|----------|----------|
| out_of_menu | 100% |
| allergen | 50% |
| dietary | 50% |
| ingredient | 40% |
| recommendation | 0% |
| listing | 0% |
| special_request | 0% |

A low baseline was *useful* — it gave me concrete, specific failures to chase
rather than a vague sense that "it mostly works."

## What was actually failing

Investigating the failures, they fell into three distinct buckets:

**1. Missing data (real product bug).** "What are your desserts?" returned *"I
couldn't find any desserts."* The desserts (Gulab Jamun, Tiramisu, Glace à la
Pistache, Crème Brûlée à la Cardamome) existed only in a separate allergen-reference
file, not in the searchable menu data — so from RosaBot's perspective they didn't
exist. Same root cause for "what's in the Gulab Jamun?".

**2. A miscalibrated grader (measurement bug, not a RosaBot bug).** Several
"failures" were the judge itself being wrong: it flagged real cocktails (Pisco Sour,
Mezcaloni, etc.) as "invented" because it had no access to the actual menu and was
guessing. An evaluation you can't trust is worse than no evaluation, so this had to
be fixed before the score meant anything.

**3. A real comprehension miss.** Asked "does *Mademoiselle Rosa* contain litchi?",
RosaBot answered about a *different* drink (Litchi Martini) — pattern-matching the
ingredient name instead of looking up the named item.

## What I fixed

- **Added the missing menu data.** A `desserts` section was added to the menu, with
  real ingredients. Because the data layer loads every menu section automatically,
  the fix required zero code changes — the items became searchable immediately.
- **Gave the grader the real menu.** The judge now receives the complete list of
  real menu items, so it can correctly distinguish real dishes from invented ones.
  This removed the false "hallucination" flags and made the score trustworthy.
- **Tightened the system prompt** so the agent looks up a *named* item directly
  rather than pattern-matching on an ingredient word.

## Final result: 81%

After the fixes, accuracy rose to **81% (13/16)** — a **+37 point improvement** over
baseline. Average latency was ~5s per query; full cost and trace data is in LangSmith.

| Category | Baseline | Final |
|----------|----------|-------|
| out_of_menu | 100% | 100% |
| ingredient | 40% | 80% |
| allergen | 50% | 100% |
| listing | 0% | 100% |
| recommendation | 0% | 50% |
| special_request | 0% | 100% |
| dietary | 50% | 50% |

The biggest gains were exactly where the real bugs lived: ingredient lookups,
listings, and allergen accuracy (now 100%).

## What the eval caught that I'd otherwise have shipped

The most valuable outcome wasn't the score — it was a **real dietary-safety bug the
eval surfaced**: RosaBot listed *Dal Makhani* (which contains dairy/butter) as a
vegan option. That is exactly the kind of quietly-wrong answer that manual testing
misses and that matters in a real restaurant. It's logged as a known issue to fix in
the next iteration, alongside extending the grader's menu coverage for a few drink
categories it still under-recognizes.

## Honest limitations

- 16 cases is a starting suite, not exhaustive; the plan is to grow it toward 50+
  with more adversarial edge cases.
- The LLM-judge is itself fallible — a few remaining "failures" are the judge
  under-recognizing real items, not RosaBot errors, so true accuracy is likely a few
  points higher than the reported 81%.
- "Correctness" for dietary queries is scored on safe *exclusion* of unsafe items
  rather than exhaustive listing, which is the property that actually matters for
  safety.

## Why this matters

The point of this exercise was to be able to say something most projects can't:
*here is how often my system is right, here is how I measured it, here is a bug the
measurement caught, and here is the number before and after I fixed it.* That loop —
measure, find failures, fix, re-measure — is the difference between a demo and a
system.