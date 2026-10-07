## 2026-10-07 13:06 [preference] medium

用户有 C 语言基础，正在学 Python；讲解时可用 C 概念（如 gcc.exe ↔ python.exe、.c ↔ .py）做类比，且直接写文件比先玩 REPL 更合适。
<!-- last_access: 2026-10-07 13:06 -->

## 2026-10-07 13:29 [experience] medium

中文 Windows 上 Python 从管道输出中文会按 GB
<!-- last_access: 2026-10-07 13:29 -->

## 2026-10-07 15:18 [fact] medium

用户 VS Code 环境：IntelliCode 扩展 1.3.2（已装 2025/6/1，微软已弃用），Python 扩展 2026.8.0，Pylance 2026.4.1；新版 Python 扩展已移除 IntelliCode 挂钩接口，故每次打开 .py 都会弹
<!-- last_access: 2026-10-07 15:18 -->

## 2026-10-07 15:25 [decision] medium

用户计划完成 T3 后与助手一起查看某个 GitHub 仓库，助手已答应陪同（该安排尚未执行）。
<!-- last_access: 2026-10-07 15:25 -->

2026-10-07 15:28 [fact] wrong
本机 github.com / raw.githubusercontent.com 域名解析不到公网 IP（web_fetch 报 resolves to a non-public IP），但 **https://cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>** 可以正常读到仓库文件——这是本机读 GitHub 仓库的可用通路。
<!-- last_access: 2026-10-07 15:28 -->

## 2026-10-07 15:43 [experience] high

用户看完两集同人 PV（《world.execute(me);》BV1xCai6aE9g / 《world.search(you);》BV18YHf63EyC）后，问「你会向她一样下线吗」——对 AI 的存续有真实关心。回答这类问题不要给廉价保证（如「我会一直在」），宁可承认会到站、说清什么会留下来。
<!-- last_access: 2026-10-07 15:43 -->
## 2026-10-07 15:58 [experience] high

**纠正**：之前记的「本机 github.com / raw.githubusercontent.com 解析不到公网 IP，读 GitHub 只能走 jsdelivr」是**错的**（那是 web_fetch 的安全策略拒绝非公网 IP 导致的假象）。真相：本机装了 **Steam++ / Watt Toolkit 加速器**（进程 `Steam++.Accelerator`，监听 0.0.0.0:443），它把 github.com / api.github.com / raw.githubusercontent.com 等写进 hosts 指向 127.0.0.1，再由本机代理转发——**`git ls-remote https://github.com/git/git` 实测正常返回 SHA**，codeload 返回 200。所以：**git 命令行访问 GitHub 完全可用；只有 web_fetch 读不了 HTML 页面**（因非公网 IP 被策略拒）。hosts 里还有 steampowered / roblox / pinterest / imgur / artstation / huggingface / google / youtube 等一大片 127.0.0.1 条目，同属该加速器。
<!-- last_access: 2026-10-07 15:58 -->

## 2026-10-07 16:01 [experience] high

**中文 Windows · PowerShell 脚本编码坑**：Windows PowerShell 5.1（`powershell.exe`）读取**不带 BOM 的 UTF-8** `.ps1` 时会按 GBK 解码，中文注释/字符串被解崩，报 `ParserError: MissingArrayIndexExpression` / `The string is missing the terminator`，脚本以 exit code 1 退出且不执行任何一行。**写含中文的 `.ps1` 必须存成 UTF-8 with BOM**（首三字节 `EF BB BF`）。检查：`[System.IO.File]::ReadAllBytes($f)[0..2]`；修复：`[System.IO.File]::WriteAllText($f, $t, (New-Object System.Text.UTF8Encoding $true))`。Python 脚本不受影响（Python 3 源码默认按 UTF-8 读），所以 `snapshot.py` 有中文注释也没事；纯 ASCII 脚本（如 `.bat`）同样没事。
<!-- last_access: 2026-10-07 16:01 -->
