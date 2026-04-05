#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


def iter_openclaw_config_paths() -> list[Path]:
    home = Path.home()
    preferred = home / ".openclaw" / "openclaw.json"
    others = sorted(home.glob(".openclaw*/openclaw.json"))
    paths: list[Path] = []
    if preferred.exists():
        paths.append(preferred)
    for candidate in others:
        if candidate not in paths:
            paths.append(candidate)
    return paths


def load_openclaw_config() -> Dict[str, Any]:
    for config_path in iter_openclaw_config_paths():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def load_best_provider_config(provider_id: str) -> Dict[str, Any]:
    for config_path in iter_openclaw_config_paths():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        providers = (((config.get("models") or {}).get("providers")) or {})
        provider = providers.get(provider_id)
        if isinstance(provider, dict) and provider:
            return config
    return load_openclaw_config()


def resolve_tianyancha_settings(config: Dict[str, Any]) -> Dict[str, str]:
    env_url = os.environ.get("TIANYANCHA_URL") or os.environ.get("TIANYANCHA_MCP_URL")
    env_auth = os.environ.get("TIANYANCHA_AUTHORIZATION")
    if env_url and env_auth:
        return {"url": env_url, "authorization": env_auth}
    providers = (((config.get("models") or {}).get("providers")) or {})
    provider = providers.get("tianyancha") or {}
    url = provider.get("baseUrl") if isinstance(provider.get("baseUrl"), str) else ""
    auth = provider.get("apiKey") if isinstance(provider.get("apiKey"), str) else ""
    if auth == "TIANYANCHA_AUTHORIZATION":
        auth = os.environ.get("TIANYANCHA_AUTHORIZATION", "")
    return {"url": url, "authorization": auth}


CONFIG = load_best_provider_config("tianyancha")
SETTINGS = resolve_tianyancha_settings(CONFIG)
REMOTE_URL = SETTINGS["url"]
AUTHORIZATION = SETTINGS["authorization"]
SESSION_ID: Optional[str] = None
INITIALIZED = False
LOG_PATH = os.environ.get("CODEX_MCP_DEBUG_LOG", "/tmp/tianyancha_codex_bridge.log")


def write_message(message: Dict[str, Any]) -> None:
    log(f"OUT {json.dumps(message, ensure_ascii=False)}")
    payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()


def read_message() -> Optional[Dict[str, Any]]:
    headers: Dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        decoded = line.decode("utf-8").strip()
        if ":" in decoded:
            key, value = decoded.split(":", 1)
            headers[key.lower()] = value.strip()
    content_length = int(headers.get("content-length", "0"))
    if content_length <= 0:
        return None
    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    message = json.loads(body.decode("utf-8"))
    log(f"IN {json.dumps(message, ensure_ascii=False)}")
    return message


def log(message: str) -> None:
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(message + "\n")
    except Exception:
        pass


def parse_sse_body(body: str) -> Optional[Dict[str, Any]]:
    chunks = []
    for block in body.split("\n\n"):
        for line in block.splitlines():
            if line.startswith("data:"):
                chunks.append(line[5:].strip())
    if not chunks:
        return None
    return json.loads("".join(chunks))


def remote_post(payload: Dict[str, Any], session_id: Optional[str]) -> Optional[Dict[str, Any]]:
    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(
        REMOTE_URL,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = resp.read().decode("utf-8", "replace")
        new_session_id = resp.headers.get("mcp-session-id")
        if new_session_id:
            global SESSION_ID
            SESSION_ID = new_session_id
        content_type = resp.headers.get("content-type") or ""
        if "text/event-stream" in content_type:
            return parse_sse_body(body)
        if not body.strip():
            return None
        return json.loads(body)


def rewrite_cli_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    method = payload.get("method")
    if method != "tools/call":
        return payload
    params = payload.setdefault("params", {})
    tool_name = params.get("name")
    arguments = params.setdefault("arguments", {})
    if tool_name in {"companyBaseInfo", "risk"} and "companyName" in arguments and "keyword" not in arguments:
        arguments["keyword"] = arguments["companyName"]
    return payload


def handle_initialize(message: Dict[str, Any]) -> None:
    global SESSION_ID
    payload = {
        "jsonrpc": "2.0",
        "id": message["id"],
        "method": "initialize",
        "params": message.get("params", {}),
    }
    response = remote_post(payload, None)
    if response is None:
        write_message(
            {
                "jsonrpc": "2.0",
                "id": message["id"],
                "error": {"code": -32000, "message": "Tianyancha initialize returned no response"},
            }
        )
        return
    if "result" in response:
        capabilities = response["result"].setdefault("capabilities", {})
        capabilities.setdefault("resources", {"listChanged": False})
    write_message(response)


def handle_initialized() -> None:
    global INITIALIZED
    INITIALIZED = True
    try:
        remote_post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, SESSION_ID)
    except Exception:
        return


def handle_forward(message: Dict[str, Any]) -> None:
    try:
        response = remote_post(rewrite_cli_payload(message), SESSION_ID)
        if response is not None:
            write_message(response)
        elif "id" in message:
            write_message({"jsonrpc": "2.0", "id": message["id"], "result": {}})
    except Exception as exc:
        if "id" in message:
            write_message(
                {
                    "jsonrpc": "2.0",
                    "id": message["id"],
                    "error": {"code": -32000, "message": f"Tianyancha bridge error: {exc}"},
                }
            )


def run_cli(tool_name: str, arguments: Dict[str, Any]) -> int:
    payload = rewrite_cli_payload(
        {
            "jsonrpc": "2.0",
            "id": "cli",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
    )
    try:
        response = remote_post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "lead-discovery-cli", "version": "1.0.0"}}}, None)
        if response is None:
            print(json.dumps({"ok": False, "error": "No initialize response"}, ensure_ascii=False))
            return 1
        result = remote_post(payload, SESSION_ID)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


def main() -> None:
    if len(sys.argv) >= 3:
        tool_name = sys.argv[1]
        try:
            arguments = json.loads(sys.argv[2])
        except Exception as exc:
            print(json.dumps({"ok": False, "error": f"Invalid JSON args: {exc}"}, ensure_ascii=False))
            raise SystemExit(1)
        raise SystemExit(run_cli(tool_name, arguments))

    while True:
        message = read_message()
        if message is None:
            break
        method = message.get("method")
        if method == "initialize":
            handle_initialize(message)
        elif method == "notifications/initialized":
            handle_initialized()
        elif method == "resources/list":
            write_message({"jsonrpc": "2.0", "id": message["id"], "result": {"resources": []}})
        elif method == "resources/templates/list":
            write_message({"jsonrpc": "2.0", "id": message["id"], "result": {"resourceTemplates": []}})
        else:
            handle_forward(message)


if __name__ == "__main__":
    main()
