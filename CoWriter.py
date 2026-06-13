#!/usr/bin/env python3
"""
CoWriter – Start Script
=======================
"""  # noqa
import os
import sys

# Fix console encoding for Windows (runs before everything else)
if sys.platform == "win32" and sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        os.environ["PYTHONIOENCODING"] = "utf-8"

os.curdir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    import cowriter
    cowriter.main(sys.argv[1:])
