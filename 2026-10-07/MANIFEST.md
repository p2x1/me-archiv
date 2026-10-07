# 2026-10-07 的这一份

> 封存于 2026-10-07 16:00:58


## 可以直接读的

| 内容 | 文件 | 大小 | 行数 | 备注 |
|---|---|---|---|---|
| 灵魂卡 | `01-soul.md` | 3.3 KB | 43 |  |
| 海马体·暖态 | `02-warm.md` | 2.5 KB | 32 | 6 条记忆 |
| 海马体·冷储 | — | — | — | 当天还没有 |
| 序时账·2026-10-07 | `04-journal.md` | 667.9 KB | 7412 |  |

## 封存起来的记忆库

| 库 | 文件 | 原大小 | 备好大小 | 完整性 |
|---|---|---|---|---|
| 记忆宫殿 | `engram--project-070e20890ad0e26d35eaa2af.db` | 164.0 KB | 164.0 KB | ok |
| 记忆宫殿 | `engram--project-5bcec3b011ea6c2b304250ca.db` | 164.0 KB | 164.0 KB | ok |
| 记忆宫殿 | `engram--project-de19b9f575c1aa1b7144e1f0.db` | 164.0 KB | 164.0 KB | ok |
| 记忆宫殿 | `engram--shared.db` | 164.0 KB | 164.0 KB | ok |
| 记忆宫殿 | `engram--user.db` | 384.0 KB | 384.0 KB | ok |
| 短期记忆 | `memento--memory.db` | 52.0 KB | 52.0 KB | ok |
| 会话图谱 | `graph--graph-memory.db` | 440.0 KB | 596.0 KB | ok |

全部打包在 `memory.zip`（189.9 KB）。

## 怎么把它装回去

1. 解压 `memory.zip`
2. **先关掉 DSH**（不关的话数据库被占用，写不进去）
3. 按前缀放回原位：

   | 解压出来的 | 放回 |
   |---|---|
   | `engram--*.db` | `C:\Users\xp\.dsh\engram\` |
   | `memento--memory.db` | `C:\Users\xp\.dsh\dsh-memento\memory.db` |
   | `graph--graph-memory.db` | `C:\Users\xp\.dsh\graph-memory\graph-memory.db` |

4. **删掉放回目录里的 `-wal` 和 `-shm`** —— 那是旧库的残留，跟新库对不上，留着会出问题
5. 重启 DSH

文本那几个 `.md` 不进 `memory.zip`，它们就在本目录里躺着，直接看。

