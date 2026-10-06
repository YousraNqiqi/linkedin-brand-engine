"""Pattern 2 - ReWOO ("Reasoning WithOut Observation"): market research.

Plain English: write the WHOLE to-do list first, do every task at the same time,
then combine the results. No slow "ask one thing, wait, think, ask the next".

Three roles:
  1. PLANNER  - decides the research questions (the to-do list)
  2. WORKERS  - one per question, all running at the same time
  3. SOLVER   - combines everything into one brief

IMPORTANT HONESTY NOTE: these workers use Claude's built-in knowledge. They do NOT
browse the live web, so "trends" may be out of date. Later we can give them a web
search tool. An FDE must tell the customer this limit out loud.
"""
from agents import Agent, parallel_map, parse_json_list

# ---- 1. The planner --------------------------------------------------------
planner = Agent(
    "research_planner",
    "You plan market research for LinkedIn marketing. Given a customer profile (ICP) "
    "and an offer, write exactly 3 research tasks that can be done INDEPENDENTLY of "
    "each other: (1) industry trends and what topics get LinkedIn engagement, "
    "(2) the audience's deepest pains, (3) competitor content gaps. "
    'Reply with ONLY JSON: [{"name": "...", "question": "..."}, ...]',
)

# Safety net: if the planner's answer is not valid JSON, use this plan instead.
# FDE habit #4: never trust AI output to be perfectly formatted. Always have a fallback.
DEFAULT_PLAN = [
    {"name": "trends", "question": "What are the top 3 trends and which topics get the most LinkedIn engagement for this audience?"},
    {"name": "pains", "question": "What are this audience's deepest pains: urgency, emotional cost, business cost?"},
    {"name": "competitor_gaps", "question": "What content angles are overused by competitors, what gaps exist, what formats get engagement?"},
]


def parse_plan(text: str) -> list[dict]:
    """Turn the planner's text into a Python list. Fall back to DEFAULT_PLAN on any problem."""
    plan = parse_json_list(text)
    if plan and 1 <= len(plan) <= 5 and all(isinstance(t, dict) and "name" in t and "question" in t for t in plan):
        return plan
    print("  ! planner reply was not valid JSON -> using default plan")
    return DEFAULT_PLAN


# ---- 2. The workers --------------------------------------------------------
def make_worker(task: dict) -> Agent:
    return Agent(
        f"worker_{task['name']}",
        "You are a LinkedIn market researcher. Answer ONLY the question you are given. "
        "Be specific and concrete, max 150 words. If you are unsure of a fact, say so "
        "instead of inventing numbers.",
    )


# ---- 3. The solver ---------------------------------------------------------
solver = Agent(
    "research_solver",
    "You combine three research reports into one brief for a B2B founder. Output: "
    "1) Top 3 positioning angles, 2) What NOT to post, 3) Three quick wins for this week. "
    "Only use facts from the reports. Max 250 words.",
)


def run_research(icp: str, offer: str) -> str:
    context = f"Offer: {offer}\n\nIdeal customer profile:\n{icp}"

    # STEP 1 - plan everything up front.
    plan = parse_plan(planner.run(context))
    print(f"  Plan: {[t['name'] for t in plan]}")

    # STEP 2 - all workers run at the same time.
    def do_task(task: dict) -> tuple[str, str]:
        answer = make_worker(task).run(f"{context}\n\nYour question: {task['question']}")
        return task["name"], answer

    results = parallel_map(do_task, plan)

    # STEP 3 - the solver combines.
    combined = "\n\n".join(f"### {name}\n{text}" for name, text in results)
    return solver.run(f"{context}\n\nThe research reports:\n{combined}")
