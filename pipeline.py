"""pipeline.py - runs the six patterns in order, driven by a ClientConfig.

Both the command line (main.py) and the web app (app.py) call these two functions,
so there is ONE engine and two front doors. FDE habit #6: separate "the engine" from
"the screen" so you can change either without breaking the other.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from config import ClientConfig
from pattern1_icp import run_icp
from pattern2_research import run_research
from pattern3_profile import run_profile
from pattern4_planner import run_planner
from pattern5_approval import assemble_package, make_review
from pattern6_compiler import run_compiler

NOT_RUN = "(This step was switched off.)"


@dataclass
class StrategyResult:
    run_id: str
    icp: str = NOT_RUN
    research: str = NOT_RUN
    profile: str = NOT_RUN
    profile_log: str = ""
    plan: str = NOT_RUN
    weeks: str = ""
    changes: str = ""
    review: str = ""
    package: str = ""

    def full_text(self) -> str:
        """Everything in one file the user can download."""
        return f"{self.package}\n\n# REVIEW CHECKLIST\n{self.review}\n"


def run_strategy(cfg: ClientConfig, progress: Callable[[str], None] = print) -> StrategyResult:
    """Patterns 1-4, then the review checklist for the human (pattern 5's preparation)."""
    res = StrategyResult(run_id=f"{datetime.now():%Y%m%d_%H%M%S}")
    offer = cfg.full_offer
    style = cfg.style_note()

    if cfg.run_icp:
        progress("Step 1/4: defining your ideal customer (3 analysts + 1 consensus agent)...")
        res.icp = run_icp(offer, cfg.audience_hint)
    else:
        res.icp = cfg.audience_hint.strip() or "No audience description was provided."
        progress("Step 1/4: skipped (using the audience you typed).")

    if cfg.run_research:
        progress("Step 2/4: researching your market (plan first, then 3 researchers at once)...")
        res.research = run_research(res.icp, offer)
    else:
        progress("Step 2/4: skipped.")

    if cfg.run_profile:
        progress("Step 3/4: rewriting your profile (writer and critic loop)...")
        res.profile, res.profile_log = run_profile(
            res.icp, res.research, cfg.current_profile,
            max_rounds=cfg.profile_rounds, threshold=cfg.profile_threshold, style=style)
    else:
        progress("Step 3/4: skipped.")

    if cfg.run_plan:
        progress("Step 4/4: building your 30-day plan (writing week by week and adapting)...")
        res.plan, res.weeks, res.changes = run_planner(
            res.icp, res.research, cfg.effective_goal, weeks=cfg.plan_weeks, style=style)
    else:
        progress("Step 4/4: skipped.")

    progress("Preparing your review checklist...")
    res.package = assemble_package(
        offer, res.icp, res.research,
        res.profile if cfg.run_profile else "", res.profile_log,
        res.plan if cfg.run_plan else "", res.weeks, res.changes)
    res.review = make_review(res.package)
    progress("Done. Read everything, then approve on the Daily post tab.")
    return res


def run_daily_post(cfg: ClientConfig, icp: str, topic: str, tone: str = "",
                   progress: Callable[[str], None] = print) -> str:
    """Pattern 6. Only call this AFTER a human approved the strategy."""
    progress("Writing your post (a planner picks the helpers, they work at the same time)...")
    voice = f" Voice notes: {cfg.voice_notes.strip()}" if cfg.voice_notes.strip() else ""
    return run_compiler(topic, icp, tone=f"{tone.strip() or cfg.tone}.{voice}")
