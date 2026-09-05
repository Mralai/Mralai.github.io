# 来可助手 · C 里程碑：安卓手机版（Laike Assistant Mobile）

> 目标：手机（同局域网/远程）使用来可助手——即 PC 端本地 DSH（含 laike-tools 插件）从手机可达。
> 官方安全边界：`dsh web` **刻意不支持 `--host 0.0.0.0`**（防远程 RCE），只监听回环。
> 因此手机版 = 「PC 安全局域网模式 + 手机端入口」组合，不牺牲安全模型。

## 1. 架构（手机版）

```
手机浏览器/壳 (同一 Wi-Fi)
   │  http://<PC-局域网IP>:<lanPort>
   ▼
netsh portproxy（LAN 口 → 127.0.0.1）   ← 需管理员；laike_runner serve 自动管理
   ▼
dsh web（仅回环 127.0.0.1:dshPort，--trusted-host 含 LAN 页面 authority）
   └─ web profile 全插件栈 + laike-tools（laike_browser / laike_doc）
```

## 2. 已交付并验证（2026-09-06）

`pkg/laike_runner.py serve --home <home> --port 3088 --listen-port 3089`
- dsh 起于回环 3088（官方安全模型），netsh 转发 LAN:3089 → 127.0.0.1:3088，
  dsh 加 `--trusted-host 127.0.0.1:3088 --trusted-host <LAN-IP>:3089`
- 实测：`http://192.168.110.122:3089/` → 200（313KB）；LAN 地址手机同网即可访问
- `stop` 自动删除 portproxy 并终止 dsh（验证 netsh 表清空）
- 安全提示输出：仅可信网络使用；防火墙需放行 LAN 端口（按需）

## 3. 手机端入口（路线）

| 方案 | 说明 | 状态 |
|---|---|---|
| A. 手机浏览器直访 | 手机浏览器打开 `http://<PC-IP>:<lanPort>`（可存书签） | ✅ 已可用 |
| B. PWA/启动页（推荐首版） | 来可助手手机首页（记录地址/连接状态/一键跳 DSH；品牌图标）→ “添加到主屏幕” | 开发中（后续轮） |
| C. 原生壳 APK | Capacitor 壳内嵌 DSH WebView 或内置 B 启动页 → APK；本机无 Android SDK → 提供 CI（GitHub Actions）云构建 | 后续轮 |

## 4. 安全与限制（如实）

- dsh 是 Agent/工具运行面：**仅在本机可信任的局域网启用 serve**；公共 Wi-Fi/互联网不要开；
  需要跨网时用 VPN/SSH 隧道而非直放端口。
- netsh 需要管理员权限（serve 失败时给出手动命令提示）。
- 手机浏览器体验 = DSH Web 原生界面；桌面专属能力（浏览器自动化等）仍需 PC 端运行。

## 5. 验收点（手机在手上时）

1. PC：`laike_runner serve --home %LOCALAPPDATA%\LaikeAssistant\home --port 3085 --listen-port 3086`
2. 手机（同一 Wi-Fi）浏览器打开输出的 `lan_url` → 应看到 DSH 登录/工作区界面
3. 建工作区/标准模式 → 发送“请使用 laike_doc 读取本地文件”类任务验证 laike-tools
4. 回报结果；PC 端 `laike_runner stop` 清理

## 增补：手机启动页（PWA）已交付（2026-09-06 第1轮）
- mobile/web/：来可助手手机入口页（品牌图标/地址记忆/连接检测/一键打开 DSH）+ manifest+PWA 图标
- serve 支持 --page --page-port：额外在局域网起静态启动页（无代码执行，安全）
- 实测：page LAN 200、manifest 200；stop 自动清理 page/转发/进程
- 手机使用：打开 page_url → 填 lan_url（记忆）→ 连接 → 添加到主屏幕（PWA）
