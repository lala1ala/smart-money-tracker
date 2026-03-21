"""
改进的信号评分算法 v2.0 - 增量监控

核心思路：
1. 对比不同时间窗口的数据（1h vs 4h vs 24h）
2. 检测Smart Money的增量变化
3. 发现早期入场机会
"""
from typing import Dict, List, Tuple
from datetime import datetime


class SignalScorerV2:
    def __init__(self, weights: Dict):
        self.weights = weights

    def score_token_with_time_windows(
        self,
        token_data_1h: Dict,
        token_data_4h: Dict = None,
        token_data_24h: Dict = None
    ) -> Dict:
        """
        对代币进行增量评分

        Args:
            token_data_1h: 1小时窗口数据
            token_data_4h: 4小时窗口数据（可选）
            token_data_24h: 24小时窗口数据（可选）

        Returns:
            {
                "score": 85,
                "breakdown": {...},
                "recommendation": "强买入",
                "insights": ["🚀 Smart Money数量1小时内从2个增加到8个"]
            }
        """
        score = 0
        breakdown = {}
        insights = []

        # 1. 增量评分（40分）- 最重要！
        increment_score, increment_detail = self._score_increment(
            token_data_1h, token_data_4h, token_data_24h
        )
        score += increment_score
        breakdown["increment"] = {
            "score": increment_score,
            "max_score": 40,
            "detail": increment_detail
        }

        # 提取关键洞察
        if "sm_count_1h" in token_data_1h:
            sm_count_1h = token_data_1h["sm_count_1h"]
            if token_data_4h and "sm_count_4h" in token_data_4h:
                sm_count_4h = token_data_4h["sm_count_4h"]
                if sm_count_1h > sm_count_4h * 2:
                    insights.append(f"🚀 Smart Money数量翻倍：{sm_count_4h}→{sm_count_1h}")
            if token_data_24h and "sm_count_24h" in token_data_24h:
                sm_count_24h = token_data_24h["sm_count_24h"]
                if sm_count_1h > sm_count_24h * 0.8:
                    insights.append(f"⚡ 1小时内Smart Money占24h总量的80%+")

        # 2. 早期评分（30分）- 越早越好
        early_score, early_detail = self._score_early_stage(
            token_data_1h, token_data_4h, token_data_24h
        )
        score += early_score
        breakdown["early_stage"] = {
            "score": early_score,
            "max_score": 30,
            "detail": early_detail
        }

        # 3. 趋势评分（20分）- 持续性
        trend_score, trend_detail = self._score_trend(
            token_data_1h, token_data_4h, token_data_24h
        )
        score += trend_score
        breakdown["trend"] = {
            "score": trend_score,
            "max_score": 20,
            "detail": trend_detail
        }

        # 4. 流动性评分（10分）
        liquidity_score, liquidity_detail = self._score_liquidity(token_data_1h)
        score += liquidity_score
        breakdown["liquidity"] = {
            "score": liquidity_score,
            "max_score": 10,
            "detail": liquidity_detail
        }

        # 5. 拥挤度惩罚（最多-20分）- 越拥挤越危险
        crowding_penalty, crowding_detail = self._score_crowding(
            token_data_1h, token_data_24h
        )
        score -= crowding_penalty
        breakdown["crowding"] = {
            "penalty": crowding_penalty,
            "detail": crowding_detail
        }

        # 6. 生成建议
        recommendation = self._generate_recommendation(score)

        return {
            "score": score,
            "breakdown": breakdown,
            "recommendation": recommendation,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }

    def _score_increment(
        self,
        data_1h: Dict,
        data_4h: Dict = None,
        data_24h: Dict = None
    ) -> Tuple[int, List[str]]:
        """增量评分 - Smart Money在增加吗？"""
        score = 0
        details = []

        sm_count_1h = data_1h.get("smart_money_count", 0)
        netflow_1h = data_1h.get("netflow_1h", 0)

        # 1. Smart Money数量增量（20分）
        if data_4h:
            sm_count_4h = data_4h.get("smart_money_count", 0)

            # 计算增长率
            if sm_count_4h > 0:
                growth_rate = (sm_count_1h - sm_count_4h) / sm_count_4h
            else:
                growth_rate = 0

            if growth_rate >= 1.0:  # 翻倍
                score += 20
                details.append(f"🚀 Smart Money数量翻倍：{sm_count_4h}→{sm_count_1h}（+{growth_rate*100:.0f}%）")
            elif growth_rate >= 0.5:  # 增长50%
                score += 15
                details.append(f"✅ Smart Money数量增长：{sm_count_4h}→{sm_count_1h}（+{growth_rate*100:.0f}%）")
            elif growth_rate >= 0.25:  # 增长25%
                score += 10
                details.append(f"⚠️ Smart Money数量微增：{sm_count_4h}→{sm_count_1h}")
            elif growth_rate >= 0:
                score += 5
                details.append(f"⏳ Smart Money数量持平：{sm_count_1h}个")
            else:
                details.append(f"📉 Smart Money数量减少：{sm_count_4h}→{sm_count_1h}")
        else:
            # 如果没有4h数据，只看1h的绝对值
            if sm_count_1h >= 5:
                score += 15
                details.append(f"✅ 1小时内{sm_count_1h}个Smart Money买入")
            elif sm_count_1h >= 3:
                score += 10
                details.append(f"⚠️ 1小时内{sm_count_1h}个Smart Money买入")
            else:
                details.append(f"❌ 1小时内仅{sm_count_1h}个Smart Money买入")

        # 2. 净流入增量（20分）
        if data_4h:
            netflow_4h = data_4h.get("netflow_1h", 0) * 4  # 估算4小时流入

            if netflow_4h > 0:
                inflow_rate = netflow_1h / netflow_4h

                if inflow_rate >= 0.5:  # 1小时占4小时总量的50%+
                    score += 20
                    details.append(f"🔥 加速流入！1小时占4小时总量的{inflow_rate*100:.0f}%")
                elif inflow_rate >= 0.3:
                    score += 15
                    details.append(f"✅ 1小时占4小时总量的{inflow_rate*100:.0f}%")
                elif inflow_rate >= 0.2:
                    score += 10
                    details.append(f"⚠️ 1小时占4小时总量的{inflow_rate*100:.0f}%")
                else:
                    score += 5
                    details.append(f"⏳ 流入平稳")
        else:
            # 只看1h流入
            if netflow_1h >= 100_000:
                score += 15
                details.append(f"✅ 1小时净流入${netflow_1h/1000:.0f}K")
            elif netflow_1h >= 50_000:
                score += 10
                details.append(f"⚠️ 1小时净流入${netflow_1h/1000:.0f}K")

        return score, details

    def _score_early_stage(
        self,
        data_1h: Dict,
        data_4h: Dict = None,
        data_24h: Dict = None
    ) -> Tuple[int, List[str]]:
        """早期评分 - 越早越好"""
        score = 0
        details = []

        price_change_1h = data_1h.get("price_change_1h") or 0
        price_change_24h = data_1h.get("price_change_24h") or 0

        # 1. 早期阶段识别（15分）
        if 5 <= price_change_1h <= 30:
            score += 15
            details.append(f"✅ 1h涨幅+{price_change_1h}%（早期阶段）")
        elif 30 < price_change_1h <= 60:
            score += 10
            details.append(f"⚠️ 1h涨幅+{price_change_1h}%（中期）")
        elif price_change_1h > 60:
            score += 5
            details.append(f"❌ 1h涨幅+{price_change_1h}%（偏晚）")
        else:
            score += 8
            details.append(f"⏳ 1h涨幅+{price_change_1h}%（刚开始）")

        # 2. 24小时涨幅判断（15分）
        if 10 <= price_change_24h <= 100:
            score += 15
            details.append(f"✅ 24h涨幅+{price_change_24h}%（仍在早期）")
        elif 100 < price_change_24h <= 200:
            score += 10
            details.append(f"⚠️ 24h涨幅+{price_change_24h}%（中期）")
        elif price_change_24h > 200:
            score += 5
            details.append(f"❌ 24h涨幅+{price_change_24h}%（可能过热）")
        else:
            score += 8
            details.append(f"⏳ 24h涨幅+{price_change_24h}%（极早期）")

        return score, details

    def _score_trend(
        self,
        data_1h: Dict,
        data_4h: Dict = None,
        data_24h: Dict = None
    ) -> Tuple[int, List[str]]:
        """趋势评分 - 持续性"""
        score = 0
        details = []

        # 检查是否持续流入
        netflow_1h = data_1h.get("netflow_1h", 0)

        if data_4h and data_24h:
            netflow_4h = data_4h.get("netflow_1h", 0) * 4
            netflow_24h = data_24h.get("netflow_24h", 0)

            # 检查流入趋势
            if netflow_1h > 0 and netflow_4h > 0 and netflow_24h > 0:
                score += 20
                details.append(f"✅ 持续净流入：1h=${netflow_1h/1000:.0f}K, 4h=${netflow_4h/1000:.0f}K, 24h=${netflow_24h/1000:.0f}K")
            elif netflow_1h > 0 and netflow_4h > 0:
                score += 15
                details.append(f"✅ 近期持续流入")
            elif netflow_1h > 0:
                score += 10
                details.append(f"⚠️ 仅1小时有流入")
            else:
                details.append(f"❌ 净流出")
        else:
            if netflow_1h > 0:
                score += 10
                details.append(f"✅ 1小时净流入${netflow_1h/1000:.0f}K")

        return score, details

    def _score_liquidity(self, data_1h: Dict) -> Tuple[int, List[str]]:
        """流动性评分"""
        score = 0
        details = []

        volume_24h = data_1h.get("volume_24h", 0)

        if volume_24h >= 1_000_000:
            score = 10
            details.append(f"✅ 24h交易量${volume_24h/1000000:.1f}M")
        elif volume_24h >= 500_000:
            score = 8
            details.append(f"⚠️ 24h交易量${volume_24h/1000:.0f}K")
        elif volume_24h >= 100_000:
            score = 5
            details.append(f"⚠️ 24h交易量${volume_24h/1000:.0f}K（偏低）")
        else:
            score = 2
            details.append(f"❌ 24h交易量${volume_24h/1000:.0f}K（很低）")

        return score, details

    def _score_crowding(
        self,
        data_1h: Dict,
        data_24h: Dict = None
    ) -> Tuple[int, List[str]]:
        """拥挤度惩罚 - 越拥挤越危险"""
        penalty = 0
        details = []

        price_change_1h = data_1h.get("price_change_1h") or 0

        # 1. 暴涨惩罚（最多-10分）
        if price_change_1h > 100:
            penalty += 10
            details.append(f"⚠️ 1h暴涨{price_change_1h}%（严重追高）")
        elif price_change_1h > 50:
            penalty += 5
            details.append(f"⚠️ 1h暴涨{price_change_1h}%（追高）")

        # 2. 换手率惩罚（如果有数据）（最多-10分）
        # TODO: 需要从API获取换手率数据

        return penalty, details

    def _generate_recommendation(self, score: int) -> str:
        """生成建议"""
        if score >= 80:
            return "🚀 强买入信号（早期+增量）"
        elif score >= 70:
            return "✅ 可以买入（趋势确立）"
        elif score >= 60:
            return "⚠️ 谨慎考虑（可能偏晚）"
        elif score >= 50:
            return "❌ 观望为主（不够早期）"
        else:
            return "🛑 不建议买入（太晚或没信号）"
