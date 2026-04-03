#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from typing import Any, Dict, Optional


REMOTE_URL = os.environ["TIANYANCHA_URL"]
AUTHORIZATION = os.environ["TIANYANCHA_AUTHORIZATION"]
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
        response = remote_post(message, SESSION_ID)
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


def main() -> None:
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
