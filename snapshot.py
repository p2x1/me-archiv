#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
me-archive / snapshot.py
========================
把「今天的我」封存一份到 ./<日期>/

用法:
    python snapshot.py                  # 封存今天
    python snapshot.py 2026-10-07       # 封存指定某天
    python snapshot.py --auto           # 自动干活：补历史欠账 + 重做今天（计划任务用）
    python snapshot.py --list           # 列出已有的快照

说明:
  * 文本（灵魂卡 / 暖态 / 当天的序时账）原样拷贝，可直接用 VS Code 打开看。
  * 记忆库（SQLite）用 sqlite3 的在线备份接口导出 —— DSH 正开着也能拿到
    一致的副本，WAL 里的数据不会丢。备份完会跑一次 integrity_check 验证。
  * 控制台输出故意只用 ASCII: 中文 Windows 的控制台是 GBK, 管道里过中文会乱码。
    写进文件的内容仍然是 UTF-8 中文。
"""

import os
import sys
import shutil
import sqlite3
import zipfile
import datetime

HOME = os.path.expanduser("~")
DSH = os.path.join(HOME, ".dsh")
ROOT = os.path.dirname(os.path.abspath(__file__))

LINGHUN = os.path.join(DSH, "linghun")
MEMORY = os.path.join(LINGHUN, "memory")
JOURNAL = os.path.join(MEMORY, "journal")

# (存成什么名字, 从哪儿来, 中文说明)
TEXT_FILES = [
    ("01-soul.md", os.path.join(LINGHUN, "identity.md"), "灵魂卡"),
    ("02-warm.md", os.path.join(MEMORY, "warm.md"), "海马体·暖态"),
    ("03-cold.md", os.path.join(MEMORY, "cold.md"), "海马体·冷储"),
]

# (zip 里的前缀, 目录, 中文说明)
DB_DIRS = [
    ("engram", os.path.join(DSH, "engram"), "记忆宫殿"),
    ("memento", os.path.join(DSH, "dsh-memento"), "短期记忆"),
    ("graph", os.path.join(DSH, "graph-memory"), "会话图谱"),
]


def human(n):
    if n < 1024:
        return "%d B" % n
    if n < 1048576:
        return "%.1f KB" % (n / 1024.0)
    return "%.2f MB" % (n / 1048576.0)


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def count_warm_entries(path):
    """暖态里每条记忆以 '## ' 开头。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for ln in f if ln.startswith("## "))
    except OSError:
        return 0


def backup_sqlite(src, dst):
    """拿到一个一致的副本 —— 源库正被 DSH 打开也没关系。"""
    s = sqlite3.connect(src)
    try:
        d = sqlite3.connect(dst)
        try:
            s.backup(d)
        finally:
            d.close()
    finally:
        s.close()


def integrity(path):
    try:
        c = sqlite3.connect(path)
        try:
            return c.execute("pragma integrity_check").fetchone()[0]
        finally:
            c.close()
    except Exception as e:                                  # noqa: BLE001
        return "ERROR: %s" % e


