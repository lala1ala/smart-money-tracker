"""
信号评分算法
"""
from typing import Dict, List
from datetime import datetime

class SignalScorer:
    def __init__(self, weights: Dict):
        self.weights = weights

    def score_token(self, token_data: Dict) -> Dict:
        """
        对代币进行综合评分

        Args:
            token_data: 包含price_change, smart_money_data等

        Returns:
            {
                "score": 85,
                "breakdown": {...},
                "recommendation": "强买入"
            }
        """
        score = 0
        breakdown = {}

        # 1. Smart Money质量评分 (40分)
        sm_score, sm_detail = self._score_smart_money(token_data)
        score += sm_score
        breakdown["smart_money"] = {
            "score": sm_score,
            "max_score": self.weights["smart_money_quality"],
            "detail": sm_detail
        }

        # 2. 时机评分 (30分)
        timing_score, timing_detail = self._score_timing(token_data)
        score += timing_score
        breakdown["timing"] = {
            "score": timing_score,
            "max_score": self.weights["timing"],
            "detail": timing_detail
        }

        # 3. 流动性评分 (20分)
        liquidity_score, liquidity_detail = self._score_liquidity(token_data)
        score += liquidity_score
        breakdown["liquidity"] = {
            "score": liquidity_score,
            "max_score": self.weights["liquidity"],
            "detail": liquidity_detail
        }

        # 4. 风险惩罚 (最多-10分)
        risk_penalty, risk_detail = self._score_risk(token_data)
        score -= risk_penalty
        breakdown["risk"] = {
            "penalty": risk_penalty,
            "detail": risk_detail
        }

        # 5. 生成建议
        recommendation = self._generate_recommendation(score)

        return {
            "score": score,
            "breakdown": breakdown,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat()
        }

    def _score_smart_money(self, token: Dict) -> tuple:
        """Smart Money质量评分"""
        score = 0
        details = []

        sm_count = token.get("smart_money_count", 0)
        sm_avg_roi = token.get("smart_money_avg_roi", 0)
        sm_total_amount = token.get("smart_money_total_amount", 0)

        # Smart Money数量 (20分)
        if sm_count >= 8:
            score += 20
            details.append(f"✅ {sm_count}个Smart Money买入 (满分)")
        elif sm_count >= 5:
            score += 15
            details.append(f"✅ {sm_count}个Smart Money买入")
        elif sm_count >= 3:
            score += 10
            details.append(f"⚠️ {sm_count}个Smart Money买入")
        else:
            details.append(f"❌ 仅{sm_count}个Smart Money买入")

        # 历史ROI (20分)
        if sm_avg_roi >= 200:
            score += 20
            details.append(f"✅ 平均ROI {sm_avg_roi}% (超高)")
        elif sm_avg_roi >= 100:
            score += 15
            details.append(f"✅ 平均ROI {sm_avg_roi}%")
        elif sm_avg_roi >= 50:
            score += 10
            details.append(f"⚠️ 平均ROI {sm_avg_roi}%")
        else:
            details.append(f"❌ 平均ROI {sm_avg_roi}% (较低)")

        # 总金额 (加分项，不占权重)
        if sm_total_amount >= 1_000_000:
            details.append(f"💰 总金额: ${sm_total_amount/1000000:.1f}M")
        else:
            details.append(f"💰 总金额: ${sm_total_amount/1000:.0f}K")

        return score, details

    def _score_timing(self, token: Dict) -> tuple:
        """时机评分"""
        score = 0
        details = []

        change_1h = token.get("price_change_1h") or 0
        change_24h = token.get("price_change_24h") or 0

        # 1小时涨幅 (15分) - 不要追高
        if 5 <= change_1h <= 20:
            score += 15
            details.append(f"✅ 1h涨幅 +{change_1h}% (早期)")
        elif 20 < change_1h <= 40:
            score += 8
            details.append(f"⚠️ 1h涨幅 +{change_1h}% (有点高)")
        elif change_1h > 40:
            score += 0
            details.append(f"❌ 1h涨幅 +{change_1h}% (追高风险)")
        else:
            score += 10
            details.append(f"⏳ 1h涨幅 +{change_1h}% (可接受)")

        # 24小时涨幅 (15分) - 早期阶段最好
        if 10 <= change_24h <= 50:
            score += 15
            details.append(f"✅ 24h涨幅 +{change_24h}% (早期)")
        elif 50 < change_24h <= 100:
            score += 10
            details.append(f"⚠️ 24h涨幅 +{change_24h}% (中期)")
        elif change_24h > 100:
            score += 5
            details.append(f"❌ 24h涨幅 +{change_24h}% (可能过热)")
        else:
            score += 8
            details.append(f"⏳ 24h涨幅 +{change_24h}% (刚开始)")

        return score, details

    def _score_liquidity(self, token: Dict) -> tuple:
        """流动性评分"""
        score = 0
        details = []

        liquidity_24h = token.get("volume_24h", 0)

        if liquidity_24h >= 10_000_000:
            score = 20
            details.append(f"✅ 24h交易量 ${liquidity_24h/1000000:.1f}M (充足)")
        elif liquidity_24h >= 1_000_000:
            score = 15
            details.append(f"✅ 24h交易量 ${liquidity_24h/1000:.0f}K")
        elif liquidity_24h >= 500_000:
            score = 10
            details.append(f"⚠️ 24h交易量 ${liquidity_24h/1000:.0f}K (一般)")
        else:
            score = 5
            details.append(f"❌ 24h交易量 ${liquidity_24h/1000:.0f}K (偏低)")

        return score, details

    def _score_risk(self, token: Dict) -> tuple:
        """风险惩罚"""
        penalty = 0
        details = []

        change_1h = token.get("price_change_1h", 0)
        holder_concentration = token.get("holder_concentration", 0)

        # 追高惩罚
        if change_1h > 50:
            penalty += 10
            details.append(f"⚠️ 1h暴涨{change_1h}%，追高风险大")

        # 持仓集中惩罚
        if holder_concentration > 0.7:
            penalty += 5
            details.append(f"⚠️ 前10持有人占{holder_concentration*100:.0f}% (较集中)")
        elif holder_concentration > 0.5:
            penalty += 2
            details.append(f"⚠️ 前10持有人占{holder_concentration*100:.0f}%")

        return penalty, details

    def _generate_recommendation(self, score: int) -> str:
        """生成建议"""
        if score >= 80:
            return "🚀 强买入信号"
        elif score >= 70:
            return "✅ 可以买入"
        elif score >= 60:
            return "⚠️ 谨慎考虑"
        elif score >= 50:
            return "❌ 观望为主"
        else:
            return "🛑 不建议买入"
