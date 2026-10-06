"""main.py - the command-line front door (the web app is app.py).

  python main.py "your offer in one sentence"
  python main.py --topic "post topic" --auto-approve     (auto-approve = testing only!)
"""
import argparse
from pathlib import Path

import llm
from config import ClientConfig
from pipeline import run_daily_post, run_strategy
from pattern5_approval import approval_gate

DEFAULT_OFFER = ("software that automatically chases late client invoices "
                 "for agencies with 10-50 employees")
DEFAULT_PROFILE = ("Headline: Founder & CEO at InvoiceWise\n"
                   "About: I am a founder with 10 years of experience in software. I started "
                   "InvoiceWise to build great products. Contact me to learn more.")
DEFAULT_TOPIC = "Late invoices are a communication problem, not a money problem"


def save(name: str, text: str, run_id: str) -> None:
    """FDE habit #2: save every output to a file so work is reviewable and never lost."""
    Path("outputs").mkdir(exist_ok=True)
    path = Path("outputs") / f"{run_id}_{name}.md"
    path.write_text(text)
    print(f"  saved: {path}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("offer", nargs="*", help="what the customer sells, in one sentence")
    parser.add_argument("--name", default="InvoiceWise")
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help="topic for the daily post")
    parser.add_argument("--auto-approve", action="store_true", help="TESTING ONLY")
    args = parser.parse_args()

    cfg = ClientConfig(business_name=args.name, offer=" ".join(args.offer) or DEFAULT_OFFER,
                       current_profile=DEFAULT_PROFILE)
    print(f"Mode: {'DEMO (no API key)' if llm.is_mock() else 'REAL (' + llm.active_model() + ')'}")
    print(f"Offer: {cfg.full_offer}\n")

    res = run_strategy(cfg)
    save("strategy", res.full_text(), res.run_id)

    status = approval_gate(res.full_text(), res.run_id, auto_approve=args.auto_approve)
    print(f"  Status: {status.upper()}\n")
    if status != "approved":
        print("Stopped before creating daily content. Nothing was posted anywhere.")
        return

    post = run_daily_post(cfg, res.icp, args.topic)
    save("daily_post", post, res.run_id)
    print("---- READY-TO-REVIEW POST PACKAGE ----")
    print(post)


if __name__ == "__main__":
    main()
