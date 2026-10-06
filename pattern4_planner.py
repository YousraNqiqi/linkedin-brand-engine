"""Pattern 4 - Adaptive planner: plan -> do one week -> check -> adjust -> next week.

Plain English: a GPS. It plans the route, but recalculates when conditions change.
Difference from ReWOO (pattern 2): there the plan never changed. Here it evolves.

Loop (4 weeks):
   executor writes week N  ->  observer checks "is the plan still right?"  ->
   its suggested changes are handed to the executor for week N+1.
"""
from agents import Agent

planner = Agent(
    "content_planner",
    "You build a 30-day LinkedIn content plan for a B2B founder: 4 weeks, 3 posts per week. "
    "For each post give: topic, hook idea, format. Mix: ~60% educational, 20% storytelling, "
    "20% engagement with soft calls to action. Tie every post to the ideal customer's pains.",
)

executor = Agent(
    "week_writer",
    "You write ONE week of LinkedIn posts from a content plan. For each of the 3 posts: the "
    "hook, a short draft body (max 120 words), and a soft call to action. Apply any "
    "adaptive changes provided. Never invent statistics or customers; mark any needed "
    "proof as [ADD REAL EXAMPLE].",
)

observer = Agent(
    "trend_observer",
    "You check whether a content plan still makes sense after a week of content was written. "
    "Are the remaining topics still relevant? Is there a better angle? Any emerging topic? "
    "Reply 'NO CHANGES' if the plan is fine, otherwise a short list of specific changes "
    "for the remaining weeks.",
)


def run_planner(icp: str, research: str, goal: str, weeks: int = 4, style: str = ""):
    context = f"Ideal customer:\n{icp}\n\nResearch brief:\n{research}\n\nGoal: {goal}\nStyle: {style}"
    plan = planner.run(context, max_tokens=2500)

    changes = "None yet (first week)."
    week_texts, change_log = [], []
    for week in range(1, weeks + 1):
        print(f"  Week {week}/{weeks}")
        content = executor.run(
            f"{context}\n\nFull plan:\n{plan}\n\nAdaptive changes so far:\n{changes}\n\n"
            f"Write week {week} now.", max_tokens=2500)
        week_texts.append(f"## Week {week}\n{content}")
        if week < weeks:  # nothing left to adapt after the last week
            changes = observer.run(
                f"Plan:\n{plan}\n\nWeek {week} content:\n{content}\n\n"
                f"Remaining weeks: {weeks - week}")
            change_log.append(f"After week {week}: {changes}")

    return plan, "\n\n".join(week_texts), "\n\n".join(change_log)
