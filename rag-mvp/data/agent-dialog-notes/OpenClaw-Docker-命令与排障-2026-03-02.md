---
title: "OpenClaw Docker 命令与排障"
date: "2026-03-02"
tags: [codex-dialog]
source: codex-chat
status: draft
---

# OpenClaw Docker 命令与排障

## 结论

已在本机建立可用的 OpenClaw Docker 安全隔离环境。TUI 和后台页面可通过统一脚本入口正常访问；此前 `gateway token mismatch` 问题已定位并修复。

## 关键证据

- `./openclaw-docker.sh cli --help` 可正常返回命令列表，包含 `tui`、`dashboard`、`devices`。
- `./openclaw-docker.sh cli dashboard --no-open` 成功返回 Dashboard URL。
- `./openclaw-docker.sh cli devices list --json` 成功返回已配对设备，说明 CLI 与网关认证链路可用。
- 网关日志中 `token_mismatch` 与配置 token 不一致相关；同步后恢复。

## 结果与影响

- 后续使用 OpenClaw 时可以稳定通过 `~/openclaw-docker-safe/openclaw-docker.sh` 进入。
- 避免宿主机与容器状态混用导致的 token 不一致问题。
- 为 OpenAI Codex OAuth / 模型配置提供可复用运行环境。

## 下一步

1. 使用容器入口重新执行 Codex OAuth：`./openclaw-docker.sh cli models auth login --provider openai-codex`。
2. 完成授权后检查模型状态：`./openclaw-docker.sh cli models status`。
3. 若再次出现授权问题，优先查看：`./openclaw-docker.sh logs`。

## 背景

目标是在本机以 Docker 隔离方式运行 OpenClaw，并减少直接在宿主机运行带来的安全和状态污染风险。

## 问题与根因

`gateway connect failed: unauthorized: gateway token mismatch`。
根因是运行中的网关 token 与本地配置/环境中 token 不一致，导致 WebSocket 鉴权失败。

## 处理过程

- 创建并使用隔离目录：`~/openclaw-docker-safe`。
- 统一以封装脚本调用 CLI：`./openclaw-docker.sh cli ...`。
- 对齐 Docker `.env` 与 `state/config/openclaw.json` 中的网关 token。
- 重启网关后重新验证连接与设备列表。

## 方案对比与决策

- 方案 A：宿主机直接运行 `openclaw`
  - 优点：命令短。
  - 风险：容易和容器配置混用，导致 token/状态冲突。
- 方案 B：统一走 `openclaw-docker.sh`（最终采用）
  - 优点：入口统一、状态可控、排障路径清晰。

## 验证结果

- TUI 入口命令可执行：`./openclaw-docker.sh cli tui`。
- 后台 URL 可生成并访问：`./openclaw-docker.sh cli dashboard --no-open`。
- 设备列表可读：`./openclaw-docker.sh cli devices list --json`。

## 风险与注意事项

- 不要混用宿主机 `openclaw` 与容器 `openclaw` 配置。
- 网关 token 变更后要同步配置并重启服务。
- 如需批准浏览器设备，使用 `devices list/approve` 完成配对。

## 复盘要点

统一入口和单一状态源是避免 Docker 场景认证问题的关键。

## 关键命令
```bash
cd ~/openclaw-docker-safe

# 启动/状态
./openclaw-docker.sh start
./openclaw-docker.sh status

# 进入 TUI
./openclaw-docker.sh cli tui

# 后台页面（返回可访问 URL）
./openclaw-docker.sh cli dashboard --no-open

# 设备配对排障
./openclaw-docker.sh cli devices list
./openclaw-docker.sh cli devices approve <requestId>

# 模型与认证
./openclaw-docker.sh cli models status
./openclaw-docker.sh cli models auth login --provider openai-codex

# 日志与停止
./openclaw-docker.sh logs
./openclaw-docker.sh stop
```
