---
name: key-account-briefing
description: 客户首访前 briefing 技能。适用于“明天要拜访这家公司，帮我先做外网情报梳理”“给我一个客户画像卡和切入点”。使用 PrimeMatrixData-stdio、Tianyancha 与公开网页搜索，生成客户经理拜访前简报。
---

# 客户首访前 Briefing

用于拜访或首次触达前，快速形成一页式客户画像。

## 必做步骤

1. 用 `PrimeMatrixData-stdio.company_name` 确认企业
2. 用 `basic_info` + `shareholder_info` 获取基本画像
3. 用 `Tianyancha.companyBaseInfo` + `Tianyancha.risk` 做注册与风险交叉核验
4. 用 `job_info` / `honor_info` / `ip_info` 补增长与亮点
5. 补最新网页搜索，找最近 90 天事件

## 输出模板

### 客户画像
- 主营业务
- 企业阶段
- 规模与区域
- 股东与控制人特征

### 近期变化
- 招聘
- 扩张
- 合作
- 荣誉或资质

### 可能需求
- 融资
- 现金管理
- 供应链金融
- 结算与国际业务

### 风险提示
- 经营异常
- 司法诉讼
- 负面舆情

### 拜访建议
- 推荐开场
- 推荐切入问题
- 不宜直接触碰的话题

## 规则

- 输出要短、硬、能直接拿去拜访
- 明确区分“事实”“推断”“建议”
- 风险项不省略，但不要替代合规审查
