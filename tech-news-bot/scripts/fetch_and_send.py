"""
Tech News Bot
每天自动搜集全球科技资讯（重点亚洲），发送到 Slack 私信
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

# ── 常量配置 ────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
SLACK_BOT_TOKEN   = os.environ["SLACK_BOT_TOKEN"]
SLACK_USER_ID     = os.environ["SLACK_USER_ID"]   # 你自己的 Slack User ID

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
SLACK_DM_OPEN = "https://slack.com/api/conversations.open"
SLACK_POST    = "https://slack.com/api/chat.postMessage"

MODEL         = "claude-sonnet-4-20250514"
MAX_TOKENS    = 8000
NEWS_COUNT    = 15   # 每日资讯条数

# ── 构建 Prompt ─────────────────────────────────────────────
def build_prompt() -> str:
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    return f"""你是一个专业的科技资讯编辑。今天是 {today}（东京时间）。

请立刻搜集今日全球科技资讯，重点覆盖亚洲（中国、日本、韩国、东南亚），并生成一份完整简报。

## 搜集来源（需覆盖以下类型）
- 中文科技媒体：36Kr、IT之家、虎嗅、少数派、澎湃科技
- 英文科技媒体：TechCrunch、The Verge、Wired、Bloomberg Tech
- 日文媒体：Nikkei Asia、ITmedia、ASCII.jp
- 社交热点：微博科技热搜、X/Twitter 科技 Trending

## 输出格式（严格按照以下结构，共 {NEWS_COUNT} 条）

---
📅 *{today} 全球科技资讯简报*
━━━━━━━━━━━━━━━━━━━━━━━

（每条按以下格式输出，按热度从高到低排列）

*🔥 第N条 | 热度评级：⭐⭐⭐⭐⭐*
*【标题】*（中文标题）
*【热度依据】* 例：微博热搜第X位 / X平台趋势 / 多家媒体头条转载
*【摘要】* 2-3句话说清核心内容
*【来源 & 链接】* 媒体名称 + 原文链接
*【业内视角】* 该新闻的行业意义、专家关注点、或展现的趋势（2-3句）

---

## 热度评级说明
⭐⭐⭐⭐⭐ = 多平台爆发式讨论 / 行业重大事件
⭐⭐⭐⭐ = 主流科技媒体头条
⭐⭐⭐ = 专业圈层高度关注
⭐⭐ = 值得追踪的新兴动态

## 分类标签（每条资讯标注所属类别）
可选：#AI #芯片 #新能源 #消费电子 #政策监管 #初创融资 #宇宙航天 #机器人 #区块链 #其他

请直接开始输出简报，不要有任何前言。"""

# ── 调用 Claude API ─────────────────────────────────────────
def fetch_news_from_claude() -> str:
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": build_prompt()}],
    }

    print("📡 正在调用 Claude API 搜集资讯...")
    resp = requests.post(ANTHROPIC_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()

    data = resp.json()
    # 提取所有 text 类型的 content block
    texts = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
    result = "\n".join(texts).strip()
    print(f"✅ Claude 返回内容长度：{len(result)} 字符")
    return result

# ── 发送到 Slack DM ─────────────────────────────────────────
def get_dm_channel(user_id: str) -> str:
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    resp = requests.post(SLACK_DM_OPEN, headers=headers, json={"users": user_id})
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack DM open 失败: {data.get('error')}")
    return data["channel"]["id"]


def send_to_slack(text: str) -> None:
    channel_id = get_dm_channel(SLACK_USER_ID)
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    # Slack 单条消息上限约 3000 字符，超过需分段发送
    chunk_size = 2800
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    total  = len(chunks)

    print(f"📤 共分 {total} 段发送到 Slack...")
    for idx, chunk in enumerate(chunks, 1):
        # 第一段加标题 header block，其余直接文本
        if idx == 1:
            payload = {
                "channel": channel_id,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "🌏 每日科技资讯简报", "emoji": True},
                    },
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": chunk}},
                ],
            }
        else:
            payload = {
                "channel": channel_id,
                "blocks": [
                    {"type": "section", "text": {"type": "mrkdwn", "text": chunk}},
                ],
            }
            if idx == total:
                payload["blocks"].append({
                    "type": "context",
                    "elements": [{"type": "mrkdwn", "text": f"_由 Tech News Bot 自动生成 · {datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M')} JST_"}],
                })

        resp = requests.post(SLACK_POST, headers=headers, json=payload)
        resp.raise_for_status()
        result = resp.json()
        if not result.get("ok"):
            raise RuntimeError(f"Slack 发送失败 (段 {idx}/{total}): {result.get('error')}")
        print(f"  ✓ 第 {idx}/{total} 段发送成功")


# ── 主入口 ──────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("🚀 Tech News Bot 启动")
    jst = timezone(timedelta(hours=9))
    print(f"⏰ 当前东京时间：{datetime.now(jst).strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    news_text = fetch_news_from_claude()
    send_to_slack(news_text)

    print("=" * 50)
    print("✅ 全部完成！资讯已推送到 Slack 私信")
    print("=" * 50)


if __name__ == "__main__":
    main()
