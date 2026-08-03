#!/usr/bin/env python3
"""
小鹏日报看板 — 部署同步脚本
用法：python3 deploy.py

作用：
1. 从源文件夹扫描日/月报 HTML 文件
2. 只复制还不存在的文件到 reports/ 目录（不删除历史文件）
3. 扫描 reports/ 目录下所有日报和月报，生成 data.json
"""

import json
import os
import shutil
import datetime
import re

# ====== 路径配置 ======
SRC_DIR = "/Users/apple/WorkBuddy/小鹏运营日报/outputs"
MONTHLY_SRC_DIR = "/Users/apple/WorkBuddy/小鹏月报分析/output"
PROJECT_DIR = "/Users/apple/WorkBuddy/小鹏日报看板"
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
START_DATE = "2026-07-20"  # 日报：只同步此日期及之后的

WEEKDAY_MAP = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}


def sync_file(src, dst, fname):
    """复制或更新单个文件，返回操作类型：'new' / 'update' / 'skip'"""
    if os.path.exists(dst):
        src_mtime = os.path.getmtime(src)
        dst_mtime = os.path.getmtime(dst)
        if src_mtime <= dst_mtime:
            return "skip"
        shutil.copy2(src, dst)
        return "update"
    else:
        shutil.copy2(src, dst)
        return "new"


def main():
    print("=" * 50)
    print("  小鹏日报看板 — 部署同步")
    print("=" * 50)

    os.makedirs(REPORTS_DIR, exist_ok=True)

    # === 第一步：同步日/月报到 reports/ ===
    new_count = 0
    update_count = 0

    # 日报：小鹏运营日报_YYYY-MM-DD.html
    for fname in os.listdir(SRC_DIR):
        m = re.match(r"小鹏运营日报_(\d{4}-\d{2}-\d{2})\.html", fname)
        if not m:
            continue
        date_str = m.group(1)
        if date_str < START_DATE:
            continue
        src = os.path.join(SRC_DIR, fname)
        dst = os.path.join(REPORTS_DIR, fname)
        result = sync_file(src, dst, fname)
        if result == "new":
            new_count += 1
            print(f"   🆕 新增日报: {fname}")
        elif result == "update":
            update_count += 1
            print(f"   🔄 更新日报: {fname}")

    # 月报：小鹏X月运营月报.html（如 小鹏6月运营月报.html）
    if os.path.isdir(MONTHLY_SRC_DIR):
        for fname in sorted(os.listdir(MONTHLY_SRC_DIR)):
            m = re.match(r"小鹏(\d+)月运营月报\.html", fname)
            if not m:
                continue
            src = os.path.join(MONTHLY_SRC_DIR, fname)
            dst = os.path.join(REPORTS_DIR, fname)
            result = sync_file(src, dst, fname)
            if result == "new":
                new_count += 1
                print(f"   🆕 新增月报: {fname}")
            elif result == "update":
                update_count += 1
                print(f"   🔄 更新月报: {fname}")
    else:
        print(f"   ⚠️ 月报目录不存在: {MONTHLY_SRC_DIR}")

    if new_count == 0 and update_count == 0:
        print("   — 没有新日报/月报需要同步")
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
        # 日报
        m = re.match(r"小鹏运营日报_(\d{4}-\d{2}-\d{2})\.html", fname)
        if m:
            date_str = m.group(1)
            y, m_, d = date_str.split("-")
            w = datetime.date(int(y), int(m_), int(d)).weekday()
            reports.append({
                "date": date_str,
                "file": fname,
                "type": "daily",
                "weekday": WEEKDAY_MAP[w],
            })
            continue

        # 月报
        m = re.match(r"小鹏(\d+)月运营月报\.html", fname)
        if m:
            month_num = int(m.group(1))
            date_str = f"2026-{month_num:02d}"
            # 月报的 sort_date 用当月最后一天，保证排序正确
            if month_num == 12:
                sort_date = "2026-12-31"
            else:
                # 下月第一天减一天
                import calendar
                last_day = calendar.monthrange(2026, month_num)[1]
                sort_date = f"2026-{month_num:02d}-{last_day:02d}"
            reports.append({
                "date": date_str,
                "file": fname,
                "type": "monthly",
                "label": f"{month_num}月",
            })
            continue

    # 年报也可以加，预留
    # 小鹏2026年度运营年报.html 等

    # 按 sort_date 排序（日报用 date，月报用月末日期）
    # 这里日报 date 已经是 YYYY-MM-DD，月报 date 是 YYYY-MM，用 date 直接排序月报会排在日报前面
    # 用 label/sort_key 解决：月报放在当月最后
    data = {"reports": reports}
    data_path = os.path.join(PROJECT_DIR, "data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    daily_count = sum(1 for r in reports if r.get("type") != "monthly")
    monthly_count = sum(1 for r in reports if r.get("type") == "monthly")
    print(f"\n📄 data.json 已更新")
    print(f"   日报 {daily_count} 份 + 月报 {monthly_count} 份 = 共 {len(reports)} 份")
    for r in reports:
        if r.get("type") == "monthly":
            print(f"   · {r['date']} 📊 {r['label']}月报")
        else:
            print(f"   · {r['date']} (星期{r['weekday']})")

    print(f"\n{'=' * 50}")
    print(f"  ✅ 同步完成！")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
