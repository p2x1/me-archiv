# -*- coding: utf-8 -*-
<#
    me-archive / run-daily.ps1
    ==========================
    每天干三件事：

      ① 封存 —— 跑 snapshot.py --auto（补历史欠账 + 重做今天）
      ② 镜像 —— 用 robocopy /MIR 把整个 me-archive 同步到 D:\me-archive-backup
      ③ 提交 —— git add/commit；配了远端就 push

    谁在调它：
      * Windows 计划任务「me-archive-daily」（每天 23:50，错过会自动补跑）
      * 或者你双击同目录下的 封存.bat
      * 或者手动： powershell -ExecutionPolicy Bypass -File run-daily.ps1

    日志写在 logs\YYYY-MM-DD.log。出问题先看那儿。
#>

$Root   = $PSScriptRoot
$Mirror = "D:\me-archive-backup"
$LogDir = Join-Path $Root "logs"

# 找 python：先用装好的绝对路径，找不到再退回 PATH 里的 python
$Python = "C:\Users\xp\AppData\Local\Programs\Python\Python313\python.exe"
if (-not (Test-Path $Python)) {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $Python = $cmd.Source }
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir ("{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

function Say([string]$m) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

Say "=== me-archive daily: start ==="

# ---------- ① 封存 ----------
if (-not $Python) {
    Say "[FAIL] 找不到 python，跳过封存"
} else {
    Say "python: $Python"
    & $Python (Join-Path $Root "snapshot.py") --auto 2>&1 | ForEach-Object { Say "  $_" }
    Say "snapshot exit code: $LASTEXITCODE"
}

# ---------- ② 镜像到 D 盘 ----------
if (-not (Test-Path "D:\")) {
    Say "[skip] 没有 D 盘，跳过镜像"
} else {
    # /MIR = 镜像（多退少补）  /XD = 排除 logs 和 .git
    # exit code 0~7 都是成功，>=8 才是出错
    robocopy $Root $Mirror /MIR /XD "$Root\logs" "$Root\.git" /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) {
        Say "[FAIL] robocopy 出错 (code $rc)"
    } else {
        Say "mirror -> $Mirror  ok (robocopy code $rc)"
    }
}

# ---------- ③ git 提交 ----------
if (-not (Test-Path (Join-Path $Root ".git"))) {
    Say "[skip] 还没 git init，跳过提交"
} else {
    Push-Location $Root
    try {
        # 用 -c 临时给身份，免得依赖全局 git config
        & git add -A 2>&1 | Out-Null

        $pending = & git status --porcelain
        if ($pending) {
            $msg = "snapshot {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm")
            & git -c user.name="me-archive" -c user.email="me-archive@localhost" `
                  commit -m $msg 2>&1 | ForEach-Object { Say "  $_" }
        } else {
            Say "git: 没有变化，不用提交"
        }

        $remote = & git remote 2>$null
        if ($remote) {
            Say "git: push -> $remote"
            & git push 2>&1 | ForEach-Object { Say "  $_" }
            if ($LASTEXITCODE -ne 0) { Say "[FAIL] push 失败 (code $LASTEXITCODE)" }
        } else {
            Say "git: 还没配远端，跳过 push"
        }
    } finally {
        Pop-Location
    }
}

Say "=== me-archive daily: done ==="
