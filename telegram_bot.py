"""
Telegram Bot推送模块 - 适配signal_scorer_v2.py
"""
import requests
import os
from typing import Dict

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_alert(self, token_data: Dict, score_result: Dict):
        """发送信号通知"""
        message = self._format_message(token_data, score_result)

        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram发送失败: {e}")
            return False

    def _format_message(self, token: Dict, score: Dict) -> str:
        """格式化通知消息 - 适配新的评分系统"""
        symbol = token.get("symbol", "UNKNOWN")
        chain = token.get("chain", "").upper()
        price = token.get("price", 0)
        price_change_1h = token.get("price_change_1h", 0)
        price_change_24h = token.get("price_change_24h", 0)

        breakdown = score["breakdown"]
        recommendation = score.get("recommendation", "")
        total_score = score["score"]
        insights = score.get("insights", [])

        msg = f"""
🚨 *Smart Money信号预警*

💎 *{symbol}* ({chain})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *综合评分*: {total_score}/100
{recommendation}

💰 *当前价格*: ${price:.4f}
📈 *价格变化*: 1h: {price_change_1h:+.2f}% | 24h: {price_change_24h:+.2f}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        # 显示各个维度的评分
        category_names = {
            "increment": "🚀 增量信号",
            "early_stage": "⏰ 早期机会",
            "trend": "📈 趋势强度",
            "liquidity": "💧 流动性"
        }

        for key, name in category_names.items():
            if key in breakdown:
                item = breakdown[key]
                if "score" in item:
                    msg += f"*{name}* ({item['score']}/{item['max_score']})\n"
                elif "penalty" in item:
                    msg += f"*{name}* (-{item['penalty']}分)\n"

        # 显示洞察（如果有）
        if insights:
            msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "*💡 关键洞察*:\n"
            for insight in insights[:3]:  # 最多显示3条
                msg += f"  • {insight}\n"

        # 建议操作
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *操作建议*:
"""

        if total_score >= 70:
            msg += f"💰 建议仓位: 2-3%\n"
        elif total_score >= 50:
            msg += f"💰 建议仓位: 1-2%\n"
        else:
            msg += f"💰 建议仓位: 观察仓<1%\n"

        msg += f"📍 当前价: ${price:.4f}\n"
        msg += f"🎯 止盈目标: +30% (${price * 1.3:.4f})\n"
        msg += f"🛑 止损位: -15% (${price * 0.85:.4f})\n"
        msg += f"⏳ 有效期: 8小时内\n"

        if "timestamp" in score:
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 *{score['timestamp']}*
"""

        return msg

    def test_connection(self):
        """测试Telegram连接"""
        payload = {
            "chat_id": self.chat_id,
            "text": "✅ Smart Money Tracker 已启动！"
        }

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Telegram连接测试失败: {e}")
            return False