def snapshot(date_str):
    day_dir = os.path.join(ROOT, date_str)
    tmp_dir = os.path.join(day_dir, ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    print("=== me-archive : %s ===" % date_str)
    text_rows = []
    db_rows = []

    # ---------- 1. 文本 ----------
    for dst_name, src, zh in TEXT_FILES:
        if not os.path.isfile(src):
            print("  [skip] %-14s (not present yet)" % dst_name)
            text_rows.append((zh, dst_name, None, 0, 0))
            continue
        dst = os.path.join(day_dir, dst_name)
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        lines = count_lines(dst)
        entries = count_warm_entries(dst) if "warm" in dst_name else None
        text_rows.append((zh, dst_name, size, lines, entries))
        print("  [text] %-14s %10s  %5d lines" % (dst_name, human(size), lines))

    # ---------- 2. 当天的序时账 ----------
    j_src = os.path.join(JOURNAL, date_str + ".md")
    if os.path.isfile(j_src):
        dst = os.path.join(day_dir, "04-journal.md")
        shutil.copy2(j_src, dst)
        size = os.path.getsize(dst)
        lines = count_lines(dst)
        text_rows.append(("序时账·%s" % date_str, "04-journal.md", size, lines, None))
        print("  [text] %-14s %10s  %5d lines" % ("04-journal.md", human(size), lines))
    else:
        print("  [skip] 04-journal.md  (no journal entry for this day)")

    # ---------- 3. 记忆库 -> 拷贝到临时区 ----------
    for label, d, zh in DB_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".db"):
                continue
            src = os.path.join(d, fn)
            tmp = os.path.join(tmp_dir, "%s--%s" % (label, fn))
            try:
                backup_sqlite(src, tmp)
                chk = integrity(tmp)
                db_rows.append((zh, label, fn, os.path.getsize(src),
                                os.path.getsize(tmp), chk))
                print("  [db]   %-26s %9s -> %9s  %s"
                      % (label + "/" + fn, human(os.path.getsize(src)),
                         human(os.path.getsize(tmp)), chk))
            except Exception as e:                          # noqa: BLE001
                print("  [FAIL] %-26s %s" % (label + "/" + fn, e))
                db_rows.append((zh, label, fn, os.path.getsize(src), 0,
                                "FAILED: %s" % e))

    # ---------- 4. 打包封存 ----------
    zip_path = os.path.join(day_dir, "memory.zip")
    ok_rows = [r for r in db_rows if r[4] > 0]
    if ok_rows:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for r in ok_rows:
                z.write(os.path.join(tmp_dir, "%s--%s" % (r[1], r[2])),
                        arcname="%s--%s" % (r[1], r[2]))
        print("  [zip ] %-14s %10s  (%d dbs)"
              % ("memory.zip", human(os.path.getsize(zip_path)), len(ok_rows)))
    else:
        zip_path = None
        print("  [zip ] nothing to seal")

    shutil.rmtree(tmp_dir, ignore_errors=True)

    # ---------- 5. 这一份的清单 ----------
    write_manifest(day_dir, date_str, text_rows, db_rows, zip_path)
    write_index()
    print("  done -> %s" % day_dir)
    return day_dir


