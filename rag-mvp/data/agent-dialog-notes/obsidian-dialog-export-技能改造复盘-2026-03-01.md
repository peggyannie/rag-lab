---
title: "obsidian-dialog-export 技能改造复盘"
date: "2026-03-01"
tags: [codex-dialog, implementation]
source: codex-chat
template: implementation
status: done
---

# obsidian-dialog-export 技能改造复盘

## 目标
- 要解决的问题: 让技能路由更稳定、模板输出更可用、规则更可验证。
- 完成标准: 形成可执行路由规则、完善模板、补齐回归测试并完成自测。

## 实现方案
- 核心思路: 采用“上下文证据打分”进行模板路由，配合写入质量门禁。
- 关键权衡: 牺牲少量自由度，换取更稳定的一致性输出。

## 关键改动
- 变更对象: `SKILL.md`、7 个模板文件、`agents/openai.yaml`。
- 具体改动:
  - 重写路由规则为上下文打分与确定性选择算法。
  - 明确 `new/append/overwrite` 判定顺序与 `daily-log` 例外。
  - 增加写入前质量门禁（必填章节、空段落清理、命令块校验）。
  - 优化模板结构，加入最小引导字段。
  - 扩展回归案例到 12 条并执行一致性检查。

## 关键命令
```bash
cat > /Users/xuanling/.agents/skills/obsidian-dialog-export/SKILL.md
cat > /Users/xuanling/.agents/skills/obsidian-dialog-export/templates/*.md
apply_patch /Users/xuanling/.agents/skills/obsidian-dialog-export/agents/openai.yaml
rg -n "..." /Users/xuanling/.agents/skills/obsidian-dialog-export/SKILL.md
```

## 验证结果
- 验证方式: 规则一致性检查 + 模板必填章节检查。
- 结果摘要:
  - `PASS: routing spec consistency checks OK (cases=12)`
  - `PASS: template required sections present`

## 结论
已完成技能可用性升级，当前版本在“自动路由稳定性、输出质量一致性、可回归验证”三个维度明显更好用。

## 后续动作
- 在真实使用中遇到误判时，补充到回归案例并迭代打分信号。
