"""
适配新API的简化评分系统 v3.0

由于新API的smart_money_count字段全是0，
我们改用其他可用数据：交易量、净流入金额、价格变化
"""
from typing import Dict, List, Tuple
from datetime import datetime


class SignalScorerV3:
    """适配新API的评分器 - 不依赖smart_money_count"""

    def score_token(self, token_data: Dict) -> Dict:
        """
        基于可用数据评分
        
        使用的数据：
        - netflow_24h: 24h净流入金额
        - volume_24h: 24h交易量
        - price_change_1h/24h: 价格变化
        - liquidity: 流动性
        """
        score = 0
        details = []
        
        # 1. 净流入评分（35分）- 用金额代替数量
        netflow = token_data.get("netflow_24h") or 0
        if netflow > 1000000:  # $1M+
            score += 35
            details.append(f"🚀 24h净流入: ${netflow:,.0f}")
        elif netflow > 500000:  # $500K+
            score += 30
            details.append(f"✅ 24h净流入: ${netflow:,.0f}")
        elif netflow > 100000:  # $100K+
            score += 20
            details.append(f"⚠️ 24h净流入: ${netflow:,.0f}")
        elif netflow > 0:
            score += 10
            details.append(f"📊 24h净流入: ${netflow:,.0f}")
        
        # 2. 交易量评分（30分）
        volume = token_data.get("volume_24h") or 0
        if volume > 10000000:  # $10M+
            score += 30
            details.append(f"💱 24h交易量: ${volume:,.0f}")
        elif volume > 5000000:  # $5M+
            score += 25
            details.append(f"💱 24h交易量: ${volume:,.0f}")
        elif volume > 1000000:  # $1M+
            score += 20
            details.append(f"💱 24h交易量: ${volume:,.0f}")
        
        # 3. 价格趋势评分（20分）
        price_change_1h = token_data.get("price_change_1h") or 0
        price_change_24h = token_data.get("price_change_24h") or 0
        
        # 正向趋势
        if price_change_1h > 5 and price_change_24h > 10:
            score += 20
            details.append(f"📈 强势上涨: 1h+{price_change_1h:.1f}% | 24h+{price_change_24h:.1f}%")
        elif price_change_1h > 2 and price_change_24h > 5:
            score += 15
            details.append(f"📈 上涨中: 1h+{price_change_1h:.1f}% | 24h+{price_change_24h:.1f}%")
        elif price_change_24h > 0:
            score += 10
            details.append(f"📊 微涨: 24h+{price_change_24h:.1f}%")
        
        # 4. 流动性评分（15分）
        liquidity = token_data.get("liquidity") or 0
        if liquidity > 10000000:  # $10M+
            score += 15
            details.append(f"💧 高流动性: ${liquidity:,.0f}")
        elif liquidity > 5000000:  # $5M+
            score += 12
            details.append(f"💧 流动性: ${liquidity:,.0f}")
        elif liquidity > 1000000:  # $1M+
            score += 8
            details.append(f"💧 流动性: ${liquidity:,.0f}")
        
        # 生成建议
        recommendation = self._generate_recommendation(score)
        
        return {
            "score": min(score, 100),  # 最高100分
            "breakdown": {
                "netflow": {"score": min(score, 35), "max_score": 35},
                "volume": {"score": min(max(0, score - 35), 30), "max_score": 30},
                "trend": {"score": min(max(0, score - 65), 20), "max_score": 20},
                "liquidity": {"score": min(max(0, score - 85), 15), "max_score": 15}
            },
            "recommendation": recommendation,
            "insights": details,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendation(self, score: int) -> str:
        if score >= 70:
            return "🚀 强买入"
        elif score >= 50:
            return "✅ 买入"
        elif score >= 30:
            return "⚠️ 观察"
        else:
            return "❌ 不建议"
