# 🚀 Smart Money 交易信号系统

基于Nansen API的智能交易信号扫描和推送系统。每小时自动扫描Smart Money动向，通过多维度评分算法识别高潜力交易机会，并推送至Telegram。

## ✨ 核心功能

- **🔍 多链扫描**: 同时监控Ethereum、Solana、Base三条公链
- **📊 智能评分**: 4维度评分系统（Smart Money质量40分 + 时机30分 + 流动性20分 - 风险惩罚10分）
- **⚡ 实时推送**: 高分信号（≥70分）实时推送到Telegram
- **🎯 交易建议**: 提供入场价、止盈目标、止损位置、仓位建议
- **🛡️ 防重复**: 24小时内同一代币不重复推送
- **📈 信号质量控制**: 每轮最多推送5个最高分信号

## 📁 项目结构

```
smart-money-tracker/
├── .github/
│   └── workflows/
│       └── scan.yml          # GitHub Actions工作流
├── config.py                 # 配置文件（评分权重、阈值）
├── nansen_client.py          # Nansen API客户端
├── signal_scorer.py          # 信号评分算法
├── telegram_bot.py           # Telegram推送模块
├── scanner.py                # 主扫描程序
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量模板
└── README.md                 # 本文档
```

## 🚀 快速开始

### 1. 准备工作

#### 1.1 获取Nansen API Key
- 访问 [Nansen](https://www.nansen.ai/) 注册账号
- 获取API Key并确认调用额度

#### 1.2 创建Telegram Bot
1. 在Telegram中找到 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称
4. 保存返回的 **Bot Token**（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

#### 1.3 获取Telegram Chat ID
1. 在Telegram中找到 [@userinfobot](https://t.me/userinfobot)
2. 发送任意消息
3. 保存返回的 **Chat ID**（纯数字或负数）

### 2. 本地测试

#### 2.1 克隆项目
```bash
git clone https://github.com/YOUR_USERNAME/smart-money-tracker.git
cd smart-money-tracker
```

#### 2.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 2.3 配置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的密钥：
```bash
NANSEN_API_KEY=your_nansen_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

SCAN_INTERVAL_HOURS=1
MIN_SCORE_THRESHOLD=70
MAX_SIGNALS_PER_RUN=5
```

#### 2.4 测试运行
```bash
python scanner.py
```

检查你的Telegram，应该收到测试通知。

### 3. 部署到GitHub Actions

#### 3.1 推送代码到GitHub
```bash
git add .
git commit -m "Initial commit: Smart Money Scanner"
git push origin main
```

#### 3.2 配置GitHub Secrets

1. 打开你的GitHub仓库
2. 进入 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**，添加以下4个密钥：

| Secret名称 | 值 |
|-----------|---|
| `NANSEN_API_KEY` | 你的Nansen API Key |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID |

#### 3.3 启用GitHub Actions

1. 进入 **Actions** 标签
2. 找到 **Smart Money Scanner** 工作流
3. 点击 **Enable workflow**

#### 3.4 手动测试（可选）

1. 在Actions页面点击 **Run workflow**
2. 选择分支，点击 **Run workflow**
3. 等待执行完成，检查是否收到Telegram通知

### 4. 验证定时任务

GitHub Actions默认每小时自动执行一次（cron: `0 * * * *`），你会在Telegram收到定时推送。

## 📊 评分系统说明

### 评分维度（总分100分）

#### 1. Smart Money质量（40分）
- **Smart Money数量（20分）**
  - ≥8个: 20分
  - ≥5个: 15分
  - ≥3个: 10分
  - <3个: 0分

- **平均ROI（20分）**
  - ≥200%: 20分
  - ≥100%: 15分
  - ≥50%: 10分
  - <50%: 0分

#### 2. 时机评估（30分）
- **1小时涨幅（15分）**
  - 5%-20%: 15分（早期）
  - 20%-40%: 8分（有点高）
  - >40%: 0分（追高风险）
  - <5%: 10分（可接受）

- **24小时涨幅（15分）**
  - 10%-50%: 15分（早期）
  - 50%-100%: 10分（中期）
  - >100%: 5分（可能过热）
  - <10%: 8分（刚开始）

#### 3. 流动性（20分）
- **24小时交易量**
  - ≥$10M: 20分
  - ≥$1M: 15分
  - ≥$500K: 10分
  - <$500K: 5分

#### 4. 风险惩罚（-10分）
- **追高惩罚**: 1h涨幅>50% → -10分
- **持仓集中**: 前10持有人>70% → -5分

### 信号等级

| 分数 | 建议 | 含义 |
|-----|------|------|
| ≥80 | 🚀 强买入信号 | 多个维度表现优秀 |
| 70-79 | ✅ 可以买入 | 达到买入标准 |
| 60-69 | ⚠️ 谨慎考虑 | 部分指标未达标 |
| 50-59 | ❌ 观望为主 | 风险较高 |
| <50 | 🛑 不建议买入 | 不符合买入条件 |

## 🔧 配置说明

在 `config.py` 中可调整：

```python
# 扫描配置
SCAN_INTERVAL_HOURS = 1        # 扫描间隔（小时）
MIN_SCORE_THRESHOLD = 70       # 最低推送分数
MAX_SIGNALS_PER_RUN = 5        # 每轮最多推送信号数

# 扫描的链
CHAINS = ["ethereum", "solana", "base"]

# 评分权重
WEIGHTS = {
    "smart_money_quality": 40,
    "timing": 30,
    "liquidity": 20,
    "risk_penalty": 10
}

# 风险阈值
MAX_1H_CHANGE = 50             # 超过此1h涨幅会扣分
MIN_LIQUIDITY = 1_000_000      # 最低流动性要求（$1M）
```

## 📈 API消耗估算

基于当前配置（每小时扫描，3条链）：

- **每次扫描**: ~1,300次API调用
- **每天**: ~31,200次调用
- **每月**: ~936,000次调用
- **8个月**: ~7,488,000次调用

**当前额度**: 1,666,248次调用 → **可运行约5个月**

如需延长使用时间，可：
- 减少扫描链数（只保留ethereum和solana）
- 降低扫描频率（改为每2小时一次）
- 减少每次扫描的top_n数量（从50降到30）

## 🐛 故障排除

### 没有收到Telegram通知

1. 检查GitHub Actions日志：
   - 进入Actions标签
   - 查看最新运行记录
   - 检查是否有错误

2. 验证Telegram配置：
   ```bash
   # 测试Bot Token
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe

   # 获取最新消息
   curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

3. 检查环境变量是否正确配置在GitHub Secrets中

### 扫描成功但没有高分信号

这是正常的！系统的设计理念是**宁缺毋滥**：
- 不是每小时都会有高分信号
- 只有真正符合标准的机会才推送
- 可以降低 `MIN_SCORE_THRESHOLD` 来增加信号数量

### Nansen API错误

1. 检查API Key是否过期
2. 确认API调用额度是否充足
3. 查看Nansen服务状态

## 📝 License

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚠️ 免责声明

本系统仅供学习和研究目的，不构成投资建议。加密货币交易存在高风险，请自行判断并承担风险。
