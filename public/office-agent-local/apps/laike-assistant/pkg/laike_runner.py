#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""laike_runner.py - Laike Assistant (Windows) launcher/orchestrator for the
bundled DeepSeek Harness instance (milestone A).

Commands:
  init-home  --home <dir> [--port 3085]   create a fresh DSH home from template
  start      --home <dir> [--port 3085]   boot dsh web for that home
  status     --home <dir> [--port 3085]   is it up?
  stop       --home <dir> [--port 3085]   stop the instance for that home/port
  open       --url <url>                  open url in Laike Browser (via dsh_bridge)
ASCII-only source to survive PS5.1 ANSI parsing of .ps1 wrappers; this is .py.
"""
import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(os.path.join(HERE, ".."))
BRIDGE = os.path.join(APP, "..", "dsh-browser", "tools", "dsh_bridge.py")
TEMPLATE = os.path.join(APP, "runtime", "template-home")
DEFAULT_HOME = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                            "LaikeAssistant", "home")
DEFAULT_PORT = 3085


def _ping(port, timeout=3):
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def _pidfile(home):
    return os.path.join(home, "laike-web.pid")


def _copy_tree(src, dst):
    if os.name == "nt" and shutil.which("robocopy"):
        r = subprocess.run(["robocopy", src, dst, "/E", "/MT:16",
                            "/NFL", "/NDL", "/NJH", "/NP", "/R:1"],
                           capture_output=True, timeout=1800)
        return r.returncode < 8
    shutil.copytree(src, dst)
    return True


def cmd_init(args):
    home = args.home or DEFAULT_HOME
    if os.path.exists(os.path.join(home, "settings.yaml")):
        print(json.dumps({"ok": True, "existing": True, "home": home}))
        return
    if not os.path.isdir(TEMPLATE):
        sys.exit("template-home missing at " + TEMPLATE)
    os.makedirs(home, exist_ok=True)
    if not _copy_tree(TEMPLATE, home):
        sys.exit("copy template failed")
    print(json.dumps({"ok": True, "home": home, "size_mb": round(
        sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(home)
            for f in fs) / 1e6, 1)}))


def _start_proc(home, port):
    log = os.path.join(home, "logs", "laike-web.log")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    env = dict(os.environ)
    env["DSH_HOME"] = home
    cmd = "dsh web --port %d --no-open 2>&1 | Tee-Object -FilePath '%s'" % (port, log)
    p = subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd],
                         env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    with open(_pidfile(home), "w") as f:
        f.write(str(p.pid))
    return p


def cmd_start(args):
    home = args.home or DEFAULT_HOME
    port = args.port or DEFAULT_PORT
    if not os.path.exists(os.path.join(home, "settings.yaml")):
        cmd_init(args)
    if _ping(port):
        print(json.dumps({"ok": True, "already": True, "url": "http://127.0.0.1:%d" % port}))
        return
    p = _start_proc(home, port)
    ok = False
    for _ in range(120):
        time.sleep(1)
        if _ping(port):
            ok = True
            break
    print(json.dumps({"ok": ok, "pid": p.pid, "port": port,
                      "url": "http://127.0.0.1:%d" % port, "home": home}))


def cmd_status(args):
    port = args.port or DEFAULT_PORT
    print(json.dumps({"ok": _ping(port), "port": port}))


def cmd_stop(args):
    home = args.home or DEFAULT_HOME
    _proxy_cleanup(home)   # remove the LAN portproxy when serve was used
    # kill the static launcher page if serve started one
    pf = _pagefile(home)
    if os.path.exists(pf):
        try:
            pid = int(open(pf).read().strip())
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        os.remove(pf)
    port = args.port or DEFAULT_PORT
    killed = []
    if os.path.exists(_pidfile(home)):
        try:
            pid = int(open(_pidfile(home)).read().strip())
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except Exception:
            pass
    # also kill the node listening on the port
    if os.name == "nt":
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-NetTCPConnection -LocalPort %d -State Listen).OwningProcess" % port],
                           capture_output=True, text=True, timeout=20)
        for line in r.stdout.split():
            try:
                subprocess.run(["taskkill", "/F", "/PID", line.strip()],
                               capture_output=True, timeout=20)
                killed.append(int(line.strip()))
            except Exception:
                pass
    print(json.dumps({"ok": True, "killed": killed}))


def cmd_open(args):
    url = args.url or "http://127.0.0.1:%d" % (args.port or DEFAULT_PORT)
    py = sys.executable
    if not os.path.exists(BRIDGE):
        print(json.dumps({"ok": False, "error": "bridge missing " + BRIDGE}))
        return
    p = subprocess.Popen([py, BRIDGE, "--port", "9222", "dsh", "--url", url, "--app-mode"],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    print(json.dumps({"ok": True, "pid": p.pid, "url": url}))


def cmd_setup(args):
    """First-run wizard (skeleton): collect DEEPSEEK_API_KEY and write
    .credentials.yaml in the home; optional port reminder. No key stored in repo."""
    home = args.home or DEFAULT_HOME
    if not os.path.exists(os.path.join(home, "settings.yaml")):
        cmd_init(args)
    cred = os.path.join(home, ".credentials.yaml")
    key = args.api_key or os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        print(json.dumps({"ok": False, "error": "no api key",
                          "hint": "pass --api-key or set DEEPSEEK_API_KEY"}))
        return
    with open(cred, "w", encoding="utf-8") as f:
        f.write("version: 1\nrefs: { DEEPSEEK_API_KEY: %s }\n" % key)
    print(json.dumps({"ok": True, "cred": cred,
                      "note": "wizard done; start with --port e.g. 3085"}))


def _lan_ip():
    """Best-effort LAN IPv4 address for phone access hints."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def _netsh_proxy(listen, listen_port, target_port, add=True):
    """Manage a v4tov4 portproxy (LAN listen -> 127.0.0.1 target). Needs admin."""
    op = "add" if add else "delete"
    args = ["netsh", "interface", "portproxy", op, "v4tov4",
            "listenaddress=%s" % listen, "listenport=%d" % listen_port]
    if add:
        args += ["connectaddress=127.0.0.1", "connectport=%d" % target_port]
    r = subprocess.run(args, capture_output=True, text=True, timeout=30)
    return r.returncode == 0, r.stderr.strip()[:200]


