# Quick Install — aigroup-lead-discovery-openclaw

> **target host**: macmini running OpenClaw with `main` agent on `minimax-cn/MiniMax-M2.7`.
> This is the **upstream** half of the banker stack. Install this first, then install `aigroup-financial-services-openclaw` second.

## 3-step install

```bash
# 1. Install via ClawHub (public)
openclaw plugins install clawhub:aigroup-lead-discovery-openclaw@latest

# 2. Restart gateway so cn-lead-safety + 5 lead-gen skills surface to main agent
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# 3. Run the preflight check
bash ~/.openclaw/extensions/aigroup-lead-discovery-openclaw/scripts/preflight.sh
```

Preflight exit 0 → plugin usable.

## Runtime dependencies

| Tool | Why |
|------|-----|
| `python3` ≥ 3.9 | runs `scripts/verify_intelligence.py` (Rule 4 inline-citation gate), `scripts/quality-audit.py` (data-quality-audit skill cross-check helper) |
| `node` ≥ 18 | standard OpenClaw bundle requirement |

Unlike the paired `aigroup-financial-services-openclaw`, this plugin does NOT need `pptxgenjs` or `python-pptx` — lead-discovery only emits markdown intelligence; slide compilation happens in the downstream plugin.

## Known pitfalls

### ClawHub transient "missing plugin.json" on install

Same workaround as the financial-services plugin:

```bash
find /var/folders -name "openclaw-clawhub-package-*" -type d 2>/dev/null | xargs rm -rf
openclaw plugins install clawhub:aigroup-lead-discovery-openclaw@latest
```

## Pair with the downstream banker plugin

Lead-discovery produces intelligence markdown that downstream banker workflow (datapack-builder / dcf-model / ppt-deliverable) reads. Install downstream too:

```bash
openclaw plugins install clawhub:aigroup-financial-services-openclaw@latest
```

See its own `QUICKSTART.md` for setup.

## Verify end-to-end

```bash
openclaw agent --agent main --thinking minimal --json --message "OK" | \
  python3 -c "import json,sys; t=sys.stdin.read(); d=json.loads(t[:t.index('}\n}')+3]); \
  sk=[s.get('name','?') for s in d['result']['meta']['systemPromptReport']['skills']['entries']]; \
  print('cn-lead-safety:', 'cn-lead-safety' in sk); \
  print('customer-investigation:', 'customer-investigation' in sk)"
```
