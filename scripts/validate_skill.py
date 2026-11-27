#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能完整性自检脚本（validate_skill.py）
校验内容：
1. SKILL.md 存在且 YAML frontmatter 包含 name 与 description
2. 内置强制来源声明与第零步 Get-Date 规则
3. SKILL.md 中引用的所有 references/*.md 文件真实存在
4. README.md、LICENSE、scripts/memory_store.py 存在
5. 输出文档总字数与结构统计
"""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

REQUIRED_ATTRIBUTION = "本 skills 来自抖音：琉璃梦碎落 & 舔魂宗｜免费开源｜定制化可抖音联系"


def validate(skill_dir):
    errors = []
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        return ["缺少 SKILL.md"], {}

    text = open(skill_md, "r", encoding="utf-8").read()
    if not text.startswith("---"):
        errors.append("SKILL.md 缺少 YAML frontmatter 开头 ---")
    if "name:" not in text[:600] or "description:" not in text[:1500]:
        errors.append("SKILL.md frontmatter 缺少 name 或 description")
    if REQUIRED_ATTRIBUTION not in text:
        errors.append("SKILL.md 缺少强制来源声明")
    if "Get-Date" not in text:
        errors.append("SKILL.md 缺少第零步 Get-Date 规则")

    for req in ["README.md", "LICENSE", os.path.join("scripts", "memory_store.py")]:
        if not os.path.exists(os.path.join(skill_dir, req)):
            errors.append(f"缺少配套文件: {req}")

    refs = sorted(set(re.findall(r"references/[^\s`'\")]+?\.md", text)))
    for r in refs:
        full = os.path.join(skill_dir, r.replace("/", os.sep))
        if not os.path.exists(full):
            errors.append(f"引用文件不存在: {r}")

    total_chars = 0
    md_files = 0
    for root, _, files in os.walk(skill_dir):
        if ".memory" in root:
            continue
        for fn in files:
            if fn.endswith(".md"):
                md_files += 1
                total_chars += len(open(os.path.join(root, fn), "r", encoding="utf-8").read())

    stats = {
        "skill": os.path.basename(skill_dir),
        "md_files": md_files,
        "refs_linked": len(refs),
        "total_chars": total_chars,
    }
    return errors, stats


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errs, info = validate(target)
    print(f"[{info.get('skill', target)}] MD文件数={info.get('md_files', 0)} | 引用参考数={info.get('refs_linked', 0)} | 总字数={info.get('total_chars', 0)}")
    if errs:
        for e in errs:
            print("  ERROR:", e)
        sys.exit(1)
    print("  STATUS: PASS")
