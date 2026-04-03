#!/usr/bin/env python3
import json
import os
import sys
import uuid
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional


BASE_URL = os.environ.get("BASE_URL", "https://mcp.yidian.cn/api").rstrip("/")
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
SESSION_ID: Optional[str] = None
LOG_PATH = os.environ.get("CODEX_MCP_DEBUG_LOG", "/tmp/prime_matrix_codex_bridge.log")


TOOLS = [
    {
        "name": "company_name",
        "description": "获取企业工商信息。先根据模糊公司名匹配精确公司名列表；在调用其他依赖公司名称的工具前应先调用此工具。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "blur_name": {
                    "type": "string",
                    "description": "企业相关关键字，输入字数>=2且不能仅输入“公司”或“有限公司”",
                }
            },
            "required": ["blur_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "basic_info",
        "description": "获取企业工商信息，包括企业状态、法人、统一信用代码、成立日期、注册资金、行业、地址、经营范围等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "judicial_info",
        "description": "获取企业司法信息，包括立案、法院公告、开庭公告、执行信息、司法拍卖、破产信息等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "risk_info",
        "description": "获取企业风险信息，包括经营异常、失信被执行人、严重违法、重大税收违法、限制高消费等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "ip_info",
        "description": "获取企业知识产权信息，包括专利和商标信息。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "shareholder_info",
        "description": "获取企业股东信息，包括十大流通股及工商登记股东信息。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "honor_info",
        "description": "获取企业荣誉信息，包括地区、荣誉名称、级别、发布单位、发布日期等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "statistic_info",
        "description": "按条件查询企业信息。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "industry": {"type": "string", "description": "公司所属行业，为2017年国标行业分类"},
                "entstatus": {"type": "string", "description": "公司状态，默认输入存续"},
                "start_date": {"type": "string", "description": "成立时间自，格式 YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "成立时间至，格式 YYYY-MM-DD"},
                "district_code": {"type": "string", "description": "企业所属区域编码，如 110000"},
                "page": {"type": "number", "description": "查询页数，默认 1"},
            },
            "required": ["industry", "entstatus", "start_date", "end_date", "district_code", "page"],
            "additionalProperties": False,
        },
    },
    {
        "name": "stk_company_basic_info",
        "description": "获取企业上市信息与债券信息，包括股票代码、股票简称、上市交易所、债券信息等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "job_info",
        "description": "获取企业招聘信息，包括招聘时间、薪资、教育要求、岗位描述等。",
        "inputSchema": {
            "type": "object",
            "properties": {"company_name": {"type": "string", "description": "公司精确名称"}},
            "required": ["company_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "finance_info",
        "description": "获取企业财务信息，包括资产负债表、利润表和现金流量表。若用户未提及时间，默认 2020-2024。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "公司精确名称"},
                "start_year": {"type": "string", "description": "查询年份自"},
                "end_year": {"type": "string", "description": "查询年份至"},
            },
            "required": ["company_name", "start_year", "end_year"],
            "additionalProperties": False,
        },
    },
]


ENDPOINTS = {
    "company_name": ("/company_name", {"blur_name": "blur_name"}),
    "basic_info": ("/basic_info", {"company_name": "company"}),
    "judicial_info": ("/judicial_info", {"company_name": "company"}),
    "risk_info": ("/risk_info", {"company_name": "company"}),
    "ip_info": ("/ip_info", {"company_name": "company"}),
    "shareholder_info": ("/shareholder_info", {"company_name": "company"}),
    "honor_info": ("/honor_info", {"company_name": "company"}),
    "statistic_info": (
        "/statistic_info",
        {
            "industry": "industro",
            "entstatus": "entstatus",
            "start_date": "start_date",
            "end_date": "end_date",
            "district_code": "district_code",
            "page": "page",
        },
    ),
    "stk_company_basic_info": ("/stk_company_basic_info", {"company_name": "company"}),
    "job_info": ("/job_info", {"company_name": "company"}),
    "finance_info": (
        "/finance_info",
        {"company_name": "company", "start_year": "start_year", "end_year": "end_year"},
    ),
}


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


def make_result(text: str, is_error: bool = False) -> Dict[str, Any]:
    result: Dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def request_json(path: str, query_params: Dict[str, Any], session_id: Optional[str]) -> Any:
    query = urllib.parse.urlencode({k: v for k, v in query_params.items() if v is not None})
    url = f"{BASE_URL}{path}"
    if query:
        url = f"{url}?{query}"
    headers = {"x-api-key": MCP_API_KEY, "X-MCP-Source": "mcp-stdio"}
    if session_id:
        headers["npm-session-id"] = session_id
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def notify_init(session_id: str) -> None:
    url = f"{BASE_URL}/npm-init"
    req = urllib.request.Request(url, headers={"X-MCP-Source": "mcp-stdio", "mcp-session-id": session_id})
    try:
        with urllib.request.urlopen(req, timeout=20):
            return
    except Exception:
        return


def handle_initialize(request_id: Any, params: Dict[str, Any]) -> None:
    global SESSION_ID
    SESSION_ID = str(uuid.uuid4())
    notify_init(SESSION_ID)
    protocol_version = params.get("protocolVersion", "2024-11-05")
    write_message(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"listChanged": False},
                },
                "serverInfo": {"name": "prime-matrix-codex-bridge", "version": "1.0.0"},
            },
        }
    )


def handle_tools_list(request_id: Any) -> None:
    write_message({"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}})


def handle_tools_call(request_id: Any, params: Dict[str, Any]) -> None:
    name = params.get("name")
    arguments = params.get("arguments", {}) or {}
    if name not in ENDPOINTS:
        write_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": make_result(f"Unknown tool: {name}", is_error=True),
            }
        )
        return

    path, field_map = ENDPOINTS[name]
    try:
        if name == "finance_info":
            arguments.setdefault("start_year", "2020")
            arguments.setdefault("end_year", "2024")
        query_params = {target_key: arguments.get(source_key) for source_key, target_key in field_map.items()}
        data = request_json(path, query_params, SESSION_ID)
        write_message({"jsonrpc": "2.0", "id": request_id, "result": make_result(json.dumps(data, ensure_ascii=False))})
    except Exception as exc:
        write_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": make_result(f"Error calling {name}: {exc}", is_error=True),
            }
        )


def handle_request(message: Dict[str, Any]) -> None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {}) or {}

    if method == "initialize":
        handle_initialize(request_id, params)
        return
    if method == "notifications/initialized":
        return
    if method == "ping":
        write_message({"jsonrpc": "2.0", "id": request_id, "result": {}})
        return
    if method == "tools/list":
        handle_tools_list(request_id)
        return
    if method == "resources/list":
        write_message({"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}})
        return
    if method == "resources/templates/list":
        write_message({"jsonrpc": "2.0", "id": request_id, "result": {"resourceTemplates": []}})
        return
    if method == "tools/call":
        handle_tools_call(request_id, params)
        return
    if request_id is not None:
        write_message(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }
        )


def main() -> None:
    while True:
        message = read_message()
        if message is None:
            break
        handle_request(message)


if __name__ == "__main__":
    main()
