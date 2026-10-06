# Case File: LinkedIn Brand Engine for InvoiceWise

> FICTIONAL scenario for practice. You are the FDE (forward deployed engineer) assigned to this customer.
> Every step below is tagged TECH or PEOPLE, because an FDE does both.

## 1. The customer

**Company:** InvoiceWise (fictional), a B2B SaaS that automatically chases late invoices for small agencies.
**Your contact:** Karim, founder and CEO. 8 customers, 4 months old, no marketing team, no sales team.
**Why you were called in:** His sales come from his network, which is running dry. He knows founders buy from founders they follow on LinkedIn, but he posts rarely and his profile reads like a CV.

## 2. Kickoff call notes (what Karim said, in his own words)

- "I need 5 demo calls a month from LinkedIn. I don't need 5,000 followers."
- "I post once, get 6 likes, and give up."
- "I don't want a bot spamming people. My name is my brand."
- "I have maybe one hour a week. I'm also the CEO, the support team and the sales team."
- "My buyers are owners of agencies with 10 to 50 people who hate chasing clients for money."
- Unsaid but visible: he has not defined his buyer precisely, and he is nervous about AI writing in his name.

PEOPLE skill: listen for the real need under the request. He asked for "a LinkedIn bot", but the real need is "predictable demo calls without losing my voice or my time".

## 3. Needs map

| Karim's pain | Real need | What we build | Pattern |
|---|---|---|---|
| "I don't know exactly who to write for" | A sharp buyer definition | ICP agent | 1 Self-consistency |
| "I don't know what agency owners care about" | Market intel | Research agent | 2 ReWOO |
| "My profile reads like a CV" | Profile that sells | Profile writer + critic loop | 3 Reflection |
| "I don't know what to post" | A plan that adapts | 30-day planner | 4 Adaptive planner |
| "I don't trust AI with my name" | Control | Approval gate | 5 Human in the loop |
| "Writing takes forever" | Fast daily drafts | Post compiler | 6 LLM Compiler |

## 4. Success metrics (agreed with the customer)

- Karim spends 1 hour or less per week.
- 2 posts a week published for 4 weeks.
- At least 5 inbound demo requests per month by month 3 (a business result, not a tech result).
- Karim rates drafts 4 out of 5 or better by week 4.

PEOPLE skill: agree on a business metric, not "the agents work". Customers care about calls booked.

## 5. Scope

**In scope:** ICP, market research, profile rewrite, 30-day plan, approval step, daily post drafts, a simple web page for Karim.
**Out of scope (say this out loud on the kickoff call):** auto-posting, scraping LinkedIn, auto-messaging strangers, ad management. Reason: against LinkedIn rules and against Karim's wish.

## 6. Risks and answers

| Risk | Answer |
|---|---|
| Posts sound generic | Feed in Karim's real stories and past writing; he edits |
| AI invents customer stats | Rule: no numbers without a source; reviewer checklist |
| Karim stops using it | Weekly 15-minute review format; he only approves or edits |
| API cost surprises | Mock mode for testing, spending cap, cheaper model while developing |

## 7. Delivery plan (how an FDE runs it)

| Phase | What happens | TECH | PEOPLE |
|---|---|---|---|
| 1 Discover | Kickoff and needs map | | Interview, listen, write notes (done above) |
| 2 Scope | Agree what's in and out | | Set expectations, get written agreement |
| 3 Prototype P1 | ICP agent running for real | Build, test | Show Karim the ICP, ask "is this your buyer?" |
| 4 Prototype P2 | Research agent | Parallel tasks | Share findings, ask what surprised him |
| 5 Prototype P3 | Profile loop | Writer and critic | Get his taste: which headline sounds like him? |
| 6 Prototype P4 | 30-day plan | Planner | Walk through week 1 together |
| 7 Add control | Approval gate | Human in the loop | Agree what needs his sign-off |
| 8 Daily engine | Post compiler | Parallel build | Train him on a 15-minute weekly routine |
| 9 Harden | Logging, errors, cost cap | Reliability | Explain limits honestly |
| 10 Hand over | Web page and one-page guide | Gradio UI | Short demo and Q&A |

## 8. What you hand Karim at the end

1. The working system (a simple web page).
2. A one-page "how to use it in 1 hour a week" guide.
3. A short report: what we built, what it cannot do, what we would do next.

## 9. Your FDE skill checklist (tick as you practise)

- [ ] I can explain what each agent does to a non-technical person in 2 sentences.
- [ ] I wrote down what is NOT in scope.
- [ ] I tied every feature to a customer pain.
- [ ] I showed a working demo early, not at the end.
- [ ] I can say what could go wrong and how we handle it.
