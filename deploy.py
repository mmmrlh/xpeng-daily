#!/usr/bin/env python3
"""
小鹏日报看板 — 部署同步脚本
用法：python3 deploy.py

作用：
1. 从源文件夹扫描新增的 小鹏运营日报_YYYY-MM-DD.html 文件
2. 只复制还不存在的文件到 reports/ 目录（不删除历史日报）
3. 扫描 reports/ 目录下的所有日报，生成 data.json
"""

import json
import os
import shutil
import datetime
import re

# ====== 路径配置 ======
SRC_DIR = "/Users/apple/WorkBuddy/小鹏运营日报/outputs"
PROJECT_DIR = "/Users/apple/WorkBuddy/小鹏日报看板"
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
START_DATE = "2026-07-20"  # 只同步此日期及之后的日报

WEEKDAY_MAP = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}


def main():
    print("=" * 50)
    print("  小鹏日报看板 — 部署同步")
    print("=" * 50)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    # === 第一步：从源文件夹复制新/更新的日报 ===
    new_count = 0
    update_count = 0
    for fname in os.listdir(SRC_DIR):
        m = re.match(r"小鹏运营日报_(\d{4}-\d{2}-\d{2})\.html", fname)
        if not m:
            continue
        date_str = m.group(1)
        if date_str < START_DATE:
            continue  # 早于起始日期，跳过
        src = os.path.join(SRC_DIR, fname)
        dst = os.path.join(REPORTS_DIR, fname)
        if os.path.exists(dst):
            src_mtime = os.path.getmtime(src)
            dst_mtime = os.path.getmtime(dst)
            if src_mtime <= dst_mtime:
                continue  # 源文件未更新，跳过
            shutil.copy2(src, dst)
            update_count += 1
            print(f"   🔄 更新: {fname}")
        else:
            shutil.copy2(src, dst)
            new_count += 1
            print(f"   🆕 新增: {fname}")

    if new_count == 0 and update_count == 0:
        print("   — 没有新日报需要同步")
    else:
        parts = []
        if new_count > 0:
            parts.append(f"{new_count} 个新增")
        if update_count > 0:
            parts.append(f"{update_count} 个更新")
        print(f"   共同步 {'、'.join(parts)}")

    # === 第二步：扫描 reports/ 目录，生成 data.json ===
    reports = []
    for fname in sorted(os.listdir(REPORTS_DIR), reverse=True):
        m = re.match(r"小鹏运营日报_(\d{4}-\d{2}-\d{2})\.html", fname)
        if not m:
            continue
        date_str = m.group(1)
        y, m_, d = date_str.split("-")
        w = datetime.date(int(y), int(m_), int(d)).weekday()
        reports.append({
            "date": date_str,
            "file": fname,
            "weekday": WEEKDAY_MAP[w],
        })

    data = {"reports": reports}
    data_path = os.path.join(PROJECT_DIR, "data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📄 data.json 已更新，共 {len(reports)} 份日报:")
    for r in reports:
        print(f"   · {r['date']} (星期{r['weekday']})")

    print(f"\n{'=' * 50}")
    print(f"  ✅ 同步完成！")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
