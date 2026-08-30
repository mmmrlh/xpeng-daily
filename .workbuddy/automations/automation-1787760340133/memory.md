# 小鹏日报看板-同步部署 执行记录

## 2026-08-27 06:40（首次记录）
- deploy.py 同步：✅ 成功，新增 08-26 日报，data.json 更新（38日报+2月报=40份）
- git 提交：✅ 2471332「更新日报 2026-08-26」
- git push：❌ 失败 — Clash Party (mihomo) 代理节点 HTTPS TLS 握手全挂（http 明文通 200，https 报 schannel failed to receive handshake / openssl unexpected eof）
  - 已尝试：schannel 默认、openssl 后端、7890/7892 端口，均失败；无控制 API 可切换节点
- 线上验证：无法执行（本机所有 https 出站均失败）
- 遗留：本地 2 个提交未推送（2471332 + e816077 Add daily report 08-25），需代理恢复后手动补推

## 2026-08-27 09:12 补推
- 用户重启/切换节点后代理恢复：github/google/pages.dev 走 7890 全 200（mihomo PID 16280→62572）
- 补推成功：e816077..2471332 main -> main（本地与远端已同步）
- 线上验证 ✅：xpeng-report-dashboard.pages.dev data.json 最新 = 2026-08-26（Cloudflare Pages 自动构建约 1-2 分钟）
- 遗留已清零，本次自动化任务最终完整成功

## 2026-08-27 11:27 全量重算同步
- 历史数据导入后（raw 补全 40 天），批量重生成全部 38 份日报 HTML（参考日均改为 40 天完整历史）
- deploy.py 同步：✅ 38 份日报全部更新，data.json 更新
- git 提交：✅ 6d72f7a「更新全部日报：参考日均基于40天完整历史重算」40 files
- git push：✅ 2471332..6d72f7a main -> main（代理正常）
- 线上验证 ✅：xpeng-report-dashboard.pages.dev 8-26 日报 200，南大干线参考日均 2715度（新版特征确认）

## 2026-08-28 06:40
- deploy.py 同步：✅ 新增 08-27 日报，data.json 更新（39日报+2月报=41份）
- git 提交：✅ fdd7bea「更新日报 2026-08-27」（3 files：日报 HTML + data.json + automation memory）
- git push：⚠️ 首次挂起 7 分钟 — 根因是 PortableGit 默认 `credential.helper=helper-selector`（GCM），无人值守时弹交互窗口等待选择凭据助手
  - 解决：`git -c credential.helper= -c credential.helper=wincred` 清空默认 helper 并直接用 Windows 凭据管理器（wincred 可读到 mmmrlh 凭据）；须加 `-c credential.interactive=false -c credential.modalPrompt=false` 防弹窗
  - 推送成功：6d72f7a..fdd7bea main -> main（代理 7890 正常）
- 线上验证 ✅：xpeng-report-dashboard.pages.dev data.json 最新 = 2026-08-27（构建约 1 分钟即生效，未等满 2 分钟）

## 2026-08-29 06:40
- deploy.py 同步：✅ 新增 08-28 日报，data.json 更新（40日报+2月报=42份）
- git 提交：✅ 9a8aa17「更新日报 2026-08-28」（5 files：日报 HTML + data.json + 2 memory 文件 + automation memory）
- git push：✅ 一次成功，fdd7bea..9a8aa17 main -> main（wincred 免弹窗命令正常，代理 7890 正常）
- 线上验证 ✅：xpeng-report-dashboard.pages.dev data.json 最新 = 2026-08-28，共 42 份（构建约 75 秒内生效）

## 2026-08-30 06:40
- deploy.py 同步：✅ 新增 08-29 日报，data.json 更新（41日报+2月报=43份）
- git 提交：✅ 9969302「更新日报 2026-08-29」（4 files：日报 HTML + data.json + 昨日 memory 日志 + automation memory）
- git push：✅ 一次成功，9a8aa17..9969302 main -> main（wincred 免弹窗命令正常，代理 7890 正常）
- 线上验证 ✅：xpeng-report-dashboard.pages.dev data.json 最新 = 2026-08-29，共 43 份（首次检查仍在构建显示 08-28，约 75 秒后构建完成生效）

## 经验
- Windows 上 Git Bash 的 curl/git 默认 schannel TLS 后端，走代理失败时可用 `git -c http.sslBackend=openssl` 排查（本次两者都失败，定位为节点问题）
- 判断节点故障方法：curl 走代理访问 http 明文（通）vs https（挂）→ 节点 TLS 层故障
- mihomo 无 9090 控制 API（Clash Party 未启用），无法程序化切节点，需用户在客户端手动处理
- ⚠️ Windows PortableGit 无人值守 push 的坑：credential.helper 默认是 helper-selector/GCM，会弹交互窗口挂起进程。标准推送命令应固定为：
  `git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 -c credential.helper= -c credential.helper=wincred -c credential.interactive=false -c credential.modalPrompt=false push origin main`
  （凭据存于 Windows 凭据管理器 target=git:https://github.com，用户 mmmrlh）
