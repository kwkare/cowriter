#!/usr/bin/env python3
"""
CoWriter – Start Script
=======================
"""
import os
import sys

# Ensure UTF-8 encoding for console output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Also set env vars for child processes and Python's internal encoding
os.environ.setdefault("PYTHONUTF8", "1")

if __name__ == "__main__":
    import cowriter
    cowriter.main(sys.argv[1:])
