# Putting the tool online (no coding, no installs)

Important: I could not test hosting from the build environment. The app itself was tested
(every screen, the API, mobile and dark mode). The steps below follow each provider's
standard flow, but their menus change, so check their current help pages if a label differs.

## What you are hosting
A small web app (Flask). Customers type their OWN API key into the page (Claude or OpenAI, they pick which). The host
never needs your key, and the app refuses to use any key set on the server, so you never
pay for customers' usage. Always use the HTTPS address the host gives you, because API keys
travel from the visitor's browser to your app.

## Option A: Hugging Face Spaces (easiest, free tier)
1. Create a free account at huggingface.co.
2. Click your profile picture, then "New Space". Name it, choose **Docker** as the SDK
   and "Blank" as the template. Choose **Private** while testing.
3. Open the Space's **Files** tab, click "Add file", then "Upload files", and drag in
   everything from the project folder (including the `templates` folder).
4. Upload `SPACE_README.md` and rename it to `README.md` (replace the existing one).
   Its top lines tell the host which kind of app this is.
5. Wait a few minutes while it builds. Open the Space: you should see the tool.
6. Test in demo mode first (leave the API key empty), then with a real key.

## Option B: Render
1. Put the project in a GitHub repository (github.com, "New repository", then "uploading an
   existing file").
2. On render.com choose "New", then "Web Service", and connect the repository.
3. Choose Docker as the runtime (it finds the `Dockerfile`), pick the free or cheapest plan.
4. Deploy, then open the address Render gives you.

## Rebranding for each customer (white-label)
Edit `brand.json`: product name, tagline, color (`indigo`, `blue`, `teal`, `green`, `orange`,
`red`, `purple`, `pink`, or a hex code like `#0a7cff`), support email and guide link.
Upload the changed file again and the page updates after the rebuild.
To add a new niche, copy one block in `config.py` under `PRESETS` and rename it.

## Before you charge money (checklist)
- [ ] Test a full run with a real key you control and read the output as a customer would.
- [ ] Set a small spending limit on your own Anthropic account while testing.
- [ ] Add your own terms: no auto-posting, no guarantees of results, customer reviews everything.
- [ ] Decide how customers pay and get access (a link they receive after paying, or a private
      host per client). The app itself has no login or payment, by design, to keep it simple.
- [ ] Get the guide book ready as a PDF (export it from the doc).
- [ ] Ask someone qualified about terms of service and local rules. This is not legal advice.

## Known limits of this first version
- Jobs are kept in memory: if the host restarts, a running job is lost (the user just reruns).
- No usage tracking, login or billing. Add these only after you have paying customers.
- The AI uses general knowledge, not live web search, so trends can be outdated.

## Choosing the AI models
Set these as environment variables (in the host's Settings, usually called "Variables" or "Secrets"):
- `CLAUDE_MODEL` (default `claude-sonnet-4-5`)
- `OPENAI_MODEL` (default `gpt-4o-mini`)
If a customer sees "model not found", change the variable to a model their account can use.
Do NOT set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` on the host: the web app ignores them on purpose.
