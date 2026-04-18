---
name: customer-investigation
description: Generate a structured company profile and onboarding memo in Chinese for internal banking relationship management. Use when a relationship manager needs a pre-meeting research brief, credit onboarding summary, or company overview report for a prospective corporate client. Sources data from authorised enterprise data services (PrimeMatrixData, Tianyancha) and public web search.
---

# 客户调查

为银行客户经理生成一版可内部使用的客户调查报告。默认中文输出，重点是把企业信息收集、风险识别、银行切入点和下一步动作整理成一份结构化调查稿。

## CN Lead-Gen Pre-flight（target 为中国公司时 MANDATORY）

当 target 是中国大陆 / 港股 / 中概股 entity（触发词：A股 / 港股 / 科创板 / 创业板 / 北交所 / 中概股 / H 股，或 `*.SH` / `*.SZ` / `*.BJ` / `*.HK` ticker，或公司中文名），**在开始本 skill 任何步骤之前**先加载并遵循 [`cn-lead-safety`](../cn-lead-safety/SKILL.md) skill 的 5 条 Rule：

- **Rule 1** 中文 UTF-8 literal，禁 `\uXXXX` escape（MiniMax-M2.7 escape 下"寒武纪→宽厭谛79"类 typo 实测可复现）
- **Rule 2** 公司名 / 术语 lexicon lookup（跨插件参考 `aigroup-financial-services-openclaw/skills/cn-client-investigation/references/cn-lexicon.js`，含 consumer_brand 等 6 行业词典）
- **Rule 3** 数据源 tier：T1 巨潮/Tushare/交易所 > T2 天眼查/工商 > T3 FMP/Finnhub > T4 财经媒体
- **Rule 4** 每个硬数字（营收/市值/员工数/融资等）必须**内联** source citation；客户调查尤其敏感，下游 `datapack-builder` / `dcf-model` 会引用本 skill 的 intelligence 作 primary 输入
- **Rule 5** 数据不可得标 "N/A / 数据不可得"，**禁** fabricate 估算数字

交付前必须跑 `python3 ../cn-lead-safety/scripts/verify_intelligence.py <investigation.md>`，exit 0 方可交给下游 banker workflow。

## 适用场景

- 客户调查
- 尽职调查
- 授信前初筛
- 客户准入讨论
- 客户经理首次拜访前准备
- 需要把企业情报整理成一份完整的内部调查稿

## 默认流程

## 稳定脚本路径

当 OpenClaw 需要稳定落一版 Markdown 调查稿时，优先直接调用：

```bash
python skills/customer-investigation/scripts/build_customer_investigation.py \
  --company "目标企业" \
  --ticker "可选代码" \
  --identity-lines "公司全称：目标企业|股票代码：688256.SH|经营状态：在营" \
  --business-overview "企业主营业务简介" \
  --capital-background "股权结构和融资背景摘要" \
  --industry-position "行业位置和竞争观察" \
  --risk-items "风险1|风险2|风险3" \
  --banking-entry-points "现金管理：说明|供应链金融：说明|项目融资：说明" \
  --next-steps "动作1|动作2|动作3" \
  --source-note "初步调查稿，正式使用前需核验" \
  --output /tmp/customer-investigation.md
```

这条路径的目标是稳定生成可内部使用的一版中文客户调查报告。

### Step 1: 客户识别与实体确认

优先确认：

- 企业全称
- 是否上市 / 股票代码
- 注册地 / 法人 / 注册资本
- 存续状态

优先使用：

- `PrimeMatrixData`
- `Tianyancha`

如果用户给的是模糊名称，先澄清目标实体，再继续。

### Step 2: 信息收集

至少覆盖这些维度：

1. 企业身份与工商信息
2. 主营业务与产品结构
3. 股东结构 / 控股背景 / 上市信息
4. 风险与合规
5. 行业位置与竞争格局
6. 事件线索与经营动态
7. 银行切入点

优先工具顺序：

1. `PrimeMatrixData`：公司画像、行业线索、竞品比较
2. `Tianyancha`：工商、司法、风险、知识产权
3. `aigroup-market-mcp` / `aigroup-finnhub-mcp` / `aigroup-fmp-mcp`：上市公司和市场侧补充
4. OpenClaw 自带 web / browser / search：补最新公开事件

### Step 3: 风险分级

至少识别：

- 司法风险
- 经营风险
- 财务风险
- 客户集中度 / 行业景气风险
- 供应链 / 地缘政治 / 政策风险

输出时用 `高 / 中 / 低` 或 `红 / 黄 / 绿` 分级，并写出为什么会影响银行关系。

### Step 4: 银行视角分析

不要只做公司介绍，要明确回答：

- 为什么值得跟进
- 适合从什么银行产品切入
- 当前主要障碍是什么
- 需要先补哪几类核实材料

切入点至少考虑：

- 现金管理
- 供应链金融
- 项目融资
- 贸易金融
- 授信 / 流贷
- 投行 / 资本市场对话

## 输出标准

默认输出为中文 Markdown 调查报告。除非用户明确要求英文，不要输出英文主稿。

最低结构：

```markdown
# [企业名称]客户调查报告

## 一、客户基本信息
## 二、业务与产品概况
## 三、股权结构与资本背景
## 四、经营动态与行业位置
## 五、风险与合规状况
## 六、银行合作切入点
## 七、初步判断
## 八、下一步建议
```

### 质量要求

- 不要停留在两三段摘要
- 如果可以稳定走脚本路径，先用脚本落一版完整 Markdown，再按需要补充更多事实
- 至少包含 3 张表中的 2 张：
  - 客户身份表
  - 风险分级表
  - 银行切入点表
  - 下一步行动表
- 如果数据仍是初步信息，要明确标注“需结合审计财报 / 公告 / 管理层材料进一步核验”
- 不要写 “smoke test”“fictional”“占位” 这类用户不可用文案

## 推荐表格

### 客户身份表

| 项目 | 内容 |
|------|------|
| 公司全称 | |
| 股票代码 | |
| 成立时间 | |
| 注册资本 | |
| 法定代表人 | |
| 注册地址 | |
| 经营状态 | |

### 风险分级表

| 优先级 | 风险类别 | 对银行业务影响 |
|--------|----------|----------------|
| 高/中/低 | | |

### 银行切入点表

| 产品线 | 切入点 | 说明 |
|--------|--------|------|
| 现金管理 | | |

## 与 banker stack 的配合

如果用户后续还要形成分析交付物，调查报告完成后建议继续调用：

- `aigroup-financial-services-openclaw` 的 `customer-analysis-pack`
- 或 `datapack-builder`

把本调查稿转成更正式的分析包、datapack 或后续建模输入。
