"""
Tech News Bot — Gemini 免费版
每天自动搜集全球科技资讯（重点亚洲），发送到 Slack 私信
使用 Google Gemini API（免费额度：每天1500次，完全够用）
"""

import os
import json
import requests
from datetime import datetime, timezone, timedelta

# ── 常量配置 ────────────────────────────────────────────────
GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_USER_ID   = os.environ["SLACK_USER_ID"]

# Gemini 2.0 Flash — 免费且支持 Google Search grounding
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
    f"?key={GEMINI_API_KEY}"
)

SLACK_DM_OPEN = "https://slack.com/api/conversations.open"
SLACK_POST    = "https://slack.com/api/chat.postMessage"

NEWS_COUNT = 15  # 每日资讯条数


# ── 构建 Prompt ─────────────────────────────────────────────
def build_prompt() -> str:
    jst   = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    return f"""你是一个专业的科技资讯编辑。今天是 {today}（东京时间）。

请利用 Google Search 搜集今日全球科技资讯，重点覆盖亚洲（中国、日本、韩国、东南亚），生成一份完整简报。

## 搜集来源（需覆盖以下类型）
- 中文科技媒体：36Kr、IT之家、虎嗅、少数派、澎湃科技
- 英文科技媒体：TechCrunch、The Verge、Wired、Bloomberg Tech
- 日文媒体：Nikkei Asia、ITmedia、ASCII.jp
- 社交热点：微博科技热搜、X/Twitter 科技 Trending

## 输出格式（严格按照以下结构，共 {NEWS_COUNT} 条，按热度从高到低排列）

---
📅 *{today} 全球科技资讯简报*
━━━━━━━━━━━━━━━━━━━━━━━

*🔥 第1条 | 热度：⭐⭐⭐⭐⭐ | #分类标签*
*【标题】* 资讯标题
*【热度依据】* 例：微博热搜第X位 / 多家主流媒体同日头条
*【摘要】* 2-3句话说清核心内容
*【来源 & 链接】* 媒体名称：链接URL
*【业内视角】* 该新闻的行业意义、专家关注点或趋势判断（2-3句）

（以下按同样格式输出第2条至第{NEWS_COUNT}条）

---

## 热度评级说明
⭐⭐⭐⭐⭐ = 多平台爆发式讨论 / 行业重大事件
⭐⭐⭐⭐   = 主流科技媒体头条
⭐⭐⭐     = 专业圈层高度关注
⭐⭐       = 值得追踪的新兴动态

## 分类标签
#AI #芯片 #新能源 #消费电子 #政策监管 #初创融资 #航天 #机器人 #其他

请直接输出简报内容，不要有任何前言或解释。"""


# ── 调用 Gemini API（启用 Google Search grounding）──────────
def fetch_news_from_gemini() -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": build_prompt()}]}
        ],
        # Google Search grounding — 让 Gemini 实时搜索今日新闻
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 8192,
        },
    }

    print("📡 正在调用 Gemini API 搜集资讯...")
    resp = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=120)

    # 错误处理
    if resp.status_code != 200:
        print(f"❌ Gemini API 错误 {resp.status_code}: {resp.text}")
        resp.raise_for_status()

    data = resp.json()

    # 提取文字内容
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"解析 Gemini 响应失败: {e}\n原始响应: {json.dumps(data, ensure_ascii=False)[:500]}")

    print(f"✅ Gemini 返回内容长度：{len(text)} 字符")
    return text.strip()


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

    jst = timezone(timedelta(hours=9))
    timestamp = datetime.now(jst).strftime("%Y-%m-%d %H:%M")

    # Slack 单条消息上限约 3000 字符，超过需分段
    chunk_size = 2800
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    total = len(chunks)

    print(f"📤 共分 {total} 段发送到 Slack...")

    for idx, chunk in enumerate(chunks, 1):
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
            payload = {"channel": channel_id, "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": chunk}},
            ]}

        # 最后一段加时间戳
        if idx == total:
            payload["blocks"].append({
                "type": "context",
                "elements": [{"type": "mrkdwn",
                               "text": f"_由 Tech News Bot (Gemini) 自动生成 · {timestamp} JST_"}],
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
    print("🚀 Tech News Bot (Gemini 免费版) 启动")
    jst = timezone(timedelta(hours=9))
    print(f"⏰ 当前东京时间：{datetime.now(jst).strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    news_text = fetch_news_from_gemini()
    send_to_slack(news_text)

    print("=" * 50)
    print("✅ 全部完成！资讯已推送到 Slack 私信")
    print("=" * 50)


if __name__ == "__main__":
    main()
