#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dsh_bridge 端到端自测：launch → health → navigate → fill → click → extract → quit。"""
import json
import os
import subprocess
import sys
import time

BRIDGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "tools", "dsh_bridge.py")
PORT = "9224"
DEMO = ("data:text/html,<html><body><input id='a'><button "
        "onclick=\"document.getElementById('r').textContent="
        "'OK-'+document.getElementById('a').value\">Go</button>"
        "<div id='r'></div></body></html>")


def run(*args):
    return subprocess.run([sys.executable, BRIDGE, "--port", PORT] + list(args),
                          capture_output=True, text=True, timeout=180)


def main():
    fails = []
    r = run("dsh", "--url", DEMO, "--bare")
    assert "ok" in r.stdout, r.stdout + r.stderr
    print("PASS launch:", json.loads(r.stdout)["browser"])
    time.sleep(1)

    r = run("health")
    assert "ok" in r.stdout, r.stderr
    print("PASS health:", json.loads(r.stdout)["browser"])

    r = run("act", "--actions", json.dumps([
        {"type": "navigate", "url": DEMO},
        {"type": "wait", "sec": 1},
        {"type": "fill", "selector": "#a", "value": "hello-dsh"},
        {"type": "click", "selector": "button"},
        {"type": "wait", "sec": 1},
        {"type": "extract", "selector": "#r", "key": "result"},
    ]))
    log = json.loads(r.stdout)["log"]
    vals = [x for x in log if "key" in x]
    print("PASS act log:", json.dumps(log, ensure_ascii=False)[:400])
    if not vals or vals[-1].get("value") != "OK-hello-dsh":
        fails.append("extract 结果不符: %s" % json.dumps(vals))

    r = run("eval", "--js", "document.getElementById('r').textContent")
    v = json.loads(r.stdout)["result"].get("value", "")
    print("PASS eval 复核:", v)
    if v != "OK-hello-dsh":
        fails.append("eval 复核不符: %s" % v)

    r = run("snap", "--maxlen", "200")
    snap = json.loads(r.stdout)
    print("PASS snap len:", snap["len"])
    if "hello-dsh" not in snap["text"]:
        fails.append("快照未含输入值")

    run("quit")
    print("RESULT:", "PASS" if not fails else "FAIL")
    if fails:
        for f in fails:
            print(" -", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
