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
import calendar
import re

# ====== 路径配置（自动推导，无需手动修改） ======
# 迁移包目录结构：
#   迁移包根目录/
#     ├── 小鹏运营日报/     （采集+生成）
#     ├── 小鹏日报看板/     （本脚本所在目录）
#     └── 小鹏月报分析/output/
# 如需要自定义，可通过环境变量覆盖：
#   XPENG_DAILY_SRC / XPENG_MONTHLY_SRC / XPENG_DASHBOARD_DIR
_MY_DIR = os.path.dirname(os.path.abspath(__file__))            # 小鹏日报看板/
_BASE_DIR = os.path.dirname(_MY_DIR)                            # 迁移包根目录/
SRC_DIR = os.environ.get("XPENG_DAILY_SRC", os.path.join(_BASE_DIR, "小鹏运营日报", "outputs"))
MONTHLY_SRC_DIR = os.environ.get("XPENG_MONTHLY_SRC", os.path.join(_BASE_DIR, "小鹏月报分析", "output"))
PROJECT_DIR = os.environ.get("XPENG_DASHBOARD_DIR", _MY_DIR)
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
    if not os.path.isdir(SRC_DIR):
        print(f"   ⚠️ 日报源目录不存在: {SRC_DIR}")
    else:
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
    for fname in os.listdir(REPORTS_DIR):
        # 日报：sort_date = 日期本身 (YYYY-MM-DD)
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
                "sort_date": date_str,
            })
            continue

        # 月报：sort_date = 当月最后一天 + ".5"，排在最后一天日报和次月第一天之间
        # 例如 7月 last_day=31 → sort_date="2026-07-31.5"，位于 8/1 和 7/31 之间
        m = re.match(r"小鹏(\d+)月运营月报\.html", fname)
        if m:
            month_num = int(m.group(1))
            date_str = f"2026-{month_num:02d}"
            last_day = calendar.monthrange(2026, month_num)[1]
            sort_date = f"2026-{month_num:02d}-{last_day:02d}.5"
            reports.append({
                "date": date_str,
                "file": fname,
                "type": "monthly",
                "label": f"{month_num}月",
                "sort_date": sort_date,
            })
            continue

    # 按 sort_date 降序排列，月报自然穿插在当月最后一天日报之后
    reports.sort(key=lambda r: r["sort_date"], reverse=True)

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
            print(f"   · {r['date']} 📊 {r['label']}月报  [sort: {r['sort_date']}]")
        else:
            print(f"   · {r['date']} (星期{r['weekday']})  [sort: {r['sort_date']}]")

    print(f"\n{'=' * 50}")
    print(f"  ✅ 同步完成！")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
