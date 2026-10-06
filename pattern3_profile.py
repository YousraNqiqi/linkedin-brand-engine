"""Pattern 3 - Reflection: write -> critique -> rewrite, until it is good enough.

Plain English: a writer and an editor. The editor scores the draft and sends it back
with notes. The writer rewrites. Repeat.

Two safety rules (FDE habit #5 - every loop needs an exit):
  * STOP when the score reaches the threshold (good enough), OR
  * STOP after max_rounds (so it can never loop forever and burn money).

Also: the CODE decides when to stop by reading the score. We do not simply trust the
critic's word "approved".
"""
import re

from agents import Agent

writer = Agent(
    "profile_writer",
    "You write LinkedIn headlines and About sections for B2B founders. Write for the "
    "ideal customer, not for the founder's ego: lead with the buyer's problem and the "
    "outcome, include natural keywords, end with one clear call to action. Never invent "
    "numbers or customers. Output: HEADLINE (max 220 characters), then ABOUT (max 1,500 "
    "characters). If feedback is provided, fix every issue it lists.",
)

critic = Agent(
    "profile_critic",
    "You are a strict LinkedIn profile critic. Score the draft 1-10 on five things: "
    "ICP attraction, keyword optimization, clarity, outcome focus, call to action. "
    "Then list what works and what must improve (specific, short). Penalize invented "
    "facts. End with exactly two lines:\nSCORE: <overall number from 1 to 10>\n"
    "VERDICT: APPROVED or NEEDS REVISION",
)


def parse_score(review: str):
    """Read 'SCORE: 8.5' from the critic's text. Return a number, or None if missing."""
    match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", review)
    return float(match.group(1)) if match else None


def run_profile(icp: str, research: str, current_profile: str,
                max_rounds: int = 3, threshold: float = 8.0, style: str = ""):
    context = (f"Ideal customer profile:\n{icp}\n\nMarket research brief:\n{research}\n\n"
               f"Current profile (to improve):\n{current_profile or '(empty)'}\n\nStyle: {style}")
    feedback = "No feedback yet - this is the first draft."
    log = []

    for round_no in range(1, max_rounds + 1):
        print(f"  Round {round_no}/{max_rounds}")
        draft = writer.run(f"{context}\n\nCritic feedback to fix:\n{feedback}")
        review = critic.run(f"Ideal customer:\n{icp}\n\nDraft profile:\n{draft}")
        score = parse_score(review)
        log.append(f"Round {round_no}: score = {score if score is not None else 'unreadable'}")
        print(f"    score: {score}")
        if score is not None and score >= threshold:
            log.append("Stopped: score reached the threshold.")
            break
        feedback = review
    else:
        log.append(f"Stopped: reached the {max_rounds}-round limit (human should review closely).")

    return draft, "\n".join(log)
