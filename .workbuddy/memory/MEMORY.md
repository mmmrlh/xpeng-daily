# 小鹏日报看板 - 项目记忆

## 项目结构
```
小鹏日报看板/
├── index.html         ← 侧边栏+iframe容器页面
├── data.json          ← 日报索引（deploy.py自动生成）
├── deploy.py          ← 同步脚本
└── reports/
    └── 小鹏运营日报_YYYY-MM-DD.html
```

## 数据来源
- 源路径：/Users/apple/WorkBuddy/小鹏运营日报/outputs/
- 自动化日报生成后输出到此目录
- deploy.py 只复制新文件，不删除历史文件

## 部署
- 平台：GitHub Pages
- 仓库：https://github.com/mmmrlh/xpeng-daily
- 永久网址：https://mmmrlh.github.io/xpeng-daily/
- 每日 9:00 自动同步部署（automation-1784476666023）

## GitHub
- 账号：mmmrlh（Mac + Windows 都用这个，但显示名不同）
- 已设置 Personal Access Token，存于 macOS keychain
- mmmrlh-luo 账号已废弃

## 自动化工作流
1. 每日 9:00 触发 automation
2. 运行 deploy.py 同步新日报
3. git add/commit/push 到 GitHub
4. GitHub Pages 自动部署
