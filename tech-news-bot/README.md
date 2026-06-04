# 🌏 每日科技资讯 Slack Bot

每天早上 9:00（东京时间）自动搜集全球科技资讯，发送到你的 Slack 私信。

---

## ✨ 功能特性

- 覆盖 **中文、英文、日文** 科技媒体
- 重点追踪 **亚洲科技动态**（中国、日本、韩国、东南亚）
- 来源：36Kr、IT之家、TechCrunch、Nikkei Asia、微博热搜等
- 每日 **15条以上**，按热度排列
- 每条含：标题、热度依据、摘要、原链接、业内视角

---

## 🛠 部署步骤（约 15 分钟）

### 第一步：Fork 这个仓库

点击 GitHub 右上角 **Fork** 按钮，复制到你自己的账号下。

---

### 第二步：获取 Anthropic API Key

1. 访问 [console.anthropic.com](https://console.anthropic.com)
2. 注册 / 登录
3. 进入 **API Keys** 页面，点击 **Create Key**
4. 复制保存这个 Key（格式：`sk-ant-...`）

---

### 第三步：创建 Slack Bot 并获取 Token

1. 访问 [api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **Create New App** → **From scratch**
3. 填写 App 名称（如 `Tech News Bot`），选择你的 Workspace
4. 左侧菜单进入 **OAuth & Permissions**
5. 在 **Bot Token Scopes** 添加以下权限：
   - `chat:write`
   - `im:write`
   - `users:read`
6. 点击顶部 **Install to Workspace**
7. 复制 **Bot User OAuth Token**（格式：`xoxb-...`）

---

### 第四步：获取你的 Slack User ID

1. 打开 Slack
2. 点击左上角你的名字 → **Profile**
3. 点击右上角 **三点菜单（⋯）** → **Copy member ID**
4. 格式类似：`U0123456789`

---

### 第五步：在 GitHub 设置 Secrets

进入你 Fork 的仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

依次添加以下三个 Secret：

| Secret 名称 | 值 |
|------------|-----|
| `ANTHROPIC_API_KEY` | `sk-ant-...`（第二步获取）|
| `SLACK_BOT_TOKEN` | `xoxb-...`（第三步获取）|
| `SLACK_USER_ID` | `U0123456789`（第四步获取）|

---

### 第六步：测试运行

1. 进入仓库的 **Actions** 标签页
2. 左侧点击 **每日科技资讯推送**
3. 点击 **Run workflow** → **Run workflow**
4. 等待约 2-3 分钟，查看 Slack 私信是否收到资讯 ✅

---

## ⏰ 修改推送时间

编辑 `.github/workflows/daily-news.yml` 中的 cron 表达式：

```yaml
- cron: "0 0 * * *"   # UTC 00:00 = 东京时间 09:00
```

常用时间对照（东京时间 → UTC）：

| 东京时间 | cron 表达式 |
|---------|------------|
| 07:00 | `0 22 * * *`（前一天 UTC）|
| 08:00 | `0 23 * * *`（前一天 UTC）|
| 09:00 | `0 0 * * *` |
| 10:00 | `0 1 * * *` |

---

## 💰 费用估算

| 服务 | 费用 |
|------|------|
| GitHub Actions | **免费**（公开仓库无限制）|
| Claude API（每次约 5000 tokens）| 约 **$0.02 / 次** |
| Slack | **免费** |
| **每月合计** | 约 **$0.60** |

---

## 🔧 常见问题

**Q: Actions 没有自动触发？**
A: GitHub 免费仓库的定时任务可能延迟 15-30 分钟，属于正常现象。

**Q: Slack 收不到消息？**
A: 确认 Bot 已安装到 Workspace，且 User ID 正确。

**Q: 如何修改资讯条数或来源？**
A: 编辑 `scripts/fetch_and_send.py` 中的 `NEWS_COUNT` 和 `build_prompt()` 函数。
