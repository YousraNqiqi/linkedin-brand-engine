# LinkedIn Brand Engine

A small multi-agent pipeline that turns a few business details into a LinkedIn brand package for a B2B company: ideal customer profile, market research, a stronger profile, a 4-week content plan, and ready-to-review posts.

**It never posts anything.** A person reviews and approves every output, and the approval gate is enforced on the server, not just in the page.

> **Project status (please read):** this is a learning and portfolio project. The sample customer ("InvoiceWise") is fictional. I built it with help from Claude. The full pipeline is tested end to end in **demo mode** (sample text, no API key). Output quality with a real AI key has not yet been evaluated, so treat results as drafts.

![Pipeline overview](docs/pipeline-overview.png)

## Why this exists

Many B2B leaders know their brand matters on LinkedIn but have no system for it. Strategy, profile, content and approval sit in different heads, so nothing compounds. This project explores how a chain of agents, with a person in control, could close that gap.

## The six agent patterns, and why each one

| # | Pattern | Job in the pipeline | File |
|---|---|---|---|
| 1 | Self-consistency | Three analysts define the ideal customer independently, then a consensus step settles it | `pattern1_icp.py` |
| 2 | ReWOO (plan, work, solve) | Plan the research questions first, run them in parallel, then synthesize | `pattern2_research.py` |
| 3 | Reflection | Writer and critic loop on the profile; stops at a score of 8 or more, or after 3 rounds | `pattern3_profile.py` |
| 4 | Adaptive planner | Plans 4 weeks, writes week by week, re-checks the plan after each week | `pattern4_planner.py` |
| 5 | Human in the loop | Nothing continues until a person approves | `pattern5_approval.py` |
| 6 | LLM compiler | A planner picks tasks; post, hook, hashtag and timing specialists run in parallel; an aggregator combines them | `pattern6_compiler.py` |

![Loops with exit rules](docs/patterns-3-4.png)

## Screens

| Business details | Progress | Approval locked | Approval unlocked |
|---|---|---|---|
| ![form](docs/app-form.png) | ![progress](docs/app-progress.png) | ![locked](docs/approval-locked.png) | ![unlocked](docs/approval-unlocked.png) |

## Engineering choices

- **One file talks to the AI** (`llm.py`). It supports Claude and OpenAI, so the patterns never know which provider answers.
- **Bring your own key.** A visitor's key lives only in memory for one run, is never logged, and the host's own keys are never used for visitors.
- **Validated AI output.** JSON from the model is parsed with fallbacks instead of trusted.
- **Bounded loops.** Every loop has a hard exit.
- **Server-side approval.** The daily-post endpoint rejects requests that are not approved.
- **Demo mode.** With no key the whole flow runs on sample text, so the wiring can be tested for free.

## Run it

```
pip install -r requirements.txt
python app.py                   # web app at http://localhost:7860
python main.py --auto-approve   # command-line test (auto-approve is for testing only)
```

No API key means demo mode. To use a real model, type your key into the app's key box (Claude or OpenAI) or set `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` on your own machine. Never commit a key.

## Known limits

- Agents use general model knowledge, not live web search, so claims need verifying.
- Real-AI output quality is untested so far.
- Hosting instructions in `DEPLOY.md` are untested.

## Other docs

`guide_short.md` (user guide), `DEPLOY.md` (hosting), `PATTERNS_EXPLAINED.md` (patterns in plain English), `CASE_FILE.md` (the fictional customer case).

## Credits

Pattern ideas inspired by a tutorial on six agent patterns: [add the creator's name and link here]. Built with Claude.

## Contact

Questions or want to see it run on your brand? Message me on LinkedIn: [add your profile link].
