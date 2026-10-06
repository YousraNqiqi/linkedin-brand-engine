"""Pattern 1 - Self-consistency: define your Ideal Customer Profile (ICP).

Idea from the video: one agent = one perspective = one bias.
So we ask THREE analysts, each looking from a different angle, who never see
each other's work. Then a 4th agent keeps only what they AGREE on.

Video (Google ADK)                  ->  Our plain Python
  LlmAgent                          ->  Agent (a name + instructions)
  ParallelAgent                     ->  ThreadPoolExecutor (run at same time)
  SequentialAgent                   ->  the order of lines in run_icp()
  output_key (shared context)       ->  the dict `reports`
"""
from agents import Agent, parallel_map  # an Agent = a name + instructions (see agents.py)


# ---- The three independent analysts (different angle each) ----------------
business = Agent(
    "business_analyst",
    "You are an Ideal Customer Profile (ICP) specialist focusing on BUSINESS VALUE. "
    "Describe: company size, industries, budget, and what business outcome they buy. "
    "Be specific. Max 150 words.",
)
pain = Agent(
    "pain_analyst",
    "You are an ICP specialist focusing on PAIN POINTS. List the top 3 painful problems "
    "this customer has: urgency, emotional cost, and business cost of NOT solving it. "
    "Max 150 words.",
)
demographic = Agent(
    "demographic_analyst",
    "You are an ICP specialist focusing on DEMOGRAPHICS and PSYCHOGRAPHICS: job title, "
    "seniority, department, behaviour, values, mindset. Max 150 words.",
)

# ---- The 4th agent: finds the consensus ------------------------------------
synthesizer = Agent(
    "consensus_synthesizer",
    "You read three independent ICP analyses. Keep ONLY what at least two agree on - "
    "that is almost certainly true. Output: 1) Final ICP in 5 lines, 2) Where they "
    "disagreed, 3) Who is NOT our ICP.",
)


def run_icp(offer: str, audience_hint: str = "") -> str:
    hint = f"\nThe founder's rough idea of the audience: {audience_hint}" if audience_hint.strip() else ""
    task = f"Our offer: {offer}{hint}\nDefine the ideal customer."

    # STEP 1 - parallel: all three analysts work at the same time, never seeing each other.
    analysts = [business, pain, demographic]
    answers = parallel_map(lambda a: a.run(task), analysts)
    reports = {a.name: ans for a, ans in zip(analysts, answers)}

    # STEP 2 - sequential: the synthesizer reads all three reports.
    combined = "\n\n".join(f"### {name}\n{text}" for name, text in reports.items())
    return synthesizer.run(f"Offer: {offer}\n\nThe three analyses:\n{combined}")
