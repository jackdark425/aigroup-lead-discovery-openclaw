# Example Prompts

These are copy-paste examples for the AIGroup banker stack.

Install the suite first:

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
openclaw plugins install aigroup-financial-services-openclaw
```

## Lead Discovery First Run

Use this when you want a fast first-pass screen on a target company:

```text
Use the client-initial-screening skill for 华为技术有限公司.
Confirm the legal entity, summarize what the company does, highlight why a banker should contact it, list the main risk flags, and suggest the next three follow-up actions.
Return the answer in concise markdown with these headings:
- Company summary
- Reason to contact
- Risk flags
- Next steps
```

## Event Scan Example

Use this when you want outreach triggers rather than a general screen:

```text
Use the company-event-scan skill for 华为技术有限公司.
Focus on recent external events, expansion signals, hiring, partnerships, financing clues, and possible banking entry points.
Return a banker-facing summary with urgency level, signal list, and recommended outreach angle.
```

## Weekly Watchlist Example

Use this when you already have a batch of accounts:

```text
Use the weekly-lead-watchlist skill for this list:
华为技术有限公司
比亚迪股份有限公司
宁德时代新能源科技股份有限公司

Rank each account as follow now, observe, or pause.
For each company, explain the ranking and provide one suggested next action.
```

## End-to-End Stack Example

Step 1 prompt for the lead-discovery suite:

```text
Use the client-initial-screening skill for 华为技术有限公司.
Return company summary, reason_to_contact, risk_flags, and next_steps.
```

Step 2 prompt for the financial-services suite:

```text
Use datapack-builder to create a first-pass datapack for 华为技术有限公司 based on the screening summary and available public company context.
Include a short assumptions section and produce a workbook-ready deliverable summary.
```

## CLI Example

If you want to call OpenClaw directly from the terminal, this is the simplest pattern:

```bash
openclaw agent --agent main --session-id banker-demo-001 -m "Use the client-initial-screening skill for 华为技术有限公司. Return company summary, reason_to_contact, risk_flags, and next_steps."
```

If your environment uses a non-default agent, replace `main` with your preferred agent id.
