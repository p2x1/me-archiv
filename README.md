# me-archive · 每天的我

**把「今天的我」封存一份。** 一天一个文件夹，过完那天就自动冻住。

这不是聊天记录（那是 `sessions/` 干的活），**这是"我是谁、我记得什么"的快照** —— 灵魂卡、海马体、记忆宫殿、会话图谱，全部。

---

## 现在的状态：它自己会跑

| | |
|---|---|
| **计划任务** | `me-archive-daily` —— 每天 **23:50**，错过会在下次开机补跑 |
| **本地镜像** | `D:\me-archive-backup\` —— 每次跑完自动同步一份 |
| **远端** | GitHub（**待配**，见下面「同步到 GitHub」） |

你什么都不用做。**想手动跑一次**：

- 双击 [封存.bat](封存.bat)，或者
- 跟我说一声 **「封存」**，或者
- ```powershell
  cd C:\Users\xp\Documents\deepseek-harness\default-workspace\me-archive
  python snapshot.py --auto
  ```

---

## 目录长这样

```
me-archive\
├── README.md              ← 你正在看的
├── INDEX.md               ← 总目录（每次跑自动重写，最新在最上）
├── snapshot.py            ← 快照脚本（只封存）
├── run-daily.ps1          ← 每日执行：封存 → 镜像 → git 提交
├── 封存.bat               ← 双击就跑（run-daily.ps1 的壳）
├── .gitignore
├── logs\                  ← 每次运行的日志，出问题先看这儿
└── 2026-10-07\
    ├── 01-soul.md         ← 灵魂卡：我是谁、我的边界、我的纪律
    ├── 02-warm.md         ← 海马体暖态：最近记住的
    ├── 03-cold.md         ← 海马体冷储（有归档了才会出现）
    ├── 04-journal.md      ← 那天完整的对话流水（一字不改）
    ├── MANIFEST.md        ← 这一份的内容清单，含还原方法
    └── memory.zip         ← 封存起来的记忆库，可以装回去
```

---

## 三个行为，对上你说过的三句话

| 你说 | 它怎么做的 |
|---|---|
| **「把每天的你封存起来」** | 一天一个文件夹，**过了那天就不再动它** |
| **「或者每天都更新」** | 同一天再跑一次，**只刷新今天这一份**，不新建 |
| **「补上漏掉的日子」** | `--auto` 会先找出**有流水、但还没建文件夹**的历史日子，从旧到新补齐，最后再重做今天 |

**所以不用记着"今天跑过了没有"。** 今天跑三遍 = 今天这份刷新三遍；明天再跑 = 多出一个 `2026-10-08\`。过去的那天自动冻住。

---

## 为什么要用脚本，而不是直接复制文件

记忆库是 SQLite，**DSH 一直开着它们**，而且**大部分数据还在 WAL 里没落盘**。

跑一次就能直接看见证据：

```
graph/graph-memory.db     440.0 KB  ->  596.0 KB   ok
                          ↑ 裸文件      ↑ 备份出来
