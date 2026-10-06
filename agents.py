"""agents.py - shared building block used by every pattern.

FDE habit #3: when you copy-paste the same code twice, move it to one shared file.
(We had `Agent` inside pattern1; pattern 2 needs it too, so it moved here.)
"""
import contextvars
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from llm import call_llm


@dataclass
class Agent:
    """An agent is just: a name + instructions (the 'system prompt')."""
    name: str
    instructions: str

    def run(self, task: str, max_tokens: int = 1500) -> str:
        print(f"  -> {self.name} working...", flush=True)
        return call_llm(self.instructions, task, max_tokens=max_tokens)


def parse_json_list(text: str):
    """Find a JSON list like [{"a": 1}] inside an AI reply. Return the list, or None if it fails.

    FDE habit #4: never trust AI output to be perfectly formatted - always have a fallback.
    """
    import json
    import re

    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)  # grab the [...] part
        result = json.loads(match.group(0))
        return result if isinstance(result, list) else None
    except Exception:
        return None


def parallel_map(fn, items):
    """Run fn on every item AT THE SAME TIME and return results in order.

    Each worker gets a copy of the current context, so the visitor's API key
    (kept in a context variable, see llm.py) follows the work into the threads.
    """
    with ThreadPoolExecutor() as pool:
        futures = [pool.submit(contextvars.copy_context().run, fn, item) for item in items]
        return [f.result() for f in futures]
