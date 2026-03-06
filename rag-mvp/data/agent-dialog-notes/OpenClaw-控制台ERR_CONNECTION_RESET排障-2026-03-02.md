

## 背景
在本机 Docker 环境访问 OpenClaw 控制台时，浏览器报错：`ERR_CONNECTION_RESET`，页面提示“无法访问此网站 / 连接已重置”。

## 结论
问题已恢复。网关服务实际可用，控制台可正常访问；建议统一通过 `openclaw-docker.sh cli dashboard --no-open` 获取当次带 token 的访问链接，避免旧链接或协议错误导致误判。

## 问题与根因
- 现象层面：浏览器连接被重置，用户侧看到 `ERR_CONNECTION_RESET`。
- 根因层面（本次定位结果）：
  - 访问方式与网关状态不一致（旧地址/旧 token/错误协议）时，容易表现为连接异常或鉴权失败。
  - 排障后确认网关端口服务正常，`127.0.0.1:18789` 已可稳定返回 `HTTP 200`。

## 处理过程
1. 检查容器状态与端口映射，确认 `openclaw-src-openclaw-gateway-1` 处于 `Up`。
2. 查看网关日志，确认网关已监听 `ws://0.0.0.0:18789`。
3. 使用 `curl` 直连本机端口验证 HTTP 返回。
4. 通过 `dashboard --no-open` 重新生成控制台 URL（含 `#token=...`）。
5. 按新 URL 访问后恢复正常。

## 关键证据
- `curl http://127.0.0.1:18789/` 返回：`HTTP/1.1 200 OK`。
- 网关日志显示：`listening on ws://0.0.0.0:18789`。
- `dashboard --no-open` 可输出可访问的 Dashboard URL（带 token）。

## 验证结果
- 控制台页面可打开。
- 用户确认“现在可以了”。

## 结果与影响
- OpenClaw Docker 控制台恢复可用。
- 后续进入控制台的标准入口明确，减少再次出现“连接重置/鉴权不匹配”类问题的概率。

## 风险与注意事项
- 需使用 `http://` 而不是 `https://` 访问 `127.0.0.1:18789`。
- 不建议复用历史书签中的旧 token 链接。
- 网关重启后，建议重新执行 dashboard 命令获取最新地址。

## 关键命令
```bash
cd ~/openclaw-docker-safe
./openclaw-docker.sh start
./openclaw-docker.sh cli dashboard --no-open
```

```bash
curl -sv --max-time 5 http://127.0.0.1:18789/ -o /dev/null
docker logs --tail 120 openclaw-src-openclaw-gateway-1
```

## 下一步
1. 将 `dashboard --no-open` 的输出链接作为唯一控制台入口来源。
2. 若再次异常，先执行“关键命令”中的 `curl + logs` 两条进行快速判定。

## 补充更新（pairing required）
### 现象
- 控制台页面可打开，但右上角提示 `pairing required`，聊天区显示“已断开与网关的连接”。

### 根因
- 网关启用了设备配对控制，当前浏览器设备未被授权（或旧配对码已过期），WebSocket 被以 `1008 pairing required` 拒绝。

### 处理与结果
1. 查看设备状态，发现有新的 `Pending` 配对请求。
2. 执行最新请求批准后恢复连接。
3. 日志出现 `device pairing approved` 与 `webchat connected`，控制台恢复正常。

### 对应命令
```bash
cd ~/openclaw-docker-safe
./openclaw-docker.sh cli devices list
./openclaw-docker.sh cli devices approve --latest
```

### 备注
- 之前的 `openclaw pairing approve discord 5T3VB2SE` 失败是因为该 code 已无待处理请求（已过期/已失效）。
- 后续再遇到同类问题，优先用 `devices list + devices approve --latest`。
