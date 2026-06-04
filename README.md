# 🌏 每日科技资讯 Slack Bot（Gemini 免费版）

每天早上 9:00（东京时间）自动搜集全球科技资讯，发送到你的 Slack 私信。
**完全免费！** 使用 Google Gemini API 免费额度。

---

## ✨ 功能特性

- 覆盖 **中文、英文、日文** 科技媒体
- 重点追踪 **亚洲科技动态**（中国、日本、韩国、东南亚）
- 来源：36Kr、IT之家、TechCrunch、Nikkei Asia、微博热搜等
- 每日 **15条以上**，按热度排列
- 每条含：标题、热度依据、摘要、原链接、业内视角
- 使用 Gemini Google Search Grounding 实时搜索当日新闻

---

## 💰 费用

| 服务 | 费用 |
|------|------|
| GitHub Actions | **免费** |
| Google Gemini API | **免费**（每天1500次，每分钟15次，远超需求）|
| Slack | **免费** |
| **合计** | **$0 / 月** ✅ |

---

## 🛠 部署步骤

### Step 1 — 注册 GitHub 并上传代码

1. 访问 [github.com](https://github.com) 注册账号
2. 点击右上角 **"+"** → **New repository**
3. 填写名称 `tech-news-bot`，选 **Public**，勾选 **Add a README**
4. 点 **Create repository**
5. 点击 **Add file** → **Upload files**
6. 将本项目所有文件拖入上传

> ⚠️ Mac 用户：按 `Command + Shift + .` 显示隐藏文件夹 `.github`，一起上传

---

### Step 2 — 获取 Gemini API Key（免费）

1. 访问 [aistudio.google.com](https://aistudio.google.com)
2. 用 Google 账号登录（无需信用卡）
3. 点击左侧 **Get API key**
4. 点击 **Create API key** → 选择或新建一个 Google Cloud 项目
5. 复制生成的 Key（格式：`AIzaSy...`）
6. **保存到备忘录**

---

### Step 3 — 创建 Slack Bot 获取 Token

1. 访问 [api.slack.com/apps](https://api.slack.com/apps)
2. 点击 **Create New App** → **From scratch**
3. App Name 填 `Tech News Bot`，选择你的 Workspace，点 **Create App**
4. 左侧菜单进入 **OAuth & Permissions**
5. 在 **Bot Token Scopes** 添加：
   - `chat:write`
   - `im:write`
6. 滚动到顶部点击 **Install to Workspace** → **Allow**
7. 复制 **Bot User OAuth Token**（格式：`xoxb-...`）

---

### Step 4 — 获取你的 Slack User ID

1. 打开 Slack 电脑版
2. 点击左上角你的头像 → **Profile**
3. 点右上角 **⋯** → **Copy member ID**
4. 保存（格式：`U0123456789`）

---

### Step 5 — 在 GitHub 设置 Secrets

1. 进入你的 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，依次添加：

| Secret 名称 | 填入内容 |
|------------|---------|
| `GEMINI_API_KEY` | Step 2 获取的 Key |
| `SLACK_BOT_TOKEN` | Step 3 获取的 Token |
| `SLACK_USER_ID` | Step 4 获取的 ID |

---

### Step 6 — 测试运行

1. 进入仓库 **Actions** 标签页
2. 左侧点击 **每日科技资讯推送（Gemini 免费版）**
3. 点击 **Run workflow** → **Run workflow**
4. 等待约 2-3 分钟，绿色 ✅ = 成功
5. 打开 Slack 查看私信 🎉

---

## ⏰ 修改推送时间

编辑 `.github/workflows/daily-news.yml`：

```yaml
- cron: "0 0 * * *"   # UTC时间，对应东京时间 09:00
```

| 东京时间 | cron 写法 |
|---------|----------|
| 07:00 | `0 22 * * *` |
| 08:00 | `0 23 * * *` |
| 09:00 | `0 0 * * *` |
| 10:00 | `0 1 * * *` |

---

## 🔧 常见问题

**Q: Actions 显示绿色但 Slack 没收到？**
A: 检查 Slack Bot 是否已安装到 Workspace，User ID 是否正确。

**Q: 报错 "PERMISSION_DENIED"？**
A: Gemini API Key 可能未正确复制，重新获取一次。

**Q: 想增加/减少资讯条数？**
A: 修改 `scripts/fetch_and_send.py` 第 20 行的 `NEWS_COUNT = 15`。
