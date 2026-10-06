"""Pattern 5 - Human in the loop: the AI prepares everything, then STOPS for a person.

Plain English: an assistant puts papers on your desk for signature. They never sign
for you.

Two parts:
  make_review()   - the AI writes a "verify before approving" checklist for the package
  approval_gate() - the command-line version of the stop sign (the web app uses a tick box)

Outcomes: approved -> continue | rejected -> stop | pending -> saved for later review
"""
import sys
from pathlib import Path

from agents import Agent

reviewer = Agent(
    "approval_assistant",
    "You prepare a founder to review an AI-generated LinkedIn strategy package. Write a short "
    "checklist titled 'Before you approve, verify:' covering: invented facts or numbers, "
    "tone matches the founder's real voice, claims he cannot back up, anything that could "
    "embarrass him, and what is missing. Then 'Recommended changes:' (max 5 bullets). "
    "Be specific to the package content.",
)


def assemble_package(offer, icp, research, profile, profile_log, plan, weeks, changes) -> str:
    """Join whatever was produced into one reviewable package (skipped steps are left out)."""
    sections = [
        ("Offer", offer), ("1. Ideal customer profile", icp),
        ("2. Market research brief", research),
        ("3. Optimized profile (headline + About)",
         f"{profile}\n\n_Loop log:_\n{profile_log}" if profile else ""),
        ("4. 30-day content plan", plan), ("4b. Written posts, weeks 1-4", weeks),
        ("4c. Plan changes the observer suggested", changes),
    ]
    return "\n\n".join(f"# {title}\n{body}" for title, body in sections if body)


def make_review(package: str) -> str:
    """Ask the AI for a tailored review checklist."""
    return reviewer.run(package, max_tokens=1200)


def approval_gate(full_package: str, run_id: str, auto_approve: bool = False) -> str:
    """Command-line approval: save the package, then ask a person (or stop if nobody is there)."""
    Path("outputs").mkdir(exist_ok=True)
    path = Path("outputs") / f"{run_id}_5_approval_package.md"
    path.write_text(full_package)
    print(f"  Review package saved: {path}")

    if auto_approve:
        print("  !! AUTO-APPROVE is ON (for testing only). A real human must approve real content.")
        return "approved"
    if sys.stdin.isatty():
        answer = input("  Approve this package? [a]pprove / [r]eject / [l]ater: ").strip().lower()
        return {"a": "approved", "r": "rejected"}.get(answer[:1], "pending")
    print("  No person is available to answer, so the pipeline STOPS here (status: pending).")
    return "pending"
