"""config.py - everything a buyer or reseller can change WITHOUT touching the agent code.

Three kinds of settings:
  1. PRESETS      - ready-made defaults per type of business (add your own niche here)
  2. ClientConfig - the details one customer fills in on the form
  3. brand.json   - white-label branding (product name, color, support email, guide link)
"""
import json
from dataclasses import dataclass, field
from pathlib import Path

PRESETS = {
    "SaaS founder": dict(
        tone="practical, data-aware, no fluff",
        goal="Generate 5 qualified demo calls per month",
        mix="about 60% educational, 20% storytelling, 20% engagement with soft calls to action",
    ),
    "Coach": dict(
        tone="warm, encouraging, story-led",
        goal="Book 5 discovery calls per month",
        mix="about 40% educational, 40% storytelling, 20% engagement questions",
    ),
    "Agency": dict(
        tone="confident, results-focused, proof-oriented (real examples only)",
        goal="Get 5 qualified inbound enquiries per month",
        mix="about 50% educational, 30% real case-study style, 20% engagement",
    ),
    "Consultant": dict(
        tone="authoritative, concise, insight-led",
        goal="Start 3 new client conversations per month",
        mix="about 60% insight and education, 20% storytelling, 20% engagement",
    ),
}
DEFAULT_PRESET = "SaaS founder"


@dataclass
class ClientConfig:
    business_name: str = ""
    offer: str = ""
    audience_hint: str = ""
    goal: str = ""
    preset: str = DEFAULT_PRESET
    voice_notes: str = ""
    current_profile: str = ""
    # Which strategy steps to run (untick to save time and money)
    run_icp: bool = True
    run_research: bool = True
    run_profile: bool = True
    run_plan: bool = True
    # Safety limits
    profile_rounds: int = 3
    profile_threshold: float = 8.0
    plan_weeks: int = 4

    def preset_values(self) -> dict:
        return PRESETS.get(self.preset, PRESETS[DEFAULT_PRESET])

    @property
    def tone(self) -> str:
        return self.preset_values()["tone"]

    @property
    def full_offer(self) -> str:
        name = self.business_name.strip()
        return f"{name}: {self.offer.strip()}" if name else self.offer.strip()

    @property
    def effective_goal(self) -> str:
        return self.goal.strip() or self.preset_values()["goal"]

    def style_note(self) -> str:
        """Plain-English style instructions that get added to the writing steps."""
        parts = [f"Tone: {self.tone}.", f"Content mix: {self.preset_values()['mix']}."]
        if self.voice_notes.strip():
            parts.append(f"The founder's own voice notes (follow them): {self.voice_notes.strip()}")
        return " ".join(parts)

    def estimate_calls(self) -> int:
        """Rough upper bound of AI calls for the strategy run, so users can see cost scale."""
        n = 1  # review checklist
        if self.run_icp:
            n += 4
        if self.run_research:
            n += 5
        if self.run_profile:
            n += 2 * self.profile_rounds
        if self.run_plan:
            n += 1 + self.plan_weeks + (self.plan_weeks - 1)
        return n


# ---- White-label branding ---------------------------------------------------
DEFAULT_BRAND = {
    "product_name": "LinkedIn Brand Engine",
    "tagline": "Your LinkedIn strategy, drafted by AI and approved by you.",
    "theme_hue": "indigo",  # any Gradio color name: blue, green, orange, purple, red, ...
    "support_email": "",
    "guide_url": "",
}


def load_brand(path: str = "brand.json") -> dict:
    """Read brand.json if it exists; any missing field falls back to the default."""
    brand = dict(DEFAULT_BRAND)
    file = Path(__file__).parent / path
    if file.exists():
        try:
            brand.update(json.loads(file.read_text()))
        except Exception as err:
            print(f"  ! brand.json could not be read ({err}); using defaults")
    return brand
