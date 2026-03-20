"""
Telegram Bot推送模块
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
        """格式化通知消息"""
        symbol = token.get("symbol", "UNKNOWN")
        chain = token.get("chain", "").upper()
        price = token.get("price", 0)
        price_change_1h = token.get("price_change_1h", 0)
        price_change_24h = token.get("price_change_24h", 0)

        breakdown = score["breakdown"]
        recommendation = score["recommendation"]
        total_score = score["score"]

        msg = f"""
🚨 *Smart Money信号预警*

💎 *{symbol}* ({chain})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *综合评分*: {total_score}/100
{recommendation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

*💎 Smart Money质量* ({breakdown['smart_money']['score']}/{breakdown['smart_money']['max_score']})
"""

        for detail in breakdown["smart_money"]["detail"]:
            msg += f"{detail}\n"

        msg += f"""
*⏰ 时机评估* ({breakdown['timing']['score']}/{breakdown['timing']['max_score']})
"""

        for detail in breakdown["timing"]["detail"]:
            msg += f"{detail}\n"

        msg += f"""
*💧 流动性* ({breakdown['liquidity']['score']}/{breakdown['liquidity']['max_score']})
"""

        for detail in breakdown["liquidity"]["detail"]:
            msg += f"{detail}\n"

        if breakdown["risk"]["penalty"] > 0:
            msg += f"""
*⚠️ 风险提示* (-{breakdown['risk']['penalty']}分)
"""
            for detail in breakdown["risk"]["detail"]:
                msg += f"{detail}\n"

        # 建议操作
        if total_score >= 70:
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 *操作建议*:
💰 建议仓位: 2-3%
📍 入场价: ${price:.4f}
🎯 止盈目标: +30% (${price * 1.3:.4f})
🛑 止损: -15% (${price * 0.85:.4f})

⏳ 有效期: 8小时内
"""

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
