#!/usr/bin/env python3
"""Convert Qt .ts translation files to JSON for DictTranslator."""
import json, sys
from pathlib import Path
from xml.etree import ElementTree as ET

def parse_ts(ts_path):
    tree = ET.parse(ts_path)
    root = tree.getroot()
    translations = {}
    for ctx_elem in root.findall("context"):
        ctx_name = ctx_elem.findtext("name") or ""
        if not ctx_name: continue
        ctx_dict = {}
        for msg_elem in ctx_elem.findall("message"):
            src_elem = msg_elem.find("source")
            trans_elem = msg_elem.find("translation")
            if src_elem is not None and src_elem.text:
                src = src_elem.text
                trans = trans_elem.text if trans_elem is not None and trans_elem.text else ""
                if trans and trans != src:
                    ctx_dict[src] = trans
        if ctx_dict:
            translations[ctx_name] = ctx_dict
    return translations

def main():
    repo = Path(__file__).resolve().parents[1]
    src_dir = repo / "i18n"
    dst_dir = repo / "cowriter" / "assets" / "i18n"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for ts_file in sorted(src_dir.glob("nw_*.ts")):
        if ts_file.name == "nw_base.ts": continue
        trans = parse_ts(ts_file)
        if not trans: continue
        total = sum(len(v) for v in trans.values())
        json_file = dst_dir / ts_file.name.replace(".ts", ".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(trans, f, ensure_ascii=False, indent=2)
        print(f"  {ts_file.name} -> {json_file.name} ({total})")

if __name__ == "__main__":
    main()
