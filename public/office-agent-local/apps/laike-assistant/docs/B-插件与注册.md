# 来可助手 · 里程碑 B 验收：Cordis 办公插件（laike-tools）注册与冒烟（2026-09-06）

## 目标
把我们已开发的能力（来可浏览器控制/办公）做成 DSH 的 Cordis 插件并注册进来可助手的
web profile，实现"DSH 会话内直接调用来可能力"。

## 交付

### 插件 `apps/laike-assistant/plugins/laike-tools/`（Apache-2.0，自研）
| 文件 | 说明 |
|---|---|
| `package.json` | `dsh.bundle.patch=./cordis.patch.yml`；peerDeps 仅 @deepseek-ai/cordis + dsh-tools（第三方最小范式，同 dsh-find-plugin） |
| `cordis.patch.yml` | bundle 插入层：`insert {id: laike-tools, name: laike-tools}` |
| `lib/index.js` | `export name/inject['tools']/apply(ctx)`；注册模型工具 **`laike_browser`**：`open/snap/eval/act/shot` → 子进程调 dsh_bridge（CDP）驱动来可浏览器；路径经 `LAIKE_BRIDGE/LAIKE_PYTHON` 覆盖（随包运行时注入） |

### 注册（已生效）
- 安装：`plugins/laike-tools` → `profiles/web/node_modules/laike-tools`
  （与 dshmarket/dsh-find-plugin 同级，manual placement）
- 声明：`profiles/web/package.json` → `dependencies: {"laike-tools": "file:node_modules/laike-tools"}`
  + `dsh.profile.bundles` 追加 `laike-tools`
- 同步进 **template-home**（产品基线，新实例自带）

## 验证（本机 PASS）
1. `dsh --profile web --dump-config`（复刻 home）→ 组合树包含 `# == laike-tools` 层 ✓
2. 带插件实例启动（port 3096）：页面 200、日志无 laike-tools 相关错误 ✓
3. 工具实现与官方 dsh-find-plugin（主实例运行中）同一注册范式 ✓

### 会话级真调用（如实说明）
自动会话冒烟需要 GUI/RPC 驱动，本机自动化无公开通道直接向运行实例的 agent 发话——
该步留为**人工验收点**：在来可助手 DSH 界面（如 3096 实例）发"用 laike_browser 打开
http://127.0.0.1:3080 并读取页面标题"，观察模型调用 laike_browser 工具。

## 首启向导骨架（里程碑 A 遗留，已补）
`laike_runner.py setup --home <h> --api-key <key>` → 写 `.credentials.yaml`
`{version:1, refs:{DEEPSEEK_API_KEY: …}}`（实测假 key 写入/删除验证通过；无密钥入库）。

## 遗留/下一步
- laike-office（OCR/文档/知识库/公文，桥接 python core 或 office 服务）作为第二个工具集并入
- 会话冒烟人工验收后，插件 UI/Slot（可选）
- 产品化：env 注入（LAIKE_BRIDGE/LAIKE_PYTHON）由启动编排器完成

## 增补（2026-09-06 第3轮）：laike-office 能力 + E2E 尝试记录

### laike_doc 工具（office 读取能力已并入 laike-tools）
- helper/office_read.py：桥接 office-assistant core（readers/ocr），本地解析
  pdf/docx/xlsx/csv/txt/md + 图片 OCR，纯本地无网络；路径经 LAIKE_OFFICE_SRC 注入
- 实测三类型 PASS：txt(制度169字) / xlsx(表格md 252字) / 图片OCR(报销单53字,ocr:true)
- 插件现注册 2 个模型工具：laike_browser（浏览器控制）+ laike_doc（文件读取/OCR）
- 已同步 template-home（产品基线）

### E2E 会话冒烟尝试（真实记录）
- 自动驱动（laike_browser/CDP 开 3096 UI）定位到聊天输入框 textarea（placeholder
  "选择一个工作区开始"）成功；发现：①该实例 UI 处于引导态需先创建工作区；②React
  受控 textarea 用合成 input 事件赋值未生效（value 长度 0）——DSH Web 输入需原生
  CDP Input.insertText 键入或真实键盘，属 UI 自动化细节。
- 结论：会话级冒烟正式定为**人工验收**（投入产出比最优）：
  在来可助手 DSH 界面创建/打开工作区 → 发送
  "请使用 laike_browser 工具打开 http://127.0.0.1:3080/ 并读取页面标题，然后只回复页面标题"
  → 观察模型调用 laike_browser 工具并回复（laike_doc 同理可传本地文件路径测试）。
- 自动化探针脚本保留：apps/dsh-browser/tests/e2e_laike_smoke.py（后续接入
  CDP Input.insertText 后可复跑）。
## E2E 会话冒烟·自动尝试结论（第4-5轮）
自动驱动已打通：干净复刻实例(3097)→原生键入(63字 OK)→Enter→agent 开始推理。
阻塞点（外部 UI 引导，非产品缺陷）：DSH Web 首次运行需在界面完成
①Agent 预设选择（自动化已可点：创造模式面板→标准模式）②工作区创建/选择
（界面未暴露自动可点的创建入口，疑似原生目录选择器）。
人工验收按钮级路径：3097 复刻实例 → 选择工作区/创建 → 标准模式 → 输入
"请使用 laike_browser 工具打开 http://127.0.0.1:3080/ 并读取页面标题，然后只回复页面标题"
→ 观察工具调用（laike_browser 已注册）→ 回复页面标题即 PASS。
自动化探针保留：e2e_v2.py（键入/发送/轮询）、ws_bootstrap_r5.py 系列（预设选择已自动化）。
## 验收通过（2026-09-06，用户确认）
- 会话冒烟：来可助手 DSH（3085 实例，home=%LOCALAPPDATA%\LaikeAssistant\home）中发送
  任务"请使用 laike_browser 工具打开 http://127.0.0.1:3080/ 并读取页面标题"
- Agent 成功调用 laike_browser 读取并回复页面标题（DeepSeek Harness）-> PASS
- 里程碑 B 完整达成：laike-tools（laike_browser+laike_doc）注册进 web profile，
  dump-config/启动/真实会话调用全部验证通过
