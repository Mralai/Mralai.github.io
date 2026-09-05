# 来可浏览器（Laike Browser）— Thorium 二次开发基底

> 根品牌：**来可（Laike）**（命名规范见库级 docs/14，规则=来可+属性后缀）。
> 上游开源项目：**Thorium**（Chromium fork，BSD-3-Clause，`github.com/Alex313031/Thorium`，
> 活跃版本 M152；主仓库为源码+Linux 构建，Windows/Android/macOS 构建分布在姊妹仓库，
> 见上游 README 顶部链接）。
>
> 定位：轻量、快速、干净体验的日常浏览器（**Windows/安卓启动直达百度主页，无登录与
> 条款弹窗、无首启向导**），同时全量保留 DevTools 自动化通道，可由 DSH Agent 驱动
> 完成网页自动化（CDP over WS，`dsh_bridge`）；默认主页可用 `--url` 切换为 DSH Web。
> *"轻量/最快"指相对完整 Chromium 去冗余后的体验目标；渲染内核为 Chromium 系，是承载
> 现代 SPA 与 CDP 自动化的最低前提，非 NetSurf 级旧内核。品牌资源见 `branding/`。

## 命名

- 产品名：**来可浏览器**（应用/发行显示名）；根品牌"来可"，生态见 docs/14。
- 英文（涉外）：避免直接使用 Laike 全拼（与 LAIKA / Laike-HK 冲突），见 docs/14 §3。
- 上游目录与内部代号 dsh-browser / thorium 保留用于工程与文件路径。

## 为什么是 Chromium 系（选型约束）

| 需求 | 约束 | 结论 |
|---|---|---|
| 作为 DSH Web GUI 宿主 | 现代 React SPA | 必须现代渲染内核 |
| DSH 自动化一切 | Chrome DevTools Protocol（DSH 生态/CDP 已成熟） | 必须 CDP 可达 |
| 电脑 + 安卓双端 | 双端同内核、体验一致 | Chromium 系双端覆盖 |
| 轻量/快/可二开 | 去掉冗余、深度定制 | 选开源精简 fork：**Thorium**（BSD-3，商用友好，性能导向） |

## 目录（已拉取）

```
apps/dsh-browser/thorium/     ← 上游 Thorium 源码+补丁+构建脚本（main，0.4GB 仓库，不入库）
apps/dsh-browser/runtime/     ← 运行时基座（不入库）：thorium-win/（M152 AVX2 便携）、
                                android/（arm64 APK，M2 用）
apps/dsh-browser/README.md    ← 本文件（二开设计）
apps/dsh-browser/NOTICE.txt   ← 上游 BSD-3 与第三方声明
apps/dsh-browser/docs/        ← M1 基座验证记录（新）
apps/dsh-browser/tools/       ← DSH 绑定层：dsh_bridge.py（CDP 控制桥）、start_dsh.bat
apps/dsh-browser/tests/       ← test_bridge.py（端到端，已 PASS）
```

Thorium 仓库是"全量 Chromium 源码树(经 gclient) + Thorium 覆盖补丁"的构建型仓库：
`build.sh / build_win.sh / build_android.sh / build_mac.sh`、`depot_tools/`、`src/`(补丁覆盖)、
`thorium_shell/`、`arm/`(Android) 等。二次开发 = 改 branding/默认行为 + 加 DSH 绑定模块，
然后用其构建脚本出包（构建需高配机器/CI，见 §6）。

## 里程碑进度

- M0（完成）：拉取上游基底 + 二开设计 + DSH 控制桥（CDP）原型；桥经本机 Chrome 验证。
- M1（完成）：接入 Windows Thorium M152 AVX2 便携基座（runtime/thorium-win），
  桥对 **Thorium 本体** 端到端验证 PASS（打开 DSH Web / 填表 / 点击 / 取值 / 截图），
  见 `docs/M1-基座与自动化验证.md`。
