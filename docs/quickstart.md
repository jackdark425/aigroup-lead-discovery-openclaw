# Quickstart

## Install

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
```

If OpenClaw asks you to restart the gateway after installation, do that before testing.

## 30-Second Self-Check

```bash
openclaw plugins inspect aigroup-lead-discovery-openclaw
openclaw skills list
```

Expected results:

- the plugin shows `Status: loaded`
- the bundle format shows `claude`
- the plugin exposes `PrimeMatrixData-stdio` and `Tianyancha`
- the four lead-discovery skills appear as available skills

## What This Plugin Does

Use this plugin for:

- company screening
- event scanning
- pre-meeting account briefing
- weekly lead watchlists

## Recommended Pairing

Use it together with:

- `aigroup-fmp-mcp`
- `aigroup-market-mcp`
- `aigroup-finnhub-mcp`
- `aigroup-financial-services-openclaw`

That gives you a clean workflow:

- lead discovery plugin = intelligence and external signals
- AIGroup data MCPs = market and company data
- financial services plugin = modeling and deliverables
