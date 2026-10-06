"""app.py - the web front end (a small Flask server).

How it works, in plain English:
  * The browser shows the page (templates/index.html).
  * When the user clicks a button, the page sends the form to this server.
  * The server starts the AI work in the background (it takes minutes) and hands back a
    ticket number ("job id"). The page asks "is it done yet?" every couple of seconds.
  * The visitor's API key lives only in memory for that one job. It is never saved or logged.

Run locally:   python app.py        then open http://localhost:7860
Run for real:  gunicorn -w 1 --threads 8 -b 0.0.0.0:7860 app:app
"""
import os
import re
import secrets
import threading
import time

from flask import Flask, jsonify, render_template, request

import llm
from config import PRESETS, ClientConfig, load_brand
from pipeline import run_daily_post, run_strategy

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200_000  # reject giant requests

JOB_TTL_SECONDS = 30 * 60   # forget finished jobs after 30 minutes
MAX_RUNNING_JOBS = int(os.environ.get("MAX_RUNNING_JOBS", "6"))
JOBS: dict = {}
LOCK = threading.Lock()

HUES = {  # friendly color names -> hex (brand.json "theme_hue" may also be a #hex value)
    "indigo": "#4f46e5", "blue": "#2563eb", "teal": "#0d9488", "green": "#16a34a",
    "orange": "#ea580c", "red": "#dc2626", "purple": "#9333ea", "pink": "#db2777",
}


def clean(value, limit: int) -> str:
    return str(value or "").strip()[:limit]


def friendly_error(err: Exception) -> str:
    """Turn a technical error into a sentence a non-technical person can act on."""
    name, text = type(err).__name__, str(err).lower()
    status = getattr(err, "status", None) or getattr(err, "status_code", None)
    if status == 404:
        return "The AI model name was not found for your key. The seller can change it (CLAUDE_MODEL or OPENAI_MODEL setting)."
    if status == 429 and "quota" in str(getattr(err, "detail", "")).lower():
        return "Your AI account has no credit or quota left. Add credit with your provider, then try again."
    if status == 401 or "authentication" in name.lower() or "invalid x-api-key" in text or "401" in text:
        return "Your API key was rejected. Create a new key with your AI provider and paste it again (no spaces). Make sure the provider choice on tab 1 matches your key."
    if "credit balance" in text or "billing" in text:
        return "Your AI account has no credit left. Add credit with your provider, then try again."
    if "ratelimit" in name.lower() or "rate limit" in text or "429" in text:
        return "Too many requests at once. Wait a minute and try again."
    if "overloaded" in text or "529" in text:
        return "The AI service is busy right now. Wait a minute and try again."
    if "permission" in name.lower() or "403" in text:
        return "Your API key does not have permission for this. Check the key in the Anthropic console."
    return f"Something went wrong ({name}). Try again; if it repeats, untick some steps and run a smaller version."


def start_job(api_key: str, provider: str, work) -> str | None:
    """Run `work(progress)` in a background thread. Returns a job id, or None if too busy."""
    with LOCK:
        now = time.time()
        for jid in [j for j, v in JOBS.items() if now - v["created"] > JOB_TTL_SECONDS]:
            del JOBS[jid]
        if sum(1 for v in JOBS.values() if v["status"] == "running") >= MAX_RUNNING_JOBS:
            return None
        job_id = secrets.token_urlsafe(12)
        job = {"status": "running", "progress": [], "result": None, "error": None,
               "mode": "demo", "engine": "", "created": now}
        JOBS[job_id] = job

    def runner():
        llm.force_demo()                  # never use the host's own key
        llm.set_api_key(api_key)          # this visitor's key, for this thread only
        llm.set_provider(provider)        # "anthropic", "openai" or "auto"
        job["mode"] = "demo" if llm.is_mock() else "real"
        if job["mode"] == "real":
            job["engine"] = f"{'OpenAI' if llm.current_provider() == 'openai' else 'Claude'} ({llm.active_model()})"
        try:
            job["result"] = work(lambda msg: job["progress"].append(msg))
            job["status"] = "done"
        except Exception as err:          # noqa: BLE001 - we show a friendly message instead
            job["error"] = friendly_error(err)
            job["status"] = "error"

    threading.Thread(target=runner, daemon=True).start()
    return job_id


def config_from(body: dict) -> ClientConfig:
    preset = clean(body.get("preset"), 40)
    return ClientConfig(
        business_name=clean(body.get("business_name"), 120),
        offer=clean(body.get("offer"), 600),
        audience_hint=clean(body.get("audience_hint"), 600),
        goal=clean(body.get("goal"), 300),
        preset=preset if preset in PRESETS else "SaaS founder",
        voice_notes=clean(body.get("voice_notes"), 600),
        current_profile=clean(body.get("current_profile"), 4000),
        run_icp=bool(body.get("run_icp", True)),
        run_research=bool(body.get("run_research", True)),
        run_profile=bool(body.get("run_profile", True)),
        run_plan=bool(body.get("run_plan", True)),
    )


@app.get("/")
def index():
    brand = load_brand()
    hue = brand.get("theme_hue", "indigo")
    brand["accent"] = hue if re.fullmatch(r"#[0-9a-fA-F]{6}", str(hue)) else HUES.get(hue, HUES["indigo"])
    presets = {k: {"goal": v["goal"], "tone": v["tone"]} for k, v in PRESETS.items()}
    with open(os.path.join(os.path.dirname(__file__), "guide_short.md"), encoding="utf-8") as f:
        guide = f.read()
    return render_template("index.html", brand=brand, presets=presets, guide=guide)


@app.post("/api/strategy")
def api_strategy():
    body = request.get_json(silent=True) or {}
    cfg = config_from(body)
    if not cfg.offer:
        return jsonify(error="Please describe what you sell (one sentence) on tab 1."), 400

    def work(progress):
        res = run_strategy(cfg, progress)
        return {"icp": res.icp, "research": res.research, "profile": res.profile,
                "profile_log": res.profile_log, "plan": res.plan, "weeks": res.weeks,
                "changes": res.changes, "review": res.review, "full": res.full_text()}

    job_id = start_job(clean(body.get("api_key"), 300), clean(body.get("provider"), 20), work)
    if job_id is None:
        return jsonify(error="The tool is busy right now. Please try again in a minute."), 429
    return jsonify(job_id=job_id)


@app.post("/api/post")
def api_post():
    body = request.get_json(silent=True) or {}
    if body.get("approved") is not True:      # the human-in-the-loop gate, enforced on the server
        return jsonify(error="Please tick the approval box first. Nothing is written without your approval."), 400
    cfg = config_from(body)
    topic = clean(body.get("topic"), 300)
    icp = clean(body.get("icp"), 6000) or cfg.audience_hint
    if not topic:
        return jsonify(error="Please type a topic for the post."), 400
    if not icp:
        return jsonify(error="Run the strategy first (or describe your audience on tab 1)."), 400

    def work(progress):
        return {"post": run_daily_post(cfg, icp, topic, clean(body.get("tone"), 200), progress)}

    job_id = start_job(clean(body.get("api_key"), 300), clean(body.get("provider"), 20), work)
    if job_id is None:
        return jsonify(error="The tool is busy right now. Please try again in a minute."), 429
    return jsonify(job_id=job_id)


@app.get("/api/job/<job_id>")
def api_job(job_id):
    job = JOBS.get(job_id)
    if job is None:
        return jsonify(status="error", error="This run expired. Please start it again."), 404
    return jsonify(status=job["status"], progress=job["progress"], result=job["result"],
                   error=job["error"], mode=job["mode"], engine=job["engine"])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "7860")), debug=False)