- M2（完成）：Android 路线——Public/Shell arm64 APK 归档 + 受控模式三路径与验收清单，
  见 `docs/M2-Android路线.md`（真机/自编译验证需设备与 SDK 环境）。
- M2.5（完成）：发行裁剪实验 `packaging/trim_lite.ps1`——语言包裁剪
  714MB→666MB（-48MB），裁剪版启动冒烟 PASS；其余体积为 Chromium 内核刚需。
- M2.6（完成）：默认主页迭代——Windows 默认直达百度（`--app-mode` 干净单窗）、静音
  参数集（去首启向导/登录同步/崩溃恢复气泡/翻译等弹窗）；实测百度主页无登录/条款弹层；
  安卓见 docs/M2（官方 APK 手动设主页，自编译版将固化启动页）。
- M3：品牌/默认参数壳发布（双版本、商店素材、隐私页）。

## 深度捆绑 DSH（二开核心模块）

1. **启动即 DSH**：默认首页/新标签 = DSH Web URL（`http://127.0.0.1:3080`，可配置）；
   独立品牌名与图标（"DSH Browser"），无杂项；极简 UI（kiosk/紧凑模式开关）。
2. **自动化通道（对 DSH 全开）**：
   - 启动参数固化：`--remote-debugging-port=9222 --remote-allow-origins=* --no-first-run` 等
     （桌面 Chromium 系通用；可安全裁剪默认关闭，由 DSH 控制桥按需拉起）；
   - profile 独立（不污染用户 Chrome/Edge），自动清理策略；
   - 桌面控制桥 `tools/dsh_bridge`：启动/关闭/取页面快照/执行动作/上报状态
     （HTTP/WS → CDP 语义，DSH computer-use 风格 API，供 Agent 调用）。
3. **身份与安全**：只连本机回环与用户显式授权地址；自带 DSH 会话白名单；
   提供 `--dsh-url` 覆盖与 `--no-cdp` 关闭模式。
4. **移动端**：Android 版内置"DSH 面板"书签/快捷入口 + 受控 CDP（局域网/ADB 转发），
   便于 DSH 在手机浏览器上执行自动化（借鉴开源 termux-browser-pilot 的 CDP+MCP 做法）。

## 控制面参考（开源，可并入）

- `termux-browser-pilot`（salviz）：Android/Termux 下 Firefox/Chromium + CDP + MCP server ——
  我们的 Android 受控模式可直接借鉴其 MCP→CDP 桥。
- `bwb-browser-termux`：极简 CDP 自动化 MCP server 思路。

## 构建与打包路线

| 目标 | 途径 | 备注 |
|---|---|---|
| Windows x64（本机已跑通） | 上游 M152 便携基座（runtime/thorium-win）+ 桥/启动器（DSH 深绑） | M1 完成；后续：品牌化/精简语言包 |
| Linux/macOS | 上游构建脚本/二进制 | CI 或高配机 |
| Android APK | 下载 Public/Shell arm64 APK（runtime/android）→ 安装/注入式发行；自编译走 `build_android.sh` | M2 文档化；受控模式见 docs |
| DSH 控制桥 | 本仓库自研（纯 CDP over WS），桥已打通 Thorium | 发行时可将桥打成小 exe |

## 里程碑

- M0（完成）：拉取上游基底 + 本设计文档 + 控制桥原型骨架。
- M1（完成）：Windows 基座接入 + Thorium 本体端到端验证（见 docs/M1）。
- M2：Android APK 路线 + 手机受控模式（CDP over ADB reverse / 局域网）。
- M3：商店发行素材/隐私页/双版本（沿用库内 office-assistant 合规套路）。

## 许可与合规

- 上游 Thorium：BSD-3-Clause（商业可用，保留版权声明与 LICENSE）。
- Chromium 上游：BSD-3-Clause；第三方组件许可按 Chromium 通知机制随包（NOTICE）。
- 复用 DSH 仅为界面宿主与自动化目标，不修改 DSH 本体；对外发行不冒充官方。
