"""
主扫描程序 - 每小时执行一次
扫描Smart Money信号并发送Telegram通知
"""
import os
import sys
import json
from datetime import datetime
from typing import List, Dict

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from nansen_client import NansenClient
from signal_scorer import SignalScorer
from telegram_bot import TelegramNotifier
from config import (
    NANSEN_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    CHAINS,
    WEIGHTS,
    MIN_SCORE_THRESHOLD,
    MAX_SIGNALS_PER_RUN
)

def load_sent_tokens() -> set:
    """加载已发送的代币地址（避免重复通知）"""
    try:
        if os.path.exists("sent_tokens.json"):
            with open("sent_tokens.json", "r") as f:
                data = json.load(f)
                # 清理24小时前的记录
                current_time = datetime.now().isoformat()
                cleaned = {
                    addr: time for addr, time in data.items()
                    if (datetime.fromisoformat(time) - datetime.now()).total_seconds() < 86400
                }
                if len(cleaned) != len(data):
                    with open("sent_tokens.json", "w") as fw:
                        json.dump(cleaned, fw)
                return set(cleaned.keys())
    except Exception as e:
        print(f"加载已发送代币失败: {e}")
    return set()

def save_sent_token(address: str):
    """保存已发送的代币地址"""
    try:
        sent_tokens = {}
        if os.path.exists("sent_tokens.json"):
            with open("sent_tokens.json", "r") as f:
                sent_tokens = json.load(f)
        sent_tokens[address] = datetime.now().isoformat()
        with open("sent_tokens.json", "w") as f:
            json.dump(sent_tokens, f)
    except Exception as e:
        print(f"保存已发送代币失败: {e}")

def merge_token_data(netflow_tokens: List[Dict], screener_tokens: List[Dict]) -> List[Dict]:
    """合并Smart Money净流入和代币筛选数据"""
    merged = {}

    # 先用screener数据建立基础（包含价格和交易量）
    for token in screener_tokens:
        address = token.get("token_address")
        if address:
            merged[address] = {
                "address": address,
                "symbol": token.get("token_symbol", "UNKNOWN"),
                "chain": token.get("chain", ""),
                "price": token.get("price_usd", 0),
                "price_change_1h": 0,  # API不提供，用0
                "price_change_24h": token.get("price_change", 0),  # 使用总体价格变化
                "netflow_1h": 0,
                "netflow_24h": 0,
                "smart_money_count": 0,
                "smart_money_avg_roi": 150,  # 默认值
                "smart_money_total_amount": 0,
                "volume_24h": token.get("volume", 0),
                "holder_concentration": 0.3  # 默认值
            }

    # 合并netflow数据
    for token in netflow_tokens:
        address = token.get("token_address")
        if address and address in merged:
            merged[address]["netflow_1h"] = token.get("net_flow_1h_usd", 0)
            merged[address]["netflow_24h"] = token.get("net_flow_24h_usd", 0)
            merged[address]["smart_money_count"] = token.get("trader_count", 1)
            merged[address]["smart_money_total_amount"] = abs(token.get("net_flow_1h_usd", 0))
        elif address:
            # 只有netflow数据，没有screener数据
            merged[address] = {
                "address": address,
                "symbol": token.get("token_symbol", "UNKNOWN"),
                "chain": token.get("chain", ""),
                "price": 0,
                "price_change_1h": 0,
                "price_change_24h": 0,
                "netflow_1h": token.get("net_flow_1h_usd", 0),
                "netflow_24h": token.get("net_flow_24h_usd", 0),
                "smart_money_count": token.get("trader_count", 1),
                "smart_money_avg_roi": 150,
                "smart_money_total_amount": abs(token.get("net_flow_1h_usd", 0)),
                "volume_24h": 0,
                "holder_concentration": 0.3
            }

    return list(merged.values())

def extract_smart_money_stats(netflow_tokens: List[Dict]) -> Dict[str, Dict]:
    """从净流入数据中提取Smart Money统计"""
    stats = {}

    for token in netflow_tokens:
        address = token.get("token_address") or token.get("address")
        if not address:
            continue

        # 这里简化处理，实际应该从Smart Money持仓数据中获取
        # 暂时用净流入作为代理指标
        stats[address] = {
            "count": len(token.get("smart_money_wallets", [])),  # 假设API返回
            "avg_roi": token.get("smart_money_avg_roi", 0),
            "total_amount": abs(token.get("net_flow_1h_usd", 0))
        }

    return stats

def main():
    """主扫描流程"""
    print(f"\n{'='*60}")
    print(f"🚀 Smart Money扫描开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # 初始化客户端
    nansen = NansenClient(NANSEN_API_KEY)
    scorer = SignalScorer(WEIGHTS)
    telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    # 加载已发送的代币
    sent_tokens = load_sent_tokens()
    print(f"📋 已过滤过去24小时内通知的代币: {len(sent_tokens)}个\n")

    all_signals = []
    total_scanned = 0

    # 扫描每条链
    for chain in CHAINS:
        print(f"🔍 扫描 {chain.upper()} 链...")

        # 获取Smart Money净流入
        netflow_data = nansen.get_smart_money_netflow(chain, timeframe="1h", top_n=50)
        print(f"   - 净流入数据: {len(netflow_data)}条")

        # 获取代币筛选数据
        screener_data = nansen.get_token_screener(chain, timeframe="1h", top_n=50)
        print(f"   - 筛选数据: {len(screener_data)}条")

        # 合并数据
        merged_tokens = merge_token_data(netflow_data, screener_data)
        total_scanned += len(merged_tokens)

        # 评分
        for token in merged_tokens:
            # 跳过已发送的代币
            if token["address"] in sent_tokens:
                continue

            # 评分
            score_result = scorer.score_token(token)

            # 只保留高分信号
            if score_result["score"] >= MIN_SCORE_THRESHOLD:
                all_signals.append({
                    "token": token,
                    "score": score_result,
                    "chain": chain
                })

        print(f"   ✅ {chain.upper()} 扫描完成\n")

    # 按分数排序，取前N个
    all_signals.sort(key=lambda x: x["score"]["score"], reverse=True)
    top_signals = all_signals[:MAX_SIGNALS_PER_RUN]

    print(f"\n📊 本轮扫描结果:")
    print(f"   - 扫描代币总数: {total_scanned}")
    print(f"   - 高分信号数: {len(all_signals)}")
    print(f"   - 发送通知数: {len(top_signals)}")
    print(f"   - 最低分数线: {MIN_SCORE_THRESHOLD}分\n")

    # 发送Telegram通知
    if top_signals:
        print(f"📤 发送Telegram通知...\n")

        for signal in top_signals:
            token = signal["token"]
            score_result = signal["score"]

            # 发送通知
            success = telegram.send_alert(token, score_result)

            if success:
                save_sent_token(token["address"])
                print(f"   ✅ {token['symbol']} - {score_result['score']}分")
            else:
                print(f"   ❌ {token['symbol']} - 发送失败")

        print(f"\n✅ 通知发送完成!")
    else:
        print(f"ℹ️  本轮无高分信号，暂不发送通知")

    # 保存扫描日志
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_scanned": 0,
        "high_score_signals": len(all_signals),
        "signals_sent": len(top_signals),
        "top_signals": [
            {
                "symbol": s["token"]["symbol"],
                "score": s["score"]["score"],
                "chain": s["chain"]
            }
            for s in top_signals
        ]
    }

    log_file = "scan_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"\n{'='*60}")
    print(f"✅ 扫描完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
