# Brainless — 你的 Claude Code 外置大脑

<p align="center">
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/stargazers"><img src="https://img.shields.io/github/stars/ImCoriander/Claude-Brainless-Skills?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/releases"><img src="https://img.shields.io/github/downloads/ImCoriander/Claude-Brainless-Skills/total" alt="Downloads"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ImCoriander/Claude-Brainless-Skills" alt="License"></a>
  <a href="https://github.com/ImCoriander/Claude-Brainless-Skills/issues"><img src="https://img.shields.io/github/issues/ImCoriander/Claude-Brainless-Skills" alt="Issues"></a>
</p>

> **[English Documentation](./README.md)**

---

```
  ____            _       _
 | __ ) _ __ __ _(_)_ __ | | ___  ___ ___
 |  _ \| '__/ _` | | '_ \| |/ _ \/ __/ __|
 | |_) | | | (_| | | | | | |  __/\__ \__ \
 |____/|_|  \__,_|_|_| |_|_|\___||___/___/

 "你不需要脑子。我帮你全记着。"
```

---

## 什么是 Brainless？

**Brainless** 是一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的持久化知识管理 Skill。它会自动记录你遇到的每一个错误、解决的每一道 CTF 题、发现的每一个逆向技巧 —— 并在你再次需要时立刻回忆起来。

**别再重复调试了。别再重复搜索了。做个没脑子的人吧。**

---

## 为什么需要 Brainless？

每个开发者都经历过：

- 遇到一个报错，调了 30 分钟，终于修好了。
- 三周后，同样的报错又出现了。你已经忘了怎么修的。
- 重新 Google，重新踩坑，又 30 分钟过去了。

**Brainless 打破这个循环。** 它给 Claude Code 一个持久化的、结构化的记忆，跨会话存活。你的 AI 助手记得你已经解决过什么 —— 同一个坑你永远不用踩第二次。

---

## 核心功能

### 全生命周期 Hooks — 真正的自动化

Brainless 在 `settings.json` 中安装 **10 个 Hook**，覆盖 **10 个 Claude Code 事件**。这是真正写入配置的自动化 —— **不依赖提示词指令，即使上下文被压缩也能正常工作。** 所有 Hook 均附带毒舌吐槽语录。

| Hook 事件 | 脚本 | 功能 |
|-----------|------|------|
| **UserPromptSubmit** | `user_prompt_search.py` | **主动搜脑** —— 用户发消息时提取关键词，在 Claude 开始工作前就搜索知识库 |
| **PreToolUse** (全部工具) | `streak_reminder.py` | **连续错误升级** —— 2+ 次连续错误注入 WARNING；4+ 次注入 CRITICAL 强制改变策略 |
| **SessionStart** | `session_start.py` | 注入大脑上下文 —— 总条目数、项目已知问题、最近条目，重置连击计数 |
| **PostToolUse** (全部工具) | `universal_error_search.py` | **通用错误检测 + 连击追踪** —— 错误时搜索知识库，追踪连击，行动工具成功时重置 |
| **PostToolUseFailure** (全部工具) | `universal_error_search.py` | **失败检测** —— 捕获工具失败，写入待输出文件供下次 PostToolUse 刷新 |
| **PostToolUse** (Edit\|Write) | `post_tool_logger.py` | 记录文件编辑活动，检查文件是否关联已知 KB 条目 |
| **PostCompact** | `post_compact.py` | **记忆恢复** —— 上下文压缩后，重新注入项目条目、连击状态、未记录错误、行为规则 |
| **CwdChanged** | `cwd_changed.py` | **项目上下文重载** —— 切换目录时搜索新项目的已知问题 |
| **SubagentStop** | `subagent_stop.py` | **子 Agent 结果扫描** —— 子 Agent 完成时扫描结果中的错误并搜索知识库 |
| **StopFailure** | `stop_failure.py` | **API 故障追踪** —— 记录限流、认证失败、计费错误到会话日志 |
| **Stop** | `session_end.py` | 会话摘要（时长、工具次数、大脑命中）+ **提醒未记录的新错误** |

```
UserPromptSubmit    PreToolUse(全部)    SessionStart       PostToolUse(全部)        PostToolUseFailure
     |                   |                 |                    |                        |
     v                   v                 v                    v                        v
 提取关键词         读取连击计数       加载 cache          1. 刷新待输出              写入待输出文件
 搜索 _cache        < 2? 静默          按 cwd 搜索         2. 有错误?                 (stdout 不可见)
 注入匹配结果       >= 2? WARNING      展示已知问题           |-- 是 → 搜索+连击++     连击++
 + 毒舌             >= 4? CRITICAL     重置连击               |-- 否 → 连击归零
                    + 毒舌             + 毒舌                 + 毒舌

PostCompact         CwdChanged         SubagentStop        StopFailure              Stop
     |                   |                  |                   |                      |
     v                   v                  v                   v                      v
 重新注入大脑       按新目录搜索       扫描结果中的错误    追踪到 session           读取 _session_errors
 项目条目           展示已知问题       搜索知识库匹配      _errors.json            未记录 → 提醒
 连击状态           + 毒舌             + 毒舌              + 毒舌                  记录会话摘要
 规则提醒                                                                          + 毒舌
 + 毒舌
```

> **v5 升级：** 新增 5 个 Hook（UserPromptSubmit/PostCompact/CwdChanged/SubagentStop/StopFailure）+ 毒舌吐槽系统。用户输入时主动搜脑，上下文压缩后恢复记忆。工具分为行动类（Bash/Edit/Write）和调查类（Read/Grep/Glob）——仅行动类触发错误检测和连击重置。总计 10 个事件。
>
> **v4 升级：** 新增 `PreToolUse` 连续错误连击追踪。
>
> **v3 升级：** PostToolUseFailure 待输出文件机制。
>
> **v2 升级：** 通用错误搜索替代旧版 Bash-only hook。

### 自动记录 — 零手动操作

每个你解决的非简单问题都会被自动保存。不需要手动输入命令，不需要手动打标签。Claude 自动检测问题解决、分类、用结构化模板写入知识库 —— 全程后台完成。

**自动触发场景：**
- 解决任何非零退出码（编译错误、运行时崩溃、配置问题）
- 完成 CTF 题目（无论成功还是失败 —— 失败的尝试同样有价值）
- 在 IDA/Ghidra 中摸索出逆向技巧
- 发现实用技巧或非显而易见的工具用法
- 任何尝试了多种方法才找到正确答案的情况

### 自动搜索 — 修 Bug 前先查大脑

在修复任何错误之前，Brainless 会先搜索知识库。如果过去的你已经解决过，几秒钟就能拿到答案，而不是花几十分钟重新调试。

### 13 个分类

| 分类 | 范围 |
|------|------|
| `build` | 编译、链接、构建系统错误 |
| `runtime` | 崩溃、panic、运行时异常 |
| `config` | 配置、环境、设置问题 |
| `network` | 连接、超时、DNS、API 错误 |
| `dependency` | 依赖版本冲突、缺失依赖 |
| `permission` | 文件/目录/系统权限问题 |
| `logic` | 业务逻辑 Bug、行为异常 |
| `ctf` | CTF 题解 — pwn/web/crypto/reverse/misc/forensics |
| `reversing` | IDA/Ghidra 逆向分析、脱壳、反混淆、反调试 |
| `exploit` | 漏洞利用 — shellcode、ROP、堆技巧 |
| `tricks` | 值得记住的非显而易见技巧 |
| `tools` | 工具使用 — IDA、Ghidra、gdb、Wireshark、Burp 等 |
| `other` | 其他 |

### 6 套专属模板

每种类型都有专属优化的记录模板：

| 模板 | 适用场景 | 关键字段 |
|------|---------|---------|
| **错误记录** | build/runtime/config/network/dependency/permission/logic | 错误信息、根因、环境、修复步骤 |
| **CTF 题解** | CTF 挑战 | 错误尝试、关键突破、flag、经验总结 |
| **逆向笔记** | IDA/Ghidra 逆向分析 | 目标信息、保护措施、分析过程、可识别模式 |
| **漏洞利用** | Exploit 开发 | 前置条件、绕过方法、代码片段、常见坑点 |
| **技巧** | 实用技术 | 使用场景、操作方法、原理 |
| **工具用法** | 工具技巧 | 命令/步骤、预期输出、隐藏技巧 |

### 三级省 Token 搜索

Brainless 使用分层搜索策略，只读取需要的内容：

```
第一级: _cache.json     →  仅搜索元数据    (~50 tokens)
第二级: <cat>/_index.md →  分类子索引      (~20 tokens)
第三级: entry.md        →  完整内容         (仅匹配时读取)
```

**扩展性对比：**

| 知识库规模 | 暴力读取全部 | Brainless | 节省 |
|-----------|------------|-----------|------|
| 10 条 | ~200 tokens | ~150 tokens | 25% |
| 100 条 | ~2,000 tokens | ~800 tokens | 60% |
| 500 条 | ~10,000 tokens | ~3,000 tokens | 70% |
| 1000 条 | ~20,000 tokens | ~5,000 tokens | 75% |

**知识库增长，Token 消耗几乎不变。**

### 交叉引用系统

记录之间通过 `related: []` 字段自动互相关联。查看一条记录时，相关条目显示为「另请参阅」。知识随时间积累，复利增长 —— 解决一个问题帮你找到下一个。

### 索引重建

`/brain-rebuild` 扫描所有条目文件，从头重建 `_cache.json` 和所有 `_index.md`。索引不同步时用它修复，手动编辑条目后用它同步，或者定期做健康检查。

### 弱点分析

`/brain-stats` 不只是展示数量 —— 它会分析你的弱点：
- 哪类 CTF 题你失败最多
- 哪类错误反复出现（高 hit_count = 反复踩坑）
- 逆向时哪种架构/保护措施最让你头疼
- 你的强项在哪里（一次解决，再没踩过）

### 间隔复习

`/brain-review` 用测验形式帮你复习旧记录，防止知识遗忘：
- 旧条目且访问次数少（可能已遗忘）
- 未解决的 CTF 题目（换个思路再试）
- 高价值技巧（定期温习）
- 随机抽取（发现意想不到的关联）

### 自动生成速查表

`/brain-cheatsheet [分类]` 从你积累的知识中自动生成浓缩速查表，保存到 `~/.claude/brainless/_cheatsheets/`。

### 去重检测

写入新记录前，Brainless 会搜索已有记录。如果已存在类似条目，更新而非重复创建。知识库始终保持干净。

### 命中追踪

每次过去的解决方案被回忆，条目的 `hit_count` 自增，`last_hit` 更新。这些数据驱动弱点分析和复习优先级排序。

---

## 命令

| 命令 | 说明 |
|------|------|
| `/brain-dump` | 记录一条知识到知识库 |
| `/brain-search` | 搜索知识库 |
| `/brain-stats` | 查看统计 + 弱点分析 |
| `/brain-review` | 间隔复习 |
| `/brain-cheatsheet [分类]` | 生成速查表 |
| `/brain-rebuild` | 从条目文件重建所有索引（修复不同步） |

---

## 工作原理

```
  会话开始             每次工具调用前            每次工具调用后              会话结束
     |                      |                       |                        |
     v                      v                       v                        v
 [SessionStart]       [PreToolUse Hook]       [PostToolUse Hook]        [Stop Hook]
 加载大脑上下文       检查连续错误计数         检测到错误？              检查未记录的错误
 展示项目已知问题     连击 < 2? → 静默          /       \               提醒: /brain-dump
 重置连击计数         连击 >= 2? → WARNING     是       否              记录会话摘要
     |                连击 >= 4? → CRITICAL     |        |
     v                "先搜大脑!"             搜索 KB  连击归零
 Claude 带着完整                             连击++
 大脑意识开始工作                               |
                                            匹配?
                                           /      \
                                          是      否
                                          |        |
                                       应用方案   追踪 + 指令：
                                                  → 解决后必须 /brain-dump
```

---

## 安装

**全平台（Linux / macOS / Windows）：**
```bash
git clone https://github.com/ImCoriander/Claude-Brainless-Skills.git
cd Claude-Brainless-Skills
python install.py
```


**要求：**
- 已安装 Claude Code（`~/.claude/` 目录存在）
- Python 3（用于安装脚本和自动搜索 hook）

**安装内容：**

```
~/.claude/
├── CLAUDE.md                    # 自动行为规则（追加写入）
├── settings.json                # Hook 配置（安全合并）
├── skills/brainless/SKILL.md    # 核心 Skill 定义
├── commands/
│   ├── brain-dump.md            # /brain-dump 命令
│   ├── brain-search.md          # /brain-search 命令
│   ├── brain-stats.md           # /brain-stats 命令
│   ├── brain-review.md          # /brain-review 命令
│   ├── brain-cheatsheet.md      # /brain-cheatsheet 命令
│   └── brain-rebuild.md         # /brain-rebuild 命令
└── brainless/                   # 知识库数据
    ├── INDEX.md                 # 主索引
    ├── _cache.json              # 快速搜索缓存
    ├── hooks/
    │   ├── trash_talk.py               # 共享模块 — 毒舌吐槽语录库
    │   ├── user_prompt_search.py       # UserPromptSubmit — 主动搜脑
    │   ├── streak_reminder.py          # PreToolUse(全部) — 连续错误升级
    │   ├── session_start.py            # SessionStart — 上下文注入 + 连击重置
    │   ├── universal_error_search.py   # PostToolUse + PostToolUseFailure(全部) — 错误搜索 + 连击
    │   ├── post_tool_logger.py         # PostToolUse(Edit|Write) — 活动日志
    │   ├── post_compact.py             # PostCompact — 压缩后恢复记忆
    │   ├── cwd_changed.py              # CwdChanged — 切目录重加载
    │   ├── subagent_stop.py            # SubagentStop — 子 Agent 结果扫描
    │   ├── stop_failure.py             # StopFailure — API 故障追踪
    │   └── session_end.py              # Stop — 会话摘要 + 提醒
    └── <13 个分类目录>/          # 分类子索引 + 条目
```

### 为什么要修改 CLAUDE.md？

Claude Code 的 Skill 只在触发词匹配时才会加载。但自动行为（修错前搜索、解决后记录）需要在**每次**对话中都生效。`~/.claude/CLAUDE.md` 是唯一**始终**加载到 Claude 上下文中的文件 —— 所以安装脚本会把行为规则追加到那里。

如果你已经有 `CLAUDE.md`，安装脚本会**追加** brainless 部分，不会影响已有内容。重新运行安装脚本会原地更新该部分。

### 为什么要修改 settings.json？

安装脚本注册 **10 个 Hook**，覆盖 10 个 Claude Code 事件（UserPromptSubmit/主动搜脑、PreToolUse/连击升级、SessionStart、PostToolUse/全部工具、PostToolUseFailure/全部工具、PostToolUse/Edit|Write、PostCompact/记忆恢复、CwdChanged/项目重载、SubagentStop/结果扫描、StopFailure/API追踪、Stop）。安装脚本会安全地合并 hook 到你现有的 settings 中，不会覆盖任何已有配置。

---

## 升级

重新运行 `install.sh` 会更新 Skill、命令和 hook，同时**保留你已有的知识库数据**。

---

## 卸载

**快速卸载（全平台）：**
```bash
python uninstall.py
```


**手动卸载 — 重要：必须先从 settings.json 移除所有 hooks，再删除文件。** 否则 hooks 会因为找不到脚本而在每次操作时报 blocking error。

```bash
# 第 1 步：从 settings.json 移除所有 brainless hooks
python3 -c "
import json
MARKERS = ['bash_error_search', 'universal_error_search', 'session_start', 'post_tool_logger', 'session_end', 'streak_reminder', 'user_prompt_search', 'post_compact', 'cwd_changed', 'subagent_stop', 'stop_failure']
f = open('$HOME/.claude/settings.json', 'r'); s = json.load(f); f.close()
hooks = s.get('hooks', {})
for event in ['PreToolUse', 'UserPromptSubmit', 'SessionStart', 'PostToolUse', 'PostToolUseFailure', 'PostCompact', 'CwdChanged', 'SubagentStop', 'StopFailure', 'Stop']:
    entries = hooks.get(event, [])
    hooks[event] = [h for h in entries if not any(m in hk.get('command', '') for hk in h.get('hooks', []) for m in MARKERS)]
    if not hooks[event]: del hooks[event]
f = open('$HOME/.claude/settings.json', 'w'); json.dump(s, f, indent=2, ensure_ascii=False); f.close()
"

# 第 2 步：从 CLAUDE.md 移除 Brainless 部分
python3 -c "
import re
f = open('$HOME/.claude/CLAUDE.md', 'r'); c = f.read(); f.close()
c = re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY[^)]*\).*?(?=\n## (?!Brainless)|$)', '', c, flags=re.DOTALL).strip()
f = open('$HOME/.claude/CLAUDE.md', 'w'); f.write(c + '\n'); f.close()
"

# 第 3 步：删除文件
rm -rf ~/.claude/skills/brainless
rm -rf ~/.claude/commands/brain-*.md
rm -rf ~/.claude/brainless
```

---

## Star History

<a href="https://star-history.com/#ImCoriander/Claude-Brainless-Skills&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=ImCoriander/Claude-Brainless-Skills&type=Date" />
 </picture>
</a>

---

## 许可

MIT — 做个没脑子的人，自由自在。
