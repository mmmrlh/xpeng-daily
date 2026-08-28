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
   - ⚠️ git push 时需 unset 代理环境变量（`HTTP_PROXY`/`HTTPS_PROXY` 等），否则 ClashX 代理会干扰 TLS 握手导致 `SSL_ERROR_SYSCALL`
   - Mac：credential 通过 macOS keychain (osxkeychain) 自动提供
   - **Windows（无人值守）**：默认 helper-selector/GCM 会弹交互窗口挂起，必须强制用 wincred：
     `git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 -c credential.helper= -c credential.helper=wincred -c credential.interactive=false -c credential.modalPrompt=false push origin main`
     （Windows 凭据管理器 target=git:https://github.com，用户 mmmrlh）
4. GitHub Pages / Cloudflare Pages 自动部署（xpeng-report-dashboard.pages.dev 构建约 1 分钟生效）
