#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def split_items(raw: str | None, fallback: list[str]) -> list[str]:
    if not raw:
        return fallback
    values = [item.strip() for item in raw.split("|") if item.strip()]
    return values or fallback


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--identity-lines", default="")
    parser.add_argument("--business-overview", default="")
    parser.add_argument("--capital-background", default="")
    parser.add_argument("--industry-position", default="")
    parser.add_argument("--risk-items", default="")
    parser.add_argument("--event-signals", default="")
    parser.add_argument("--banking-entry-points", default="")
    parser.add_argument("--next-steps", default="")
    parser.add_argument("--source-anchors", default="")
    parser.add_argument("--source-note", default="")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    identity_lines = split_items(
        args.identity_lines,
        [
            "公司全称待核验",
            "上市/注册主体信息待补充",
            "工商与经营状态待通过 PrimeMatrixData / Tianyancha 复核",
        ],
    )
    risk_items = split_items(
        args.risk_items,
        [
            "财务信息仍需结合审计报表核验。",
            "客户集中度、供应链稳定性和法律合规情况应继续补充。",
            "若涉及授信或投行业务推进，需增加公开披露与管理层材料验证。",
        ],
    )
    entry_points = split_items(
        args.banking_entry_points,
        [
            "现金管理：账户体系、存款沉淀与流动性安排。",
            "供应链金融：围绕核心客户/供应商应收应付开展融资。",
            "项目融资：若存在扩产、智算中心、重大采购，可作为切入点。",
        ],
    )
    event_signals = split_items(
        args.event_signals,
        [
            "最新公告/新闻：需补充最新融资、扩产、招投标或重大合作线索。",
            "经营动态：建议补抓近 90 天事件、媒体和公告，判断客户关系切入窗口。",
            "组织动向：建议补看招聘、管理层变动和区域扩张线索。",
        ],
    )
    next_steps = split_items(
        args.next_steps,
        [
            "确认企业主体与上市/非上市身份。",
            "获取最新公开披露或财务摘要。",
            "补齐司法、经营、合规与知识产权风险信息。",
            "形成客户经理首次接触话术与产品切入建议。",
        ],
    )
    source_anchors = split_items(
        args.source_anchors,
        [
            "PrimeMatrixData：企业主体、基础画像和行业线索。",
            "Tianyancha：工商、司法、风险、知识产权和合规补充。",
            "公开披露 / 年报 / 公告：正式对外使用前必须进一步核验。",
        ],
    )

    business_overview = args.business_overview or (
        f"{args.company} 当前作为客户经理内部调查对象进行初步分析，需进一步结合企业公开披露、管理层材料与外部数据服务补充完整。"
    )
    capital_background = args.capital_background or "股权结构、融资历程和资本背景待进一步确认。"
    industry_position = args.industry_position or "行业位置与竞争格局待结合同业与市场数据深化。"
    source_note = args.source_note or "本报告为内部初步调查稿，正式使用前仍需核验公开披露与审计材料。"

    title = args.company if not args.ticker else f"{args.company}（{args.ticker}）"
    lines = [
        f"# {title}客户调查报告",
        "",
        "> **内部使用 · 初步调查稿**",
        f"> {source_note}",
        "",
        "## 一、客户基本信息",
        "",
        "| 项目 | 内容 |",
        "|------|------|",
    ]
    for item in identity_lines:
        if "：" in item:
            left, right = item.split("：", 1)
        elif ":" in item:
            left, right = item.split(":", 1)
        else:
            left, right = "信息项", item
        lines.append(f"| {left.strip()} | {right.strip()} |")

    lines += [
        "",
        "## 二、业务与产品概况",
        "",
        business_overview,
        "",
        "## 三、股权结构与资本背景",
        "",
        capital_background,
        "",
        "## 四、经营动态与行业位置",
        "",
        industry_position,
        "",
        "## 五、风险与合规状况",
        "",
        "| 优先级 | 风险点 |",
        "|--------|--------|",
    ]
    for idx, item in enumerate(risk_items):
        priority = "高" if idx == 0 else "中" if idx < 3 else "低"
        lines.append(f"| {priority} | {item} |")

    lines += [
        "",
        "## 六、事件线索与经营动态",
        "",
        "| 线索类型 | 内容 |",
        "|----------|------|",
    ]
    for item in event_signals:
        if "：" in item:
            left, right = item.split("：", 1)
        elif ":" in item:
            left, right = item.split(":", 1)
        else:
            left, right = "事件线索", item
        lines.append(f"| {left.strip()} | {right.strip()} |")

    lines += [
        "",
        "## 七、银行合作切入点",
        "",
        "| 产品线 | 切入说明 |",
        "|--------|----------|",
    ]
    for item in entry_points:
        if "：" in item:
            left, right = item.split("：", 1)
        elif ":" in item:
            left, right = item.split(":", 1)
        else:
            left, right = "银行产品", item
        lines.append(f"| {left.strip()} | {right.strip()} |")

    lines += [
        "",
        "## 八、初步判断",
        "",
        "- 该客户具备进一步覆盖价值，但正式推进前应先补齐财务、风险和经营动态核验。",
        "- 调查重点应围绕企业身份、资金需求、上下游链条和可落地银行产品展开。",
        "",
        "## 九、下一步建议",
        "",
    ]
    lines.extend([f"{i + 1}. {item}" for i, item in enumerate(next_steps)])
    lines += [
        "",
        "## 十、来源与核验锚点",
        "",
    ]
    lines.extend([f"- {item}" for item in source_anchors])
    lines += [
        "",
        "---",
        "",
        "*本文件为自动生成的内部调查底稿，可作为客户经理首次内部讨论和后续分析包输入。*",
    ]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