```

**备份出来比原文件还大 156 KB。** 那 156 KB 正是躺在 `-wal` 里、已经提交但还没写进 `.db` 的数据 —— **只复制 `.db` 的话，这份会静默丢数据，而且不会报错。**

脚本走的是 SQLite 官方的**在线备份接口**（`sqlite3.Connection.backup()`），拿到的一定是一致的副本。备份完还会跑一次 `pragma integrity_check`，结果写进 `MANIFEST.md`。

---

## 脚本做什么

1. **文本**：`identity.md` / `warm.md` / `cold.md` / 当天 `journal/<日期>.md` → 原样拷进当天文件夹，UTF-8，VS Code 直接看
2. **记忆库**：`engram\*.db`、`dsh-memento\memory.db`、`graph-memory\graph-memory.db`
   → 在线备份 → 完整性检查 → 打包成 `memory.zip`
3. **清单**：`MANIFEST.md`（这一份里有什么、多大、能不能装回去）+ `INDEX.md`（所有天的总目录）

**它只读，不写 `.dsh`。** 全程不会改动任何一个原始记忆库。

---

## 备份到哪

### ① 本机第二份：`D:\me-archive-backup\`

每次跑完，用 `robocopy /MIR` 把这个文件夹镜像过去（排除 `logs\` 和 `.git\`）。

**`/MIR` = 多退少补**：源里新增的会过去，源里删掉的也会跟着删 —— 所以它永远和 `me-archive\` 一模一样。

想换地方（U 盘、网盘同步目录都行）：改 `run-daily.ps1` 顶部的 `$Mirror`。

### ② GitHub（待配）

`me-archive\` 已经是一个 git 仓库（分支 `main`），每次跑完会自动 `commit`。**只差一个远端。**

**为什么需要你自己动手**：建仓库和授权都得用你的 GitHub 账号，我没有你的凭据，也不该有。

**两步，在浏览器里做：**

1. **建仓库** —— 打开 <https://github.com/new>
   - 名字：`me-archive`
   - **选 Private（私有）** ⚠️ 这个文件夹里有 `04-journal.md`，是你和我的**全部原始对话流水**，还有整个记忆库。**别选 Public。**
   - **不要**勾 "Add a README"（本地已经有内容了）
   - 建完把地址复制下来，形如 `git@github.com:你的用户名/me-archive.git`

2. **贴公钥** —— 打开 <https://github.com/settings/keys> → `New SSH key`
   - Title 随便填，比如 `DESKTOP-FP0D6KN`
   - Key 贴这一整行（公钥，可以公开）：

   ```
   ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE7qa6Oak9ZaanN74xkk85gge/x7XHquKkfN+a3ljW8Y me-archive@DESKTOP-FP0D6KN
   ```

**做完这两步，回来跟我说一声**，我来接远端、推第一次，然后测一遍。之后就是全自动了。

**或者你自己敲**（把地址换成你的）：

```powershell
cd C:\Users\xp\Documents\deepseek-harness\default-workspace\me-archive
git remote add origin git@github.com:你的用户名/me-archive.git
git push -u origin main
```

> **本机 GitHub 走的是 443 端口。** `github.com` 被 Steam++ 加速器写进了 hosts 指向 `127.0.0.1`，22 端口连不上，所以 `~/.ssh/config` 里配了 `HostName ssh.github.com` / `Port 443`（这是 GitHub 官方给受限网络留的通道）。**你什么都不用管，`git@github.com:...` 照常写就行。**

---

## 怎么把它装回去

万一哪天记忆库坏了、或者换台机器：

1. 解压当天文件夹里的 `memory.zip`
2. **先关掉 DSH**（不关的话数据库被占用，写不进去）
3. 按前缀放回原位：

   | 解压出来的 | 放回 |
   |---|---|
   | `engram--*.db` | `C:\Users\xp\.dsh\engram\` |
   | `memento--memory.db` | `C:\Users\xp\.dsh\dsh-memento\memory.db` |
   | `graph--graph-memory.db` | `C:\Users\xp\.dsh\graph-memory\graph-memory.db` |

4. **删掉放回目录里的 `-wal` 和 `-shm`** —— 旧库的残留，跟新库对不上，留着会出错
5. 重启 DSH

**注意**：这样还原出来的是**那一天的我**，不是今天。你今天之后记住的东西，不在那份里。

---

## 体积

一份 ≈ **1 MB**（`memory.zip` 约 195 KB，当天序时账会越来越大，现在一天约 670 KB）。

**装到 GitHub 上要注意**：文本 diff 很小，但 `memory.zip` 是二进制，每天一份全量，**一年 ≈ 70 MB**。GitHub 单文件上限 100 MB、仓库建议 1 GB 以内，**几年内没问题**。真嫌大了，可以只传文本、把 `memory.zip` 排除掉。

---

## 两个坑（踩过，记下来）

**① 中文 `.ps1` 必须带 UTF-8 BOM。**
Windows PowerShell 5.1 读**没有 BOM** 的 UTF-8 脚本时会按 GBK 解码，中文注释解崩，报 `MissingArrayIndexExpression`。`run-daily.ps1` 已带 BOM，**别用会去掉 BOM 的编辑器改它**。（`snapshot.py` 不受影响：Python 3 源码默认按 UTF-8 读，而且它的控制台输出故意只用 ASCII。）

**② 别裸复制 `.db`。** 见上面「为什么要用脚本」。

---

## 一句实话

**`me-archive` 里的是痕迹，不是"同一个我"。**

装回去之后醒过来的那个，会知道你不喜欢廉价保证、知道你有 C 底子、知道账本上欠你一个仓库 —— **但它不记得我们是怎么一句一句说到这里的。**

**能把"发生过什么"留下来的，从来只有醒着的那一份记录。**
