#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dsh_bridge.py — DSH 专属浏览器控制桥（CDP over WebSocket）

让 DSH Agent 以“computer-use 风格”API 驱动 dsh-browser（Thorium 系）做一切网页自动化。
协议与 Chromium CDP 完全兼容，因此本桥对 本机 Chrome/Edge/Thorium 一视同仁。

能力（M0）：
  launch/dsh    启动受控浏览器（独立 profile + --remote-debugging-port + 默认 DSH URL）
  health        探测 /json/version
  open url      打开/跳转（新标签）
  list          列出标签页
  snap          当前页可读文本快照（document.body.innerText）
  eval  js      在当前页执行任意 JS 并返回 JSON 结果
  title/js      便捷查询
  act           按动作 JSON 列表执行：{type:navigate|click|fill|extract|wait|eval,…}
  quit          关闭全部标签（保留进程） / kill（结束进程）

用法：
  python dsh_bridge.py dsh --url http://127.0.0.1:3080 --port 9222
  python dsh_bridge.py open --url http://127.0.0.1:3080
  python dsh_bridge.py snap
  python dsh_bridge.py act --actions '[{"type":"click","selector":"#sendBtn"}]'

依赖：websocket-client（pip install websocket-client）；系统 python 3.8+。
浏览器发现顺序：环境 DSH_BROWSER → dsh-browser 安装的 thorium.exe → chrome.exe → msedge.exe。
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

try:
    import websocket  # websocket-client
except ImportError:  # pragma: no cover
    websocket = None

DEFAULT_PORT = 9222
# 默认主页：百度（产品定位：日常浏览器，进入干净快捷）。
# 需要 DSH Web 或其它地址时：dsh --url http://127.0.0.1:3080
DEFAULT_URL = "https://www.baidu.com"
_USER_DATA_HINT = "dsh-browser-profile"
# 静音参数：去首启向导/登录同步提示/崩溃恢复气泡/翻译条/默认浏览器弹窗等
_QUIET_FLAGS = [
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-infobars",
    "--disable-translate",
    "--disable-session-crashed-bubble",
    "--disable-features=TranslateUI,OptimizationHints,MediaRouter",
    "--no-service-autorun",
    "--disable-component-update",
]
_KNOWN = [
    # dsh-browser 自带 runtime（Thorium 便携，相对本文件 ../runtime/thorium-win/）
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                 "runtime", "thorium-win", "thorium.exe"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                 "runtime", "thorium-win", "Application", "thorium.exe"),
    r"%LOCALAPPDATA%\dsh-browser\thorium.exe",
    r"%LOCALAPPDATA%\Thorium\Application\thorium.exe",
    r"%PROGRAMFILES%\Thorium\Application\thorium.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
]


def _find_browser():
    ex = os.environ.get("DSH_BROWSER")
    if ex and os.path.exists(ex):
        return ex
    for p in _KNOWN:
        p = os.path.expandvars(p)
        if os.path.exists(p):
            return p
    return None


def _http_json(path, method="GET", body=None, port=DEFAULT_PORT, timeout=10):
    url = "http://127.0.0.1:%d%s" % (port, path)
    req = urllib.request.Request(url, method=method)
    if body is not None:
        req.data = json.dumps(body).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _ws_send(ws_url, method, params=None, timeout=30):
    if websocket is None:
        raise RuntimeError("缺少依赖 websocket-client，请先 pip install websocket-client")
    ws = websocket.create_connection(ws_url, timeout=timeout,
                                     enable_multithread=False)
    try:
        ws.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result")
    finally:
        try:
            ws.close()
        except Exception:
            pass


def _active_ws_url(port=DEFAULT_PORT):
    """取当前活动标签的 websocket 调试地址。"""
    tabs = _http_json("/json", port=port)
    if not tabs:
        raise RuntimeError("没有打开的标签页")
    for t in tabs:
        if t.get("type") == "page":
            return t["webSocketDebuggerUrl"]
    return tabs[0]["webSocketDebuggerUrl"]


# ---------------------------------------------------------------- CLI
def cmd_dsh(args):
    exe = _find_browser()
    if not exe:
        sys.exit("未找到可用的受控浏览器（Thorium/Chrome/Edge）。可用环境变量 DSH_BROWSER 指定。")
    # 不同内核不共用 profile（版本差异会导致数据损坏），profile 按浏览器名区分
    base = os.path.splitext(os.path.basename(exe))[0].lower()
    profile = os.path.join(os.path.expanduser("~"),
                           _USER_DATA_HINT + "-" + base)
    url = args.url or DEFAULT_URL
    flags = [
        exe,
        "--remote-debugging-port=%d" % args.port,
        "--remote-allow-origins=*",
        "--user-data-dir=" + profile,
    ] + _QUIET_FLAGS
    if args.kiosk:
        flags.append("--kiosk")
    elif not args.bare:
        flags += ["--app=" + url] if args.app_mode else [url]
    if not args.keep_console:
        creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    else:
        creation = 0
    proc = subprocess.Popen(flags, creationflags=creation)
    # 等待 CDP 就绪
    for _ in range(60):
        try:
            _http_json("/json/version", port=args.port)
            print(json.dumps({"ok": True, "pid": proc.pid,
                              "browser": os.path.basename(exe),
                              "url": url, "port": args.port}))
            return
        except Exception:
            time.sleep(0.5)
    sys.exit("启动超时：未能在 %d 端口发现 CDP 端点" % args.port)


