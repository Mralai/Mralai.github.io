/**
 * laike-tools — Laike Assistant tool bundle for DSH (deepseek harness).
 *
 * Registers model-facing tools that drive the Laike Browser through the
 * dsh_bridge (CDP over WebSocket) plus office helpers. Bridge/python paths
 * are configurable via env LAIKE_BRIDGE / LAIKE_PYTHON (the bundled runtime
 * sets them); defaults fall back to the system python and the repo path.
 *
 * Plain ESM, no build step required.
 */
import { execFile } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'laike-tools'
export const inject = ['tools']

const HELPER = fileURLToPath(new URL('../helper/office_read.py', import.meta.url))

function bridgePath() {
  if (process.env.LAIKE_BRIDGE) return process.env.LAIKE_BRIDGE
  return 'dsh_bridge.py' // resolved via LAIKE_BRIDGE at runtime when bundled
}

function runPy(args, env, timeout = 120000) {
  return new Promise((resolve) => {
    const py = process.env.LAIKE_PYTHON || 'python'
    execFile(py, args, { timeout, windowsHide: true, maxBuffer: 16 * 1024 * 1024, env },
      (err, stdout, stderr) => {
        if (err) resolve('ERR: ' + String(stderr || err.message).slice(0, 1200))
        else resolve(String(stdout || '').trim().slice(0, 30000))
      })
  })
}

function runBridge(args, timeout = 90000) {
  const py = process.env.LAIKE_PYTHON || 'python'
  const b = bridgePath()
  return runPy([b, ...args], process.env, timeout)
}

function defTool(spec) {
  return defineTool({
    name: spec.name,
    description: spec.description,
    parameters: spec.parameters,
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: String(value) }],
    },
    execute: async (args) => {
      try {
        return await spec.run(args)
      } catch (e) {
        return '工具异常: ' + e.message
      }
    },
    timeoutMs: spec.timeoutMs || 120000,
  })
}

export function apply(ctx) {
  const port = (a) => String(a.port || 9222)
  ctx.tools.register(defTool({
    name: 'laike_browser',
    description: '控制来可浏览器（Thorium/CDP，经 dsh_bridge）：打开网址、读取页面文本快照、执行 JS、' +
      '执行动作序列(open/fill/click/extract/wait/eval)、截图保存。用于网页自动化与 DSH Web 操作。',
    parameters: {
      action: { type: 'string', required: true,
        description: '动作：open(打开 url) | snap(页面文本快照) | eval(执行 js 返回 JSON) | act(执行动作 JSON 数组) | shot(截图到 out)' },
      url: { type: 'string', description: 'open 动作的目标网址；shot 时为输出 PNG 路径' },
      js: { type: 'string', description: 'eval 动作的 JavaScript 表达式' },
      actions: { type: 'string', description: 'act 动作：JSON 数组字符串，元素 {type:navigate|wait|fill|click|extract|eval|screenshot, ...}' },
      port: { type: 'number', description: 'CDP 调试端口，默认 9222' },
    },
    run: async (a) => {
      const p = port(a)
      switch (a.action) {
        case 'open': return runBridge([p ? '--port' : '--port', p, 'open', '--url', a.url || ''])
        case 'snap': return runBridge(['--port', p, 'snap'])
        case 'eval': return runBridge(['--port', p, 'eval', '--js', a.js || ''])
        case 'act': return runBridge(['--port', p, 'act', '--actions', a.actions || '[]'])
        case 'shot': return runBridge(['--port', p, 'shot', '--out', a.url || 'laike_shot.png'])
        default: return '未知动作: ' + a.action + '（支持 open/snap/eval/act/shot）'
      }
    },
  }))
  ctx.tools.register(defTool({
    name: 'laike_doc',
    description: '读取本机办公文件并返回文本（本地解析/离线OCR，无网络）：支持 pdf/docx/xlsx/csv/txt/md' +
      ' 与图片(png/jpg/bmp/webp，自动 OCR)。用于文件解读、摘要、知识库引用。返回 JSON(ok/name/chars/text)。',
    parameters: {
      path: { type: 'string', required: true, description: '文件绝对路径' },
      max_chars: { type: 'number', description: '返回最大字符数，默认 12000' },
    },
    run: async (a) => {
      const env = Object.assign({}, process.env, { LAIKE_OFFICE_SRC: process.env.LAIKE_OFFICE_SRC || '' })
      return runPy([HELPER, a.path || '', String(a.max_chars || 12000)], env)
    },
  }))
}
