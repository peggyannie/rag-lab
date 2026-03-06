# OpenClaw Gateway 与核心能力说明（2026-03-02）

## 结论
OpenClaw 的 Gateway 是整个系统的中控层：统一接入、鉴权与配对、会话状态、请求调度都由它负责。前端界面（TUI/Dashboard）和渠道接入都依赖 Gateway 才能工作。

## 关键证据
- 控制台、CLI、渠道连接都走 Gateway（常见为 `ws://127.0.0.1:18789`）。
- 出现 `pairing required`、`gateway token mismatch` 一类报错时，根因通常在 Gateway 的鉴权/配对层。
- 模型请求并非界面直连，而是由 Gateway 统一转发到 provider。

## 结果与影响
- 理解 Gateway 后，排障会更快：先看网关连通性、鉴权、配对、日志，而不是先怀疑模型本身。
- 日常运维应优先使用 `status / logs / health / devices` 这组命令判断问题层级。

## 背景
用户希望了解 OpenClaw 的 Gateway 本质，以及 OpenClaw 的核心能力和主要工具模块。

## 核心能力
1. 统一入口
   TUI、Dashboard、CLI、渠道机器人都通过 Gateway 接入。
2. 多模型路由与回退
   支持默认模型、fallback 模型、provider 级鉴权（OAuth/API Key）。
3. Agent 回合执行
   支持“消息 -> 工具调用 -> 结果回传”的完整回合，并维持上下文。
4. 多渠道集成
   支持 Discord/Telegram 等渠道，含 DM/群组策略。
5. 安全控制
   包括 token 鉴权、设备配对、命令审批、策略限制。
6. 可观测与运维
   提供状态、健康检查、日志、诊断与安全审计能力。

## 主要工具/模块
1. `gateway`
   网关本体，负责 WebSocket 服务、鉴权和转发。
2. `models`
   模型发现、配置、探测、切换默认/回退。
3. `devices` / `pairing`
   设备配对与授权管理。
4. `channels` / `message` / `directory`
   渠道登录、消息收发、联系人/群组 ID 查询。
5. `tui` / `dashboard`
   终端界面与网页控制台入口。
6. `approvals`
   高风险操作审批。
7. `memory` / `sessions`
   记忆索引与会话状态管理。
8. `sandbox` / `node` / `nodes`
   隔离执行环境与节点能力。
9. `hooks` / `plugins`
   扩展机制。
10. `doctor` / `security` / `logs` / `status`
    诊断、审计、日志、运行态总览。

## 下一步
1. 需要排障时，先执行 `openclaw status` 与 `openclaw logs --follow`。
2. 看到 `pairing required` 时，先执行 `openclaw devices list`，再 `openclaw devices approve --latest`。
3. 模型异常时，再进入 `openclaw models status --probe` 做 provider 级验证。
