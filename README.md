# aigroup-lead-discovery-openclaw

Lead-discovery and company-intelligence suite for banker workflows on OpenClaw.

## Quick Install (macmini)

**Just want it running?** See [QUICKSTART.md](QUICKSTART.md).

```bash
openclaw plugins install clawhub:aigroup-lead-discovery-openclaw
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway
bash ~/.openclaw/extensions/aigroup-lead-discovery-openclaw/scripts/preflight.sh
```

This is the **upstream** half — install this first, then add `aigroup-financial-services-openclaw` second.


This plugin is the recommended first install in the AIGroup banker stack. Install it first as the intelligence and data-entry suite, then add `aigroup-financial-services-openclaw` as the downstream modeling and deliverables suite.

This repository is a standalone OpenClaw-compatible Claude bundle. The Hub release packages:

- five banker SOP skills for lead discovery and customer investigation
- no bundled MCP bridge runtime by default
- a clean skill-only install surface for OpenClaw Hub

It is also designed to be used alongside the AIGroup data-service MCP stack:

- `aigroup-fmp-mcp`
- `aigroup-market-mcp`
- `aigroup-finnhub-mcp`
- `Tianyancha`
- `PrimeMatrixData`

## Included

### Skills

- `client-initial-screening`
- `company-event-scan`
- `customer-investigation`
- `key-account-briefing`
- `weekly-lead-watchlist`

### Recommended companion AIGroup data services

- `aigroup-fmp-mcp`
- `aigroup-market-mcp`
- `aigroup-finnhub-mcp`

## Plugin Layout

```text
.claude-plugin/plugin.json
skills/
```

OpenClaw detects this repository as a Claude bundle and maps:

- `skills/` into normal OpenClaw skills

## Install

Recommended suite-first install flow:

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
openclaw plugins install aigroup-financial-services-openclaw
```

### OpenClaw Hub

```bash
openclaw plugins install aigroup-lead-discovery-openclaw
```

### Local path

```bash
openclaw plugins install ./aigroup-lead-discovery-openclaw
```

### GitHub shorthand

```bash
openclaw plugins install jackdark425/aigroup-lead-discovery-openclaw
```

### Claude Code

This repository is a single self-contained Claude plugin, but Claude Code installs plugins through marketplaces, not raw clones. Register it as a one-plugin marketplace in `.claude/settings.json` (project or user scope):

```json
{
  "extraKnownMarketplaces": {
    "aigroup-lead-discovery": {
      "source": {
        "source": "settings",
        "plugins": [
          {
            "name": "aigroup-lead-discovery-openclaw",
            "source": {
              "source": "github",
              "repo": "jackdark425/aigroup-lead-discovery-openclaw"
            }
          }
        ]
      }
    }
  },
  "enabledPlugins": {
    "aigroup-lead-discovery-openclaw@aigroup-lead-discovery": true
  }
}
```

For an opinionated banker stack that wires this plugin alongside the financial-services bundles, see the companion `banker/` workspace — it ships a ready-made `.claude/settings.json`.

Published package:

- `aigroup-lead-discovery-openclaw@0.1.8`

Recommended companion package:

- `aigroup-financial-services-openclaw`

Quick install guide:

- [docs/start-here.md](docs/start-here.md)
- [docs/quickstart.md](docs/quickstart.md)
- [docs/banker-stack.md](docs/banker-stack.md)
- [docs/example-prompts.md](docs/example-prompts.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [docs/which-suite-to-use.md](docs/which-suite-to-use.md)

## Verify After Install

```bash
openclaw plugins inspect aigroup-lead-discovery-openclaw
openclaw plugins inspect aigroup-financial-services-openclaw
openclaw skills list
```

## Recommended Trust Pinning

If you want to silence the `plugins.allow is empty` warning and pin trust explicitly, add the two AIGroup suite ids to your OpenClaw config:

```json
{
  "plugins": {
    "allow": [
      "aigroup-lead-discovery-openclaw",
      "aigroup-financial-services-openclaw"
    ]
  }
}
```

Then restart the gateway.

## Release Prep

Validate the repository bundle shape directly:

```bash
python3 scripts/validate_bundle.py .
```

ClawHub releases should be published from the repository root. The Hub release is intentionally skill-only so it avoids shipping optional bridge helpers that can trigger conservative static security scans.

## Environment

Recommended data sources for best results:

- `PrimeMatrixData`
- `Tianyancha`
- `aigroup-market-mcp`
- `aigroup-fmp-mcp`
- `aigroup-finnhub-mcp`

## What Each Skill Does

### `client-initial-screening`

Quickly decide whether a company is worth contacting at all. Focuses on entity confirmation, operating status, growth clues, risk flags, and a recommended next action.

### `company-event-scan`

Turns web and enterprise-data signals into outreach triggers such as hiring, expansion, partnerships, honors, financing clues, and likely banking entry points.

### `customer-investigation`

Default banker workflow for turning company intelligence into a structured Chinese customer investigation report. Use it when a client manager needs entity confirmation, business summary, risk review, and banking entry points in one internal memo.

### `key-account-briefing`

Produces a concise pre-meeting briefing for a banker before first contact or an on-site visit.

### `weekly-lead-watchlist`

Scans a batch list and ranks accounts into follow now, observe, or pause groups.

## Validation

This plugin has been validated on OpenClaw `2026.4.2` for:

- bundle loading
- MCP recognition
- skill discovery
- skill readiness

See [docs/validation.md](./docs/validation.md).

## Notes

- The plugin is distributed as a compatible bundle, not a native in-process OpenClaw plugin.
- The Hub release intentionally excludes optional local bridge helpers and focuses on portable skills.
- The recommended deployment model is suite-first: use this plugin for intelligence gathering and customer investigation, then use `aigroup-financial-services-openclaw` for customer analysis, modeling, and deliverable workflows.