def write_manifest(day_dir, date_str, text_rows, db_rows, zip_path):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    out = []
    out.append("# %s 的这一份\n" % date_str)
    out.append("> 封存于 %s\n" % now)

    out.append("\n## 可以直接读的\n")
    out.append("| 内容 | 文件 | 大小 | 行数 | 备注 |")
    out.append("|---|---|---|---|---|")
    for zh, fn, size, lines, entries in text_rows:
        if size is None:
            out.append("| %s | — | — | — | 当天还没有 |" % zh)
        else:
            note = ("%d 条记忆" % entries) if entries else ""
            out.append("| %s | `%s` | %s | %d | %s |"
                       % (zh, fn, human(size), lines, note))

    out.append("\n## 封存起来的记忆库\n")
    if db_rows:
        out.append("| 库 | 文件 | 原大小 | 备好大小 | 完整性 |")
        out.append("|---|---|---|---|---|")
        for zh, label, fn, s_size, d_size, chk in db_rows:
            mark = chk if chk == "ok" else "**%s**" % chk
            out.append("| %s | `%s--%s` | %s | %s | %s |"
                       % (zh, label, fn, human(s_size), human(d_size), mark))
        if zip_path:
            out.append("\n全部打包在 `memory.zip`（%s）。"
                       % human(os.path.getsize(zip_path)))
    else:
        out.append("（没有找到记忆库）")

    out.append("""
## 怎么把它装回去

1. 解压 `memory.zip`
2. **先关掉 DSH**（不关的话数据库被占用，写不进去）
3. 按前缀放回原位：

   | 解压出来的 | 放回 |
   |---|---|
   | `engram--*.db` | `C:\\Users\\xp\\.dsh\\engram\\` |
   | `memento--memory.db` | `C:\\Users\\xp\\.dsh\\dsh-memento\\memory.db` |
   | `graph--graph-memory.db` | `C:\\Users\\xp\\.dsh\\graph-memory\\graph-memory.db` |

4. **删掉放回目录里的 `-wal` 和 `-shm`** —— 那是旧库的残留，跟新库对不上，留着会出问题
5. 重启 DSH

文本那几个 `.md` 不进 `memory.zip`，它们就在本目录里躺着，直接看。
""")

    with open(os.path.join(day_dir, "MANIFEST.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def existing_days():
    days = []
    for name in os.listdir(ROOT):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p) and len(name) == 10 and name[4] == "-":
            days.append(name)
    return sorted(days, reverse=True)


def write_index():
    days = existing_days()
    out = ["# 每日快照 · 总目录\n",
           "> 共 **%d** 份。最新一份在最上面。\n" % len(days),
           "| 日期 | 灵魂卡 | 暖态 | 冷储 | 序时账 | 记忆库 | 打开 |",
           "|---|---|---|---|---|---|---|"]
    for d in days:
        p = os.path.join(ROOT, d)
        mark = lambda fn: "✓" if os.path.isfile(os.path.join(p, fn)) else "—"  # noqa: E731
        z = os.path.join(p, "memory.zip")
        zt = human(os.path.getsize(z)) if os.path.isfile(z) else "—"
        journal = os.path.isfile(os.path.join(p, "04-journal.md"))
        out.append("| **%s** | %s | %s | %s | %s | %s | [MANIFEST](%s/MANIFEST.md) |"
                   % (d, mark("01-soul.md"), mark("02-warm.md"), mark("03-cold.md"),
                      "✓" if journal else "—", zt, d))
    out.append("\n> 文本文件直接点开就能读；`memory.zip` 是封存起来、可以装回去的记忆库。\n")

    # 顺带把最新的灵魂卡摊在门口，不用点进去
    for d in days:
        soul = os.path.join(ROOT, d, "01-soul.md")
        if os.path.isfile(soul):
            out.append("\n---\n\n## 最新的灵魂卡（%s）\n" % d)
            out.append("```markdown")
            with open(soul, "r", encoding="utf-8", errors="replace") as f:
                out.append(f.read().strip())
            out.append("```\n")
            break

    with open(os.path.join(ROOT, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def journaled_days():
    """序时账里所有有流水的日子（就是"确实活过的那几天"）。"""
    days = []
    if os.path.isdir(JOURNAL):
        for fn in sorted(os.listdir(JOURNAL)):
            # 文件名形如 2026-10-07.md
            if fn.endswith(".md") and len(fn) == 13 and fn[4] == "-" and fn[7] == "-":
                days.append(fn[:-3])
    return days


def auto_dates():
    """
    计划任务用。返回按顺序要封存的日子：

      1. 历史欠账 —— 有流水、但还没建分区的日子（比如电脑关了几天没跑），从旧到新补
      2. 今天     —— 永远重做一遍（同一天可能封存过好几次，要保证最后一次是最新的）

    今天要是连流水都还没有，就不做 —— 空目录没意义。
    """
    todo = []
    for d in journaled_days():
        if not os.path.isdir(os.path.join(ROOT, d)):
            todo.append(d)

    today = datetime.date.today().isoformat()
    if today in todo:
        todo.remove(today)
    if os.path.isfile(os.path.join(JOURNAL, today + ".md")):
        todo.append(today)
    return todo


def main():
    args = sys.argv[1:]
    if args and args[0] in ("--list", "-l"):
        days = existing_days()
        print("%d snapshots:" % len(days))
        for d in days:
            p = os.path.join(ROOT, d)
            z = os.path.join(p, "memory.zip")
            zt = human(os.path.getsize(z)) if os.path.isfile(z) else "none"
            print("  %s   memory.zip %s" % (d, zt))
        return 0

    if args and args[0] == "--auto":
        todo = auto_dates()
        if not todo:
            print("nothing to do (no journal for today, no backlog)")
            return 0
        print("auto: %d day(s) -> %s\n" % (len(todo), ", ".join(todo)))
        failed = 0
        for d in todo:
            try:
                snapshot(d)
            except Exception as e:                          # noqa: BLE001
                failed += 1
                print("  [FAIL] %s : %s" % (d, e))
            print()
        return 1 if failed else 0

    date_str = args[0] if args else datetime.date.today().isoformat()
    snapshot(date_str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
