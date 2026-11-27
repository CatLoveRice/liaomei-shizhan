#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地关系档案与时间轴记忆存储脚本（零外部依赖，纯 Python 标准库）
用途：仅在用户明确同意后，用于跨对话记录特定关系对象的档案、时间轴事件、红线预警与推进阶段。
隐私原则：所有数据仅存于用户本地目录，不联网、不上传；支持随时查看与一键删除。
"""
import argparse
import datetime
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".memory", "profiles.json")


def load_db(path):
    if not os.path.exists(path):
        return {"profiles": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_list(args):
    db = load_db(args.store)
    if not db["profiles"]:
        print("当前暂无已保存的关系档案。")
        return
    for name, p in db["profiles"].items():
        print(f"- {name} | 阶段: {p.get('stage', '未定')} | 类型: {p.get('archetype', '未定')} | 事件数: {len(p.get('events', []))} | 更新: {p.get('updated_at', '-')}")


def cmd_show(args):
    db = load_db(args.store)
    p = db["profiles"].get(args.name)
    if not p:
        print(f"未找到档案：{args.name}")
        return
    print(json.dumps(p, ensure_ascii=False, indent=2))


def cmd_upsert(args):
    db = load_db(args.store)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p = db["profiles"].get(args.name, {
        "name": args.name,
        "created_at": now,
        "events": [],
        "red_flags": [],
    })
    if args.stage:
        p["stage"] = args.stage
    if args.archetype:
        p["archetype"] = args.archetype
    if args.summary:
        p["summary"] = args.summary
    if args.flag:
        p.setdefault("red_flags", []).append({"time": now, "flag": args.flag})
    if args.event:
        p.setdefault("events", []).append({"time": now, "fact": args.event})
    p["updated_at"] = now
    db["profiles"][args.name] = p
    save_db(args.store, db)
    print(f"已更新档案：{args.name}（{now}）")


def cmd_delete(args):
    db = load_db(args.store)
    if args.name in db["profiles"]:
        del db["profiles"][args.name]
        save_db(args.store, db)
        print(f"已删除档案：{args.name}")
    else:
        print(f"未找到档案：{args.name}")


def main():
    parser = argparse.ArgumentParser(description="本地关系档案与时间轴管理工具")
    parser.add_argument("--store", default=DEFAULT_STORE, help="JSON 存储路径")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="列出所有档案")

    p_show = sub.add_parser("show", help="查看单个档案")
    p_show.add_argument("name", help="档案代号（建议使用昵称/字母代号保护隐私）")

    p_up = sub.add_parser("upsert", help="新建或更新档案")
    p_up.add_argument("name", help="档案代号")
    p_up.add_argument("--stage", help="当前阶段（初识/暧昧/确立/冷淡/止损等）")
    p_up.add_argument("--archetype", help="对方画像（如剪刀/石头/布、依恋类型等）")
    p_up.add_argument("--summary", help="核心局面摘要")
    p_up.add_argument("--event", help="追加一条带时间戳的实锤事件")
    p_up.add_argument("--flag", help="追加一条红灯/边界预警")

    p_del = sub.add_parser("delete", help="删除档案")
    p_del.add_argument("name", help="档案代号")

    args = parser.parse_args()
    {"list": cmd_list, "show": cmd_show, "upsert": cmd_upsert, "delete": cmd_delete}[args.cmd](args)


if __name__ == "__main__":
    main()
