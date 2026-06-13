"""
CoWriter — Chinese Spell Check
===============================
Lightweight Chinese text checker for common errors (错别字/笔误).

Does NOT require jieba or any external dependency.
Uses character-level pattern matching for common Chinese writing errors.
"""
from __future__ import annotations

import re
import logging
from typing import TYPE_CHECKING

logger = logging.getLogger(__name__)

# Common Chinese character confusions (错别字 pairs)
# Format: (wrong, correct) — these are common typos/misuses
CN_CONFUSIONS: list[tuple[str, str]] = [
    # 的/地/得 confusion (very common)
    ("的得", "的"),  # over-correction pattern
    # Common homophone errors
    ("在次", "再次"),
    ("在见", "再见"),
    ("从新", "重新"),
    ("必竟", "毕竟"),
    ("不记其数", "不计其数"),
    ("穿流不息", "川流不息"),
    ("一股作气", "一鼓作气"),
    ("名不符实", "名不副实"),
    ("默守成规", "墨守成规"),
    ("迫不急待", "迫不及待"),
    ("磬竹难书", "罄竹难书"),
    ("一如继往", "一如既往"),
    ("九宵云外", "九霄云外"),
    ("烩炙人口", "脍炙人口"),
    ("洁白无暇", "洁白无瑕"),
    ("死心踏地", "死心塌地"),
    ("萎糜不振", "萎靡不振"),
    ("沤心沥血", "呕心沥血"),
    ("出奇不意", "出其不意"),
    ("滥芋充数", "滥竽充数"),
    ("试目以待", "拭目以待"),
    ("一獗不振", "一蹶不振"),
    ("不径而走", "不胫而走"),
    ("谈笑风声", "谈笑风生"),
    ("人情事故", "人情世故"),
    ("有持无恐", "有恃无恐"),
    ("鬼鬼崇崇", "鬼鬼祟祟"),
    ("金榜提名", "金榜题名"),
    ("走头无路", "走投无路"),
    ("居心颇测", "居心叵测"),
    ("一愁莫展", "一筹莫展"),
    ("直接了当", "直截了当"),
    ("变本加利", "变本加厉"),
    ("兴高彩烈", "兴高采烈"),
    ("既往不究", "既往不咎"),
    ("一窃不通", "一窍不通"),
    ("破斧沉舟", "破釜沉舟"),
    ("莫不关心", "漠不关心"),
    ("不可思义", "不可思议"),
    ("不醒人事", "不省人事"),
    ("大才小用", "大材小用"),
    ("言简意骇", "言简意赅"),
    ("暂露头角", "崭露头角"),
    ("旁证博引", "旁征博引"),
    ("甘败下风", "甘拜下风"),
    ("自抱自弃", "自暴自弃"),
    ("一诺千斤", "一诺千金"),
    ("天翻地复", "天翻地覆"),
    ("悬梁刺骨", "悬梁刺股"),
    ("食不裹腹", "食不果腹"),
    ("迫不得以", "迫不得已"),
    ("草管人命", "草菅人命"),
    ("娇揉造作", "矫揉造作"),
    ("黄梁美梦", "黄粱美梦"),
    ("不落巢臼", "不落窠臼"),
    ("鼎立相助", "鼎力相助"),
    ("蛛丝蚂迹", "蛛丝马迹"),
    ("一如即往", "一如既往"),
    ("美仑美奂", "美轮美奂"),
    ("蛛丝马迹", "蛛丝蚂迹"),
    ("额首称庆", "额手称庆"),
    ("苍海桑田", "沧海桑田"),
]

# Regex patterns for Chinese character detection
CN_CHAR = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
CN_TEXT = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]{2,}")

# Repeated character pattern (e.g., "的的", "了了")
CN_REPEATED = re.compile(r"([\u4e00-\u9fff])\1")


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(CN_CHAR.search(text))


def check_chinese(text: str) -> list[tuple[int, int, str]]:
    """Check Chinese text for common errors.

    Returns a list of (start, end, suggestion) tuples.
    Start/end are character positions (not byte offsets).
    """
    errors: list[tuple[int, int, str]] = []

    # Check for known confusions
    for wrong, correct in CN_CONFUSIONS:
        # Find all occurrences
        idx = 0
        while True:
            pos = text.find(wrong, idx)
            if pos == -1:
                break
            errors.append((pos, pos + len(wrong), correct))
            idx = pos + 1

    # Check for repeated Chinese characters (potential typo)
    for match in CN_REPEATED.finditer(text):
        # Skip intentionally repeated chars like "哈哈", "嗯嗯", "哦哦"
        char = match.group(1)
        if char in "哈哈嗯哦噢喔哎唉啧啧嘻天人人年年月月日日时时分分秒秒处处家家事事项项步步妈妈爸爸哥哥姐姐弟弟妹妹爷爷奶婆婆公":
            continue
        errors.append((match.start(), match.end(), char))

    # Deduplicate and sort by position
    seen: set[tuple[int, int, str]] = set()
    unique: list[tuple[int, int, str]] = []
    for err in sorted(errors, key=lambda x: (x[0], -x[1])):
        if err not in seen:
            seen.add(err)
            unique.append(err)

    return unique


def check_chinese_words(text: str) -> list[tuple[str, str, str]]:
    """Check Chinese text returning (word, position_info, suggestion) tuples.
    
    This is a friendlier interface for integration with the spellcheck system.
    """
    results: list[tuple[str, str, str]] = []
    errors = check_chinese(text)
    for start, end, suggestion in errors:
        word = text[start:end]
        results.append((word, f"位置 {start}-{end}", suggestion))
    return results
