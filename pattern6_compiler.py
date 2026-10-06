"""Pattern 6 - LLM Compiler: a boss decides WHICH tasks to run, specialists run together.

Plain English: a newsroom editor reads a story idea and assigns people - article,
headlines, hashtags, timing. They all work at once. Another editor assembles the page.

Difference from a plain parallel step (pattern 2): there the tasks were always the same.
Here the compiler chooses the tasks, based on the request.
"""
from agents import Agent, parallel_map, parse_json_list

# The menu of specialists the compiler can pick from.
TOOLS = {
    "post_writer": Agent(
        "post_writer",
        "You write ONE complete LinkedIn post (max 200 words) for a B2B founder. Short "
        "paragraphs, concrete, no fluff, one soft call to action. Never invent statistics or "
        "customers; use [ADD REAL EXAMPLE] where proof is needed."),
    "hook_analyzer": Agent(
        "hook_analyzer",
        "You write 3 alternative opening lines (hooks) for a LinkedIn post, score each 1-10 for "
        "scroll-stopping power, and recommend the best one in a sentence."),
    "hashtag_researcher": Agent(
        "hashtag_researcher",
        "You suggest 3-5 LinkedIn hashtags for a post: mix of niche and broader. One line "
        "each on why."),
    "timing_advisor": Agent(
        "timing_advisor",
        "You advise the best day and time to post for this audience, plus one idea for a "
        "first comment. State clearly that timing advice is a hypothesis to test, not a fact."),
}

compiler = Agent(
    "content_compiler",
    "You are a task compiler. Given a post request, decide which specialists are needed from: "
    f"{', '.join(TOOLS)}. post_writer is always required. Skip specialists the request does "
    'not need. Reply with ONLY JSON: [{"tool": "<name>", "instruction": "<specific task>"}]',
)

aggregator = Agent(
    "content_aggregator",
    "You assemble specialist outputs into one ready-to-review package: 1) FINAL POST (with the "
    "recommended hook on top), 2) alternative hooks, 3) hashtags, 4) posting advice, "
    "5) a 'verify before posting' note listing any placeholders or claims to check.",
)


def compile_plan(raw: str) -> list[dict]:
    """Validate the compiler's JSON. Unknown tools are dropped; post_writer is guaranteed."""
    plan = parse_json_list(raw) or []
    plan = [t for t in plan if isinstance(t, dict) and t.get("tool") in TOOLS]
    if not any(t["tool"] == "post_writer" for t in plan):
        print("  ! compiler plan unusable -> using all specialists")
        plan = [{"tool": name, "instruction": "Do your job for this post."} for name in TOOLS]
    return plan


def run_compiler(topic: str, icp: str, tone: str = "practical, data-aware, no fluff") -> str:
    request = f"Post topic: {topic}\nTone: {tone}\nIdeal customer:\n{icp}"

    # STEP 1 - the compiler decides the task graph.
    plan = compile_plan(compiler.run(request))
    print(f"  Compiled tasks: {[t['tool'] for t in plan]}")

    # STEP 2 - chosen specialists run at the same time.
    def do(task: dict) -> tuple[str, str]:
        out = TOOLS[task["tool"]].run(f"{request}\n\nYour task: {task['instruction']}")
        return task["tool"], out

    results = parallel_map(do, plan)

    # STEP 3 - assemble.
    combined = "\n\n".join(f"### {name}\n{text}" for name, text in results)
    return aggregator.run(f"{request}\n\nSpecialist outputs:\n{combined}", max_tokens=2000)