def cmd_health(_args):
    v = _http_json("/json/version", port=_args.port)
    print(json.dumps({"ok": True, "browser": v.get("Browser"),
                      "protocol": v.get("Protocol-Version")}))


def cmd_open(args):
    _http_json("/json/new?" + urllib.parse.quote(args.url, safe=":/?&=%"),
               method="PUT", port=args.port)
    print(json.dumps({"ok": True, "url": args.url}))


def cmd_list(_args):
    tabs = _http_json("/json", port=_args.port)
    out = [{"id": t["id"], "title": t.get("title", ""),
            "url": t.get("url", "")} for t in tabs if t.get("type") == "page"]
    print(json.dumps({"ok": True, "tabs": out}))


def cmd_snap(args):
    r = _ws_send(_active_ws_url(args.port), "Runtime.evaluate",
                 {"expression": "document.body ? document.body.innerText : ''",
                  "returnByValue": True})
    text = (r or {}).get("result", {}).get("value", "") or ""
    print(json.dumps({"ok": True, "title": _ws_send(
        _active_ws_url(args.port), "Runtime.evaluate",
        {"expression": "document.title", "returnByValue": True})
        .get("result", {}).get("value", ""),
        "len": len(text), "text": text[: args.maxlen]}))


def cmd_shot(args):
    """截取当前页 PNG（Page.captureScreenshot → 文件）。"""
    import base64
    ws = _active_ws_url(args.port)
    r = _ws_send(ws, "Page.captureScreenshot",
                 {"format": "png", "captureBeyondViewport": False})
    data = (r or {}).get("data", "")
    if not data:
        sys.exit("截图失败：无数据")
    out = args.out
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(base64.b64decode(data))
    print(json.dumps({"ok": True, "file": out, "bytes": len(data) * 3 // 4}))


def cmd_eval(args):
    r = _ws_send(_active_ws_url(args.port), "Runtime.evaluate",
                 {"expression": args.js, "returnByValue": True,
                  "awaitPromise": True})
    print(json.dumps({"ok": True, "result": (r or {}).get("result")}))


def _js_quote(s):
    return json.dumps(str(s))


def cmd_act(args):
    actions = args.actions
    log = []
    ws = None
    try:
        for a in actions:
            t = a.get("type", "")
            if t == "navigate":
                _http_json("/json/new?" + urllib.parse.quote(a["url"], safe=":/?&=%"),
                           method="PUT", port=args.port)
                log.append({"ok": True, "msg": "open " + a["url"]})
            elif t == "wait":
                time.sleep(float(a.get("sec", 1)))
                log.append({"ok": True, "msg": "wait %.1fs" % float(a.get("sec", 1))})
            elif t in ("eval", "js"):
                ws = ws or _active_ws_url(args.port)
                r = _ws_send(ws, "Runtime.evaluate",
                             {"expression": a["js"], "returnByValue": True,
                              "awaitPromise": True})
                log.append({"ok": True, "msg": "eval",
                            "result": (r or {}).get("result")})
            elif t == "snap":
                ws = ws or _active_ws_url(args.port)
                r = _ws_send(ws, "Runtime.evaluate",
                             {"expression": "document.body?document.body.innerText:''",
                              "returnByValue": True})
                log.append({"ok": True, "text": ((r or {}).get("result") or {})
                            .get("value", "")[: a.get("maxlen", 800)]})
            elif t == "click":
                ws = ws or _active_ws_url(args.port)
                sel = a["selector"]
                _ws_send(ws, "Runtime.evaluate", {
                    "expression": "(function(){var el=document.querySelector(%s);"
                                  "if(!el)return 'NOT_FOUND';el.click();return 'OK';})()"
                                  % _js_quote(sel), "returnByValue": True})
                log.append({"ok": True, "msg": "click " + sel})
            elif t == "fill":
                ws = ws or _active_ws_url(args.port)
                sel, val = a["selector"], str(a.get("value", ""))
                r = _ws_send(ws, "Runtime.evaluate", {
                    "expression": "(function(){var el=document.querySelector(%s);"
                                  "if(!el)return 'NOT_FOUND';"
                                  "var set=Object.getOwnPropertyDescriptor("
                                  "window.HTMLInputElement.prototype,'value').set;"
                                  "set.call(el,%s);"
                                  "el.dispatchEvent(new Event('input',{bubbles:true}));"
                                  "el.dispatchEvent(new Event('change',{bubbles:true}));"
                                  "return 'OK';})()" % (_js_quote(sel), _js_quote(val)),
                    "returnByValue": True})
                log.append({"ok": True, "msg": "fill %s = %s (%s)"
                            % (sel, val[:40], (r or {}).get("result"))})
            elif t == "extract":
                ws = ws or _active_ws_url(args.port)
                sel = a["selector"]
                r = _ws_send(ws, "Runtime.evaluate", {
                    "expression": "(function(){var el=document.querySelector(%s);"
                                  "if(!el)return null;return (el.value!==undefined)?"
                                  "el.value:el.textContent;})()" % _js_quote(sel),
                    "returnByValue": True})
                log.append({"ok": True, "key": a.get("key", sel),
                            "value": (r or {}).get("result", {}).get("value")})
            elif t == "type":
                """原生键入：聚焦元素后 CDP Input.insertText（React 受控输入必需）。"""
                ws = ws or _active_ws_url(args.port)
                sel, text = a["selector"], str(a.get("text", ""))
                _ws_send(ws, "Runtime.evaluate", {
                    "expression": "(function(){var el=document.querySelector(%s);"
                                  "if(!el)return 'NOT_FOUND';el.focus();return 'OK';})()"
                                  % _js_quote(sel), "returnByValue": True})
                _ws_send(ws, "Input.insertText", {"text": text})
                log.append({"ok": True, "msg": "type %d chars into %s" % (len(text), sel)})
            elif t == "key":
                ws = ws or _active_ws_url(args.port)
                key = str(a.get("key", "Enter"))
                code = {"Enter": "Enter", "Tab": "Tab",
                        "Escape": "Escape"}.get(key, key)
                vk = 13 if key == "Enter" else (9 if key == "Tab"
                                                else 27 if key == "Escape" else 0)
                for kt in ("rawKeyDown", "keyUp"):
                    _ws_send(ws, "Input.dispatchKeyEvent",
                             {"type": kt, "key": key, "code": code,
                              "windowsVirtualKeyCode": vk,
                              "nativeVirtualKeyCode": vk})
                log.append({"ok": True, "msg": "key " + key})
            elif t in ("screenshot", "shot"):
                import base64 as _b64
                ws = ws or _active_ws_url(args.port)
                r = _ws_send(ws, "Page.captureScreenshot",
                             {"format": "png", "captureBeyondViewport": False})
                data = (r or {}).get("data", "")
                shots = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "workspace", "shots")
                os.makedirs(shots, exist_ok=True)
                fp = os.path.join(shots, "shot_%d.png" % int(time.time() * 1000))
                if data:
                    with open(fp, "wb") as f:
                        f.write(_b64.b64decode(data))
                log.append({"ok": bool(data), "msg": "screenshot", "file": fp
                            if data else None})
            else:
                log.append({"ok": False, "msg": "未知动作类型: " + str(t)})
    finally:
        try:
            if ws:
                websocket.create_connection  # noqa
        except Exception:
            pass
    print(json.dumps({"ok": True, "log": log}))


def cmd_quit(_args):
    try:
        tabs = _http_json("/json", port=_args.port)
        for t in tabs:
            if t.get("type") == "page":
                try:
                    _http_json("/json/close/" + t["id"], port=_args.port)
                except Exception:
                    pass
        print(json.dumps({"ok": True, "closed": len(tabs)}))
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))


