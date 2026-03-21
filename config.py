"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API配置
NANSEN_API_KEY = os.getenv("NANSEN_API_KEY")

# Telegram配置
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 扫描配置
SCAN_INTERVAL_HOURS = int(os.getenv("SCAN_INTERVAL_HOURS", 0.5))  # 30分钟
MIN_SCORE_THRESHOLD = int(os.getenv("MIN_SCORE_THRESHOLD", 70))
MAX_SIGNALS_PER_RUN = int(os.getenv("MAX_SIGNALS_PER_RUN", 5))

# 链配置（平衡方案：5条主流链）
CHAINS = ["ethereum", "solana", "base", "arbitrum", "bnb"]

# 评分权重
WEIGHTS = {
    "smart_money_quality": 40,
    "timing": 30,
    "liquidity": 20,
    "risk_penalty": 10
}

# 风险阈值
MAX_1H_CHANGE = 50  # 超过这个分数会扣分
MIN_LIQUIDITY = 1_000_000  # $1M
