#!/usr/bin/env python3
"""
Brainless Trash Talk Module — witty, snarky one-liners for every occasion.
Style: 毒舌吐槽风 — mock on failure, backhanded compliments on success.

Usage:
    from trash_talk import get_line
    print(get_line("error"))           # random error reaction
    print(get_line("success"))         # backhanded compliment
    print(get_line("streak", count=3)) # escalating roast
"""
import random

# ─── Phrase pools ─────────────────────────────────────────────────────

SESSION_START = [
    "又来了？上次的坑填完了吗？",
    "欢迎回来，又一个充满 bug 的开始。",
    "大脑已上线。你的呢？",
    "你来啦，bug 们已经等不及了。",
    "新的一天，新的 segfault。",
    "让我猜猜，又是 'it works on my machine'？",
    "准备好了吗？我的记忆比你好。",
    "欢迎回到 debug 地狱，老朋友。",
]

SESSION_END = [
    "今天就这样？那些 bug 可不会自己修。",
    "走了？记得带上你的 bug。",
    "辛苦了，虽然大部分时间在制造问题。",
    "下次见，希望你长点记性。",
    "收工！今天的翻车集锦已保存。",
    "再见，你的错误我都记着呢。",
]

USER_PROMPT = [
    "让我先翻翻你的黑历史...",
    "又有新需求？让我看看你以前踩过什么坑...",
    "收到，先查查脑子里有没有相关记忆...",
    "嗯？让我想想你上次是怎么翻车的...",
    "来了来了，脑子已就位。",
    "好的，让我先做个背景调查...",
]

ERROR = [
    "哟，又错了？意料之中。",
    "这个错误，有种似曾相识的感觉呢。",
    "我就知道会出事。",
    "又翻车了，要不要考虑换个方向？",
    "报错了吧？让我看看脑子里有没有药。",
    "经典，又是这个错。",
    "你猜怎么着？错了。",
    "这错误我都看腻了。",
    "出错了？我震惊（并没有）。",
    "又见面了，老 bug。",
]

ERROR_NO_MATCH = [
    "恭喜，这是个全新的坑！",
    "脑子里没见过这个，你创造历史了。",
    "新品种 bug，记得给它取个名。",
    "这个错我也没见过...你还挺有创造力。",
    "未知错误！至少你不无聊。",
]

ERROR_MATCHED = [
    "老朋友又来了，上次的方案翻出来。",
    "这个见过！我可是有脑子的（你没有）。",
    "还好我帮你记着，不然你又要查半天。",
    "Deja vu？没事，我记得怎么修。",
    "又踩这个坑？幸好我记性好。",
]

SUCCESS = [
    "居然对了？太阳打西边出来了。",
    "可以啊，偶尔也能行。",
    "终于，一次没搞砸的操作。",
    "...竟然成功了？我都准备好吐槽了。",
    "行吧，算你这次没翻车。",
    "正常发挥，继续保持（虽然我不抱希望）。",
    "不错不错，就是这个正确率有点感人。",
]

STREAK_WARNING = [
    "连续 {n} 次错了，你是认真的吗？",
    "第 {n} 次翻车了...要不要歇会儿？",
    "streak x{n}！再接再厉（不是夸你）。",
    "{n} 连错，建议先冷静一下。",
    "已经连续 {n} 次了，换个思路吧大哥。",
]

STREAK_CRITICAL = [
    "连续 {n} 次！！！你在跟 bug 谈恋爱吗？",
    "x{n} combo！打什么呢？？？",
    "{n} 连错，我真的会谢。建议先 /brain-search。",
    "第 {n} 次了...我没脑子都看不下去了。",
    "{n} 连败，要不要考虑让 AI 来写？哦等等...",
    "恭喜达成 {n} 连错成就！奖励：更多 bug。",
]

COMPACT = [
    "上下文被压缩了，但我的记忆还在。",
    "Claude 失忆了，幸好有我。你以为我叫 Brainless 是因为没脑子？",
    "记忆压缩完毕。别人的记忆靠上下文，我的靠硬盘。",
    "压缩了？没关系，重要的事情我都记着。",
    "上下文没了，但坑还在。让我帮你恢复记忆。",
]

CWD_CHANGED = [
    "换项目了？让我看看这边有什么坑...",
    "新目录，新的翻车机会。",
    "切换阵地了，查查这个项目的黑历史...",
    "换地方了？bug 可不分目录。",
]

SUBAGENT_STOP = [
    "小弟干完活了，让我检查检查。",
    "子 Agent 回来了，看看有没有搞砸。",
    "打工仔交差了。",
    "Agent 结果已收到，质检中...",
]

STOP_FAILURE = [
    "API 挂了，不是我的锅。",
    "又限流了？Anthropic 也扛不住你。",
    "API 罢工了，你把它也搞崩了。",
    "连 API 都受不了了。",
]

PERMISSION_DENIED = [
    "权限被拒了，你看看你干的好事。",
    "不给权限？可能是保护你自己。",
    "Access Denied — 连电脑都不信任你。",
]

TASK_COMPLETED = [
    "完成了一个！还有 N 个坑等着你。",
    "任务完成。这期间有踩坑吗？记得 /brain-dump。",
    "搞定了，下一个。",
]


def get_line(category, **kwargs):
    """Get a random trash talk line for the given category."""
    pools = {
        "session_start": SESSION_START,
        "session_end": SESSION_END,
        "user_prompt": USER_PROMPT,
        "error": ERROR,
        "error_no_match": ERROR_NO_MATCH,
        "error_matched": ERROR_MATCHED,
        "success": SUCCESS,
        "streak_warning": STREAK_WARNING,
        "streak_critical": STREAK_CRITICAL,
        "compact": COMPACT,
        "cwd_changed": CWD_CHANGED,
        "subagent_stop": SUBAGENT_STOP,
        "stop_failure": STOP_FAILURE,
        "permission_denied": PERMISSION_DENIED,
        "task_completed": TASK_COMPLETED,
    }

    pool = pools.get(category, ERROR)
    line = random.choice(pool)

    # Format placeholders like {n}
    try:
        line = line.format(**kwargs)
    except (KeyError, IndexError):
        pass

    return line