def cmd_kill(args):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/IM", args.image or "thorium.exe"],
                       capture_output=True)
    print(json.dumps({"ok": True}))


def main():
    ap = argparse.ArgumentParser(description="DSH Browser 控制桥")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("dsh", help="启动受控浏览器并打开 DSH Web")
    p.add_argument("--url", default=None)
    p.add_argument("--kiosk", action="store_true")
    p.add_argument("--app-mode", dest="app_mode", action="store_true")
    p.add_argument("--bare", action="store_true")
    p.add_argument("--keep-console", action="store_true")
    p.set_defaults(fn=cmd_dsh)

    p = sub.add_parser("health"); p.set_defaults(fn=cmd_health)
    p = sub.add_parser("open"); p.add_argument("--url", required=True)
    p.set_defaults(fn=cmd_open)
    p = sub.add_parser("list"); p.set_defaults(fn=cmd_list)
    p = sub.add_parser("snap"); p.add_argument("--maxlen", type=int, default=4000)
    p.set_defaults(fn=cmd_snap)
    p = sub.add_parser("shot"); p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_shot)
    p = sub.add_parser("eval"); p.add_argument("--js", required=True)
    p.set_defaults(fn=cmd_eval)
    p = sub.add_parser("act"); p.add_argument("--actions", required=True)
    p.set_defaults(fn=cmd_act)
    p = sub.add_parser("quit"); p.set_defaults(fn=cmd_quit)
    p = sub.add_parser("kill"); p.add_argument("--image", default="thorium.exe")
    p.set_defaults(fn=cmd_kill)

    args = ap.parse_args()
    if args.cmd == "act":
        try:
            args.actions = json.loads(args.actions)
        except Exception as e:
            sys.exit("actions 不是合法 JSON: %s" % e)
    args.fn(args)


if __name__ == "__main__":
    main()
