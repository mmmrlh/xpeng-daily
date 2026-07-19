#!/usr/bin/env python3
"""
小鹏日报看板 — 部署同步脚本
用法：python3 deploy.py

作用：
1. 从源文件夹扫描所有 小鹏运营日报_YYYY-MM-DD.html 文件
2. 复制到本项目的 reports/ 目录
3. 生成 data.json（日报索引）
4. 完成后提示部署命令
"""

import json
import os
import shutil
import datetime
import re

# ====== 路径配置 ======
# 日报源文件（自动化生成的目录）
SRC_DIR = "/Users/apple/Documents/自动化任务/outputs/xpeng_charge_report"
# 本项目路径
PROJECT_DIR = "/Users/apple/WorkBuddy/小鹏日报看板"
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")

# 星期映射
WEEKDAY_MAP = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}


def main():
    print("=" * 50)
    print("  小鹏日报看板 — 部署同步")
    print("=" * 50)

    # 确保 reports 目录存在
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # 扫描源文件夹，找到所有日报 HTML
    reports = []
    for fname in sorted(os.listdir(SRC_DIR), reverse=True):
        m = re.match(r"小鹏运营日报_(\d{4}-\d{2}-\d{2})\.html", fname)
        if m:
            date_str = m.group(1)
            y, m_, d = date_str.split("-")
            w = datetime.date(int(y), int(m_), int(d)).weekday()
            reports.append({
                "date": date_str,
                "file": fname,
                "weekday": WEEKDAY_MAP[w],
            })

    if not reports:
        print("\n❌ 源文件夹中没找到任何日报 HTML 文件！")
        print(f"   源路径: {SRC_DIR}")
        print("   请确认文件名格式为: 小鹏运营日报_YYYY-MM-DD.html")
        return

    print(f"\n📋 找到 {len(reports)} 份日报:")
    for r in reports:
        print(f"   · {r['date']} (星期{r['weekday']})")

    # 复制文件到 reports/
    print(f"\n📂 复制到: {REPORTS_DIR}/")
    for r in reports:
        src = os.path.join(SRC_DIR, r["file"])
        dst = os.path.join(REPORTS_DIR, r["file"])
        shutil.copy2(src, dst)
        size_kb = os.path.getsize(dst) / 1024
        print(f"   ✅ {r['file']} ({size_kb:.0f} KB)")

    # 生成 data.json
    data = {"reports": reports}
    data_path = os.path.join(PROJECT_DIR, "data.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n📄 已生成: data.json")

    print(f"\n{'=' * 50}")
    print(f"  ✅ 同步完成！共 {len(reports)} 份日报")
    print(f"  ")
    print(f"  下一步部署命令：")
    print(f"  cd {PROJECT_DIR}")
    print(f"  git add .")
    print(f"  git commit -m '更新日报'")
    print(f"  git push")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
