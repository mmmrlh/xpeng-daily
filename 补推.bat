@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem --- locate git: bundled PortableGit first, then system PATH ---
set "GITEXE="
for %%V in (1.3.0 1.2.0) do (
  if exist "C:\Users\TXair\.workbuddy\binaries\PortableGit\versions\%%V\cmd\git.exe" set "GITEXE=C:\Users\TXair\.workbuddy\binaries\PortableGit\versions\%%V\cmd\git.exe"
)
if not defined GITEXE where git >nul 2>&1 && set "GITEXE=git"
if not defined GITEXE (
  echo [ERROR] git.exe not found.
  goto :end
)

set "HTTP_PROXY="
set "HTTPS_PROXY="
set "http_proxy="
set "https_proxy="
set "ALL_PROXY="
set "all_proxy="

echo ================================================
echo  XPeng Daily Report  -  Push Pending Commits
echo ================================================
echo.

echo [1/3] Pending commits to push:
"%GITEXE%" -c credential.helper= -c credential.helper=store log origin/main..HEAD --oneline
echo.

echo [2/3] Pushing to GitHub (direct, no proxy) ...
"%GITEXE%" -c credential.helper= -c credential.helper=store -c credential.interactive=false -c credential.modalPrompt=false -c http.proxy= -c https.proxy= push origin main
set "RC=%ERRORLEVEL%"
echo ExitCode=%RC%

if not "%RC%"=="0" (
  echo.
  echo Direct push failed. Retrying via local proxy 127.0.0.1:7890 ...
  echo ^(Clash must be running, otherwise this also fails.^)
  "%GITEXE%" -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 -c credential.helper= -c credential.helper=store -c credential.interactive=false -c credential.modalPrompt=false push origin main
  set "RC=%ERRORLEVEL%"
  echo ExitCode=%RC%
)

echo.
if "%RC%"=="0" (
  echo [3/3] PUSH OK - Cloudflare Pages rebuilds in about 1 minute.
  echo Verify: https://xpeng-report-dashboard.pages.dev/data.json
) else (
  echo [3/3] PUSH FAILED - check network or ~/.git-credentials.
)

:end
echo.
pause
