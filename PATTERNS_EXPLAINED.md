# The 6 agent patterns from the video, in plain English

First, three words:
- **Agent:** an AI helper with a job description (instructions). It reads something and writes something.
- **Pattern:** a proven way to arrange several agents so the result is better than one agent alone. Like a recipe.
- **Parallel:** several things at the same time. **Sequential:** one after another.

One agent alone is like one employee doing everything. Patterns are about how to organize a small team.

---

## Pattern 1: Self-consistency (our ICP agent)

**Plain English:** Ask three people the same question separately, then keep what they all agree on.

**Analogy:** Three doctors examine you without talking to each other. If all three say "it's the flu", you trust it.

**How it works here:** Three analysts define Karim's buyer from different angles (business, pain, demographics). A fourth agent finds the overlap and flags who is NOT the buyer.

**Why use it:** One AI answer can be biased or random. Agreement across independent answers is more reliable.
**Trade-off:** Costs 4 calls instead of 1.

---

## Pattern 2: ReWOO (our market research agent)

**The name:** "Reasoning WithOut Observation". Ignore the name. The idea is simple.

**Plain English:** Write the whole to-do list first. Then do all the tasks at once. Then combine the results.

**Analogy, as in the video:** A normal agent (called ReAct) is a detective who asks one question, waits for the answer, thinks, asks the next question. Slow. A ReWOO detective writes all the questions on a sheet, sends assistants out together, and sums up when they return.

**How it works here:** The plan is fixed up front: (a) industry trends, (b) customer pains, (c) competitor gaps. Three researchers run in parallel. A resolver agent combines them into "top 3 positioning angles, what NOT to post, quick wins".

**Why use it:** Much faster and cheaper than a back-and-forth loop, when you already know what questions to ask.
**Trade-off:** If the first answer changes what you should ask next, ReWOO can't adapt. That is why Pattern 4 exists.

---

## Pattern 3: Reflection (our profile writer)

**Plain English:** One agent writes, another agent grades it, and the writer rewrites until the grade is good enough.

**Analogy:** A writer and an editor. The editor sends it back with notes until it's approved.

**How it works here:** The writer drafts Karim's headline and About section. The critic scores it out of 10 on five things: attracts the right buyer, keywords, clarity, outcome, call to action. Below 8 means "try again with this feedback". It stops when approved.

**Why use it:** First drafts from AI are average. A critic loop reliably raises quality.
**Trade-off:** Needs a stop rule (a maximum number of rounds), or it can loop forever and cost money.

---

## Pattern 4: Adaptive planner (our 30-day content plan)

**Plain English:** Make a plan, do one piece, check if the plan is still right, adjust, continue.

**Analogy:** A GPS. It plans the route, but recalculates when there is traffic.

**How it works here:** A planner builds the 30-day plan. For each week, a writer produces that week's posts. An observer checks if topics are still relevant and changes the remaining weeks.

**Why use it:** LinkedIn trends move. A fixed calendar goes stale.
**Difference from ReWOO:** ReWOO makes a plan once and never changes it. This one keeps changing the plan as it learns.

---

## Pattern 5: Human in the loop (our approval gate)

**Plain English:** The AI prepares everything, then stops and waits for a person to say yes, edit, or no.

**Analogy:** An assistant puts documents on your desk for signature. They never sign for you.

**Why use it:** It's Karim's name and reputation. The AI doesn't know his tone, his history, or what is risky to say. This is the most important pattern for trust, and it is the thing customers worry about most.
**FDE lesson:** Building the gate is easy. Deciding what needs approval, and making review take 15 minutes instead of 2 hours, is the real work.

---

## Pattern 6: LLM Compiler (our daily post maker)

**Plain English:** A "boss" agent reads the request and decides which tasks are needed. The specialists then run at the same time, and a final agent assembles the result.

**Analogy:** A newsroom editor reads a story idea, then assigns one person the article, one the headline options, one the hashtags, and everyone works at once. Another editor assembles the page.

**How it works here:** For a post topic, a compiler plans the tasks. A post writer, a hook analyzer (three headline options, scored) and a hashtag researcher run in parallel. An aggregator delivers the post, the best hook, hashtags, and best posting time.

**Difference from a plain parallel step:** In plain parallel, the tasks are always the same. Here the compiler decides which tasks to run based on the request.

---

## Quick comparison

| Pattern | One-line idea | Speed | Quality gain |
|---|---|---|---|
| 1 Self-consistency | Many independent opinions, keep the agreement | Medium | More reliable |
| 2 ReWOO | Plan first, do tasks in parallel | Fast | Same quality, cheaper |
| 3 Reflection | Write, critique, rewrite | Slow | Much better text |
| 4 Adaptive planner | Plan, do, re-plan | Medium | Stays relevant |
| 5 Human in the loop | Stop for approval | Depends on person | Trust and safety |
| 6 LLM Compiler | Boss decides tasks, specialists run together | Fast | Flexible |

## The video's five building blocks (Google ADK) mapped to plain Python

The video uses Google's ADK toolkit. We use plain Python so you can see how it works.

| ADK piece | Meaning | Our version |
|---|---|---|
| LLM agent | One AI worker with instructions | the `Agent` class |
| Sequential agent | Run steps in order | lines of code one after another |
| Parallel agent | Run steps together | ThreadPoolExecutor |
| Loop agent | Repeat until a stop rule | a `while` loop (Pattern 3) |
| Custom agent | Your own logic | any Python function |

The whole video is these five Lego bricks combined in different ways.
