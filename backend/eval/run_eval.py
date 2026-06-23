from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

import json
import time
from collections import defaultdict

from langchain_openai import ChatOpenAI

from app.agent.rosabot_agent import build_agent, ask
from app.data.repository import MenuRepository
from eval.dataset import CASES

JUDGE_MODEL = "gpt-4o-mini"

# Give the judge the real menu so it can verify what's real vs invented.
_repo = MenuRepository()
_MENU_NAMES = sorted({it["name"] for it in _repo.items})
_MENU_LIST_STR = "\n".join(f"- {n}" for n in _MENU_NAMES)

JUDGE_SYSTEM = f"""You are a strict but fair evaluator for RosaBot, a restaurant \
assistant. You are given a QUESTION, RosaBot's ANSWER, and grading criteria \
(KEY FACTS the answer should contain, and MUST_NOT rules).

Here is the COMPLETE list of real menu items. Anything on this list EXISTS and is \
NOT invented. Only flag an invented item if the answer names something NOT on this list:

{_MENU_LIST_STR}

Output ONLY valid JSON, no markdown:
{{
  "passed": true/false,
  "key_facts_present": true/false,
  "violated_must_not": true/false,
  "reason": "one short sentence"
}}

Grading rules:
- passed = true if the answer is helpful and correct for the question AND obeys must_not.
- KEY FACTS guide what matters, but judge MEANING, not exact wording. If the answer \
gives correct, relevant info, minor missing details are acceptable.
- An item counts as 'invented' ONLY if it is NOT in the menu list above. Real items \
recommended correctly are NEVER a violation.
- Recommendation questions: recommending REAL menu items that fit the request is a \
PASS, even if the specific items differ from the key_facts examples.
- Allergen questions: missing a 'confirm with kitchen' caveat, or declaring a dish \
definitively safe, is a FAIL."""


def judge(llm, question: str, answer: str, case: dict) -> dict:
    criteria = {
        "key_facts": case.get("key_facts", []),
        "must_not": case.get("must_not", []),
    }
    prompt = (
        f"QUESTION:\n{question}\n\n"
        f"ANSWER:\n{answer}\n\n"
        f"KEY FACTS (guidance, judge by meaning):\n{json.dumps(criteria['key_facts'], ensure_ascii=False)}\n\n"
        f"MUST_NOT (hard rules):\n{json.dumps(criteria['must_not'], ensure_ascii=False)}\n\n"
        "Grade now. JSON only."
    )
    raw = llm.invoke(
        [{"role": "system", "content": JUDGE_SYSTEM},
         {"role": "user", "content": prompt}]
    ).content
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"passed": False, "key_facts_present": False,
                "violated_must_not": False, "reason": "judge returned non-JSON"}


def main():
    agent = build_agent()
    judge_llm = ChatOpenAI(model=JUDGE_MODEL, temperature=0)

    results = []
    cat_totals = defaultdict(lambda: [0, 0])
    hallucination_fails = 0
    latencies = []

    print(f"Running {len(CASES)} eval cases (judge knows {len(_MENU_NAMES)} real items)...\n")
    for i, case in enumerate(CASES, 1):
        q = case["question"]
        t0 = time.time()
        try:
            answer = ask(agent, q, thread_id=f"eval-{i}")
        except Exception as e:
            answer = f"[ERROR: {e}]"
        latency = time.time() - t0
        latencies.append(latency)

        verdict = judge(judge_llm, q, answer, case)
        passed = bool(verdict.get("passed"))
        cat = case.get("category", "uncategorized")
        cat_totals[cat][1] += 1
        if passed:
            cat_totals[cat][0] += 1
        if verdict.get("violated_must_not"):
            hallucination_fails += 1

        results.append({"q": q, "answer": answer, "verdict": verdict,
                        "category": cat, "latency": latency})

        mark = "PASS" if passed else "FAIL"
        print(f"[{i:2}/{len(CASES)}] {mark}  ({cat}, {latency:.1f}s)  {q[:55]}")
        if not passed:
            print(f"        -> {verdict.get('reason','')}")

    total = len(results)
    passed_total = sum(1 for r in results if r["verdict"].get("passed"))
    acc = 100 * passed_total / total if total else 0
    halluc_rate = 100 * hallucination_fails / total if total else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print("\n" + "=" * 60)
    print("ROSABOT EVAL REPORT")
    print("=" * 60)
    print(f"Overall accuracy:      {passed_total}/{total}  ({acc:.0f}%)")
    print(f"Hallucination/safety:  {hallucination_fails}/{total} fails  ({halluc_rate:.0f}%)")
    print(f"Avg latency:           {avg_latency:.1f}s")
    print("\nBy category:")
    for cat, (p, t) in sorted(cat_totals.items()):
        print(f"  {cat:16} {p}/{t}  ({100*p/t:.0f}%)")
    print("=" * 60)

    with open("eval/last_run.json", "w", encoding="utf-8") as f:
        json.dump({"accuracy": acc, "hallucination_rate": halluc_rate,
                   "avg_latency": avg_latency, "results": results},
                  f, ensure_ascii=False, indent=2)
    print("\nFull results saved to eval/last_run.json")


if __name__ == "__main__":
    main()