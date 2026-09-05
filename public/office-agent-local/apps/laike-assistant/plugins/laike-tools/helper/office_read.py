#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""office_read.py - laike-office helper: read a local office/text/image file and
return plain text (JSON). Reuses office-assistant core (readers/ocr). The core
source root is injected via env LAIKE_OFFICE_SRC (appended to sys.path); the
bundled runtime sets it. ASCII/UTF-8 output, no network.
Usage: office_read.py <path> [max_chars]
"""
import json
import os
import sys

SRC = os.environ.get("LAIKE_OFFICE_SRC", "")
if SRC:
    sys.path.insert(0, SRC)

from core import readers  # noqa: E402
from core import ocr  # noqa: E402


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
    if not path or not os.path.exists(path):
        print(json.dumps({"ok": False, "error": "file not found: " + path}))
        return 1
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext in ocr.IMG_EXTS:
            doc = ocr.OcrEngine().extract_to_doc(path, {"max_doc_chars": cap})
        else:
            doc = readers.read_document(path, {"max_doc_chars": cap,
                                               "max_table_rows": 3000})
        text = (doc or {}).get("text", "")[:cap]
        print(json.dumps({"ok": True,
                          "name": os.path.basename(path),
                          "chars": len(text),
                          "ocr": bool((doc or {}).get("extra", {}).get("ocr")),
                          "text": text}, ensure_ascii=False))
        return 0
    except readers.ReadError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": "read failed: %s" % e}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