def _proxyfile(home):
    return os.path.join(home, "laike-serve-proxy.txt")


def _pagefile(home):
    return os.path.join(home, "laike-mobile-page.pid")


def _start_page(home, page_port):
    """Static launcher page for the phone (no code execution: safe to bind LAN)."""
    mobile = os.path.join(APP, "mobile", "web")
    if not os.path.isdir(mobile):
        return None, "mobile/web missing at " + mobile
    p = subprocess.Popen([sys.executable, "-m", "http.server", str(page_port),
                          "--bind", "0.0.0.0", "--directory", mobile],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    with open(_pagefile(home), "w") as f:
        f.write(str(p.pid))
    return p.pid, None


def cmd_serve(args):
    """Safe LAN mode for the phone client. dsh itself stays on 127.0.0.1
    (the product refuses 0.0.0.0 on purpose: RCE protection). We expose a
    netsh portproxy from the LAN address to the loopback port and trust the
    LAN page authority. Needs Administrator for netsh; only run on a trusted
    network. Cleanup happens on stop."""
    home = args.home or DEFAULT_HOME
    port = args.port or DEFAULT_PORT      # dsh loopback port
    lan = _lan_ip() or "127.0.0.1"
    listen_port = int(args.listen_port or 0) or (port + 1)
    if not os.path.exists(os.path.join(home, "settings.yaml")):
        cmd_init(args)
    if _ping(port):
        print(json.dumps({"ok": True, "already": True,
                          "local_url": "http://127.0.0.1:%d" % port}))
        return
    log = os.path.join(home, "logs", "laike-web.log")
    os.makedirs(os.path.dirname(log), exist_ok=True)
    env = dict(os.environ)
    env["DSH_HOME"] = home
    cmd = ("dsh web --port %d --no-open --trusted-host 127.0.0.1:%d "
           "--trusted-host %s:%d 2>&1 | Tee-Object -FilePath '%s'"
           % (port, port, lan, listen_port, log))
    p = subprocess.Popen(["powershell", "-NoProfile", "-Command", cmd],
                         env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    with open(_pidfile(home), "w") as f:
        f.write(str(p.pid))
    ok = False
    for _ in range(120):
        time.sleep(1)
        if _ping(port):
            ok = True
            break
    px_ok, px_err = _netsh_proxy(lan, listen_port, port, add=True)
    with open(_proxyfile(home), "w") as f:
        f.write("%s %d\n" % (lan, listen_port))
    page_pid = None
    page_url = None
    if args.page:
        page_port = int(args.page_port or 0) or (listen_port + 1)
        page_pid, perr = _start_page(home, page_port)
        if page_pid:
            page_url = "http://%s:%d" % (lan, page_port)
    print(json.dumps({"ok": ok, "pid": p.pid, "dsh_port": port,
                      "lan_url": "http://%s:%d" % (lan, listen_port),
                      "page_url": page_url, "page_pid": page_pid,
                      "proxy_ok": px_ok, "proxy_err": px_err,
                      "local_url": "http://127.0.0.1:%d" % port,
                      "hint": "phone on same Wi-Fi -> open the lan_url; "
                              "stop cleans the portproxy; needs admin for netsh"}))


def _proxy_cleanup(home):
    pf = _proxyfile(home)
    if os.path.exists(pf):
        try:
            lan, lp = open(pf).read().split()
            _netsh_proxy(lan, int(lp), 0, add=False)
        except Exception:
            pass
        os.remove(pf)


def main():
    ap = argparse.ArgumentParser(description="Laike Assistant DSH runner")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init-home", "start", "status", "stop", "open", "setup", "serve"):
        p = sub.add_parser(name)
        p.add_argument("--home", default=None)
        p.add_argument("--port", type=int, default=None)
        p.add_argument("--url", default=None)
        p.add_argument("--api-key", default=None)
        p.add_argument("--listen-port", type=int, default=None)
        p.add_argument("--page", action="store_true",
                       help="also serve the phone launcher page on the LAN")
        p.add_argument("--page-port", type=int, default=None)
        p.set_defaults(fn={"init-home": cmd_init, "start": cmd_start,
                           "status": cmd_status, "stop": cmd_stop,
                           "open": cmd_open, "setup": cmd_setup,
                           "serve": cmd_serve}[name])
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
