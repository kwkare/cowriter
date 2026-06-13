#!/usr/bin/env python3
"""
CoWriter – Start Script
========================
"""  # noqa
import os
import sys

os.curdir = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    import cowriter
    cowriter.main(sys.argv[1:])
