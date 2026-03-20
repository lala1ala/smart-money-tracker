# 📦 部署指南

本指南提供两种部署方式，推荐使用 **GitHub Actions**（更简单）。

---

## 方式1: GitHub Actions（推荐）

### 优点
- ✅ 完全免费
- ✅ 配置简单
- ✅ 自动定时执行
- ✅ 无需服务器管理

### 部署步骤

#### 1. 准备GitHub仓库
```bash
cd C:\Users\Administrator\smart-money-tracker
git init
git add .
git commit -m "Initial commit"
```

然后在GitHub创建新仓库，执行：
```bash
git remote add origin https://github.com/YOUR_USERNAME/smart-money-tracker.git
git branch -M main
git push -u origin main
```

#### 2. 配置GitHub Secrets

1. 打开你的GitHub仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下密钥：

| Name | Secret |
|------|--------|
| `NANSEN_API_KEY` | 你的Nansen API Key |
| `TELEGRAM_BOT_TOKEN` | 你的Telegram Bot Token（格式：`123456789:ABC...`） |
| `TELEGRAM_CHAT_ID` | 你的Telegram Chat ID |

#### 3. 启用工作流

1. 进入 **Actions** 标签
2. 找到 **Smart Money Scanner** 工作流
3. 点击 **Enable workflow**

#### 4. 手动测试

1. 点击 **Run workflow** → **Run workflow**
2. 等待执行完成（约1-2分钟）
3. 检查Telegram是否收到通知

#### 5. 验证定时任务

工作流默认每小时自动执行（整点），你可以在Actions页面查看执行历史。

---

## 方式2: Railway + Cron（可选）

### 优点
- ✅ 执行时间更灵活
- ✅ 可以实时查看日志
- ✅ 支持手动触发

### 缺点
- ❌ 免费额度有限（每月$5额度）
- ❌ 需要额外服务管理

### 部署步骤

#### 1. 准备Railway账号

1. 访问 [railway.app](https://railway.app/)
2. 使用GitHub账号登录
3. 新建项目，选择 **Deploy from GitHub repo**

#### 2. 配置环境变量

在Railway项目设置中添加以下环境变量：

```bash
NANSEN_API_KEY=your_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

#### 3. 配置定时任务

Railway需要使用外部cron服务，推荐使用 **cron-job.org**：

1. 访问 [cron-job.org](https://cron-job.org/) 注册账号
2. 创建新任务，配置：
   - **Title**: Smart Money Scanner
   - **URL**: 你的Railway项目URL（例如：`https://your-project.railway.app/scan`）
   - **Execution**: 每小时执行一次

#### 4. 修改代码支持Webhook

需要在 `scanner.py` 中添加Flask服务器：

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def trigger_scan():
    try:
        main()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # 仅在Railway运行时启动服务器
    if os.getenv("RAILWAY_ENVIRONMENT"):
        app.run(host="0.0.0.0", port=8000)
    else:
        main()
```

同时更新 `requirements.txt`：
```
flask==3.0.0
gunicorn==21.2.0
```

---

## 监控和维护

### 查看执行日志

#### GitHub Actions
1. 进入 **Actions** 标签
2. 点击具体的运行记录
3. 查看详细日志

#### Railway
1. 在项目页面点击 **Logs**
2. 实时查看程序输出

### 常见问题

#### Q1: GitHub Actions执行失败
**可能原因**:
- Secrets未正确配置
- 依赖安装失败
- Nansen API密钥无效

**解决方案**:
- 检查GitHub Secrets配置
- 查看Actions日志定位错误
- 验证API密钥有效性

#### Q2: 没有收到Telegram通知
**可能原因**:
- Chat ID错误
- Bot Token错误
- 没有达到推送阈值（<70分）

**解决方案**:
```bash
# 测试Telegram配置
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

#### Q3: API消耗过快
**解决方案**:
1. 减少扫描链数：`CHAINS = ["ethereum", "solana"]`
2. 降低扫描频率：修改cron为 `0 */2 * * *`（每2小时）
3. 减少每次扫描数量：修改top_n从50改为30

---

## 安全建议

1. **永远不要**将 `.env` 文件提交到Git
2. **永远不要**在公开代码中硬编码API密钥
3. **定期更换**API密钥和Bot Token
4. **限制GitHub Actions**的权限范围
5. **监控API使用量**，避免超出额度

---

## 费用估算

### GitHub Actions
- **费用**: 完全免费
- **限额**: 每月2000分钟
- **本系统**: 每月约720分钟（每小时1次 × 24小时 × 30天）
- **结论**: ✅ 完全在免费额度内

### Railway
- **免费额度**: $5/月
- **本系统**: 约$2-3/月（取决于执行频率）
- **结论**: ⚠️ 基本够用，但接近限额

---

## 推荐选择

| 需求 | 推荐方案 |
|-----|---------|
| 简单快速 | GitHub Actions ✅ |
| 完全免费 | GitHub Actions ✅ |
| 灵活定时 | Railway + Cron |
| 实时日志 | Railway |
| 长期运行 | GitHub Actions ✅ |

**最终推荐**: GitHub Actions（适合90%的使用场景）
