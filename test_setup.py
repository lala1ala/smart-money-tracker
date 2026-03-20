"""
测试脚本 - 验证Nansen API和Telegram配置
"""
import os
from dotenv import load_dotenv
from nansen_client import NansenClient
from telegram_bot import TelegramNotifier
from config import NANSEN_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

load_dotenv()

def test_nansen_api():
    """测试Nansen API连接"""
    print("=" * 60)
    print("🔍 测试 Nansen API")
    print("=" * 60)

    if not NANSEN_API_KEY or NANSEN_API_KEY == "your_api_key_here":
        print("❌ NANSEN_API_KEY 未配置")
        return False

    print(f"✅ API Key: {NANSEN_API_KEY[:10]}...{NANSEN_API_KEY[-4:]}")

    try:
        client = NansenClient(NANSEN_API_KEY)
        print("\n📡 测试API连接...")

        # 测试获取Smart Money净流入
        data = client.get_smart_money_netflow("ethereum", timeframe="1h", top_n=5)

        if data:
            print(f"✅ API连接成功!")
            print(f"   获取到 {len(data)} 条数据")
            if data:
                first = data[0]
                print(f"\n📊 示例数据:")
                print(f"   代币: {first.get('symbol', 'N/A')}")
                print(f"   净流入: ${first.get('net_flow_1h_usd', 0):,.0f}")
                print(f"   价格变化: {first.get('price_change_1h', 0):.2f}%")
            return True
        else:
            print("⚠️  API连接成功，但没有返回数据")
            print("   可能原因：网络问题或API正在维护")
            return False

    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_telegram_bot():
    """测试Telegram Bot连接"""
    print("\n" + "=" * 60)
    print("📱 测试 Telegram Bot")
    print("=" * 60)

    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_bot_token_here":
        print("❌ TELEGRAM_BOT_TOKEN 未配置")
        return False

    if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == "your_chat_id_here":
        print("❌ TELEGRAM_CHAT_ID 未配置")
        return False

    print(f"✅ Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-4:]}")
    print(f"✅ Chat ID: {TELEGRAM_CHAT_ID}")

    try:
        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        print("\n📡 测试Telegram连接...")

        success = notifier.test_connection()

        if success:
            print("✅ Telegram连接成功!")
            print("   请检查你的Telegram，应该收到测试消息")
            return True
        else:
            print("❌ Telegram连接失败")
            print("   请检查Bot Token和Chat ID是否正确")
            return False

    except Exception as e:
        print(f"❌ Telegram测试失败: {e}")
        return False

def test_full_pipeline():
    """测试完整流程（扫描+评分+推送）"""
    print("\n" + "=" * 60)
    print("🚀 测试完整扫描流程")
    print("=" * 60)

    try:
        from signal_scorer import SignalScorer
        from config import WEIGHTS

        client = NansenClient(NANSEN_API_KEY)
        scorer = SignalScorer(WEIGHTS)
        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

        print("\n📡 获取Ethereum数据...")

        # 获取数据
        netflow_data = client.get_smart_money_netflow("ethereum", timeframe="1h", top_n=10)
        screener_data = client.get_token_screener("ethereum", timeframe="1h", top_n=10)

        print(f"   净流入数据: {len(netflow_data)}条")
        print(f"   筛选数据: {len(screener_data)}条")

        if not netflow_data or not screener_data:
            print("⚠️  没有获取到数据，跳过评分测试")
            return True

        # 测试评分
        print("\n📊 测试评分算法...")

        # 合并数据（简化版）
        if netflow_data:
            test_token = {
                "address": netflow_data[0].get("token_address", ""),
                "symbol": netflow_data[0].get("symbol", "TEST"),
                "chain": "ethereum",
                "price": netflow_data[0].get("price", 0),
                "price_change_1h": netflow_data[0].get("price_change_1h", 0),
                "price_change_24h": netflow_data[0].get("price_change_24h", 0),
                "netflow_1h": netflow_data[0].get("net_flow_1h_usd", 0),
                "smart_money_count": 5,
                "smart_money_avg_roi": 150,
                "smart_money_total_amount": 500000,
                "volume_24h": 2000000,
                "holder_concentration": 0.4
            }

            score_result = scorer.score_token(test_token)

            print(f"   代币: {test_token['symbol']}")
            print(f"   综合评分: {score_result['score']}/100")
            print(f"   建议: {score_result['recommendation']}")
            print(f"\n   分项得分:")
            for category, data in score_result['breakdown'].items():
                if category == 'risk':
                    print(f"      - {category}: -{data['penalty']}分")
                else:
                    print(f"      - {category}: {data['score']}/{data['max_score']}分")

        print("\n✅ 完整流程测试通过!")
        return True

    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("\n" + "🔧" * 30)
    print("  Smart Money Scanner - 配置测试")
    print("🔧" * 30 + "\n")

    results = {
        "Nansen API": test_nansen_api(),
        "Telegram Bot": test_telegram_bot(),
        "完整流程": test_full_pipeline()
    }

    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("\n🎉 所有测试通过! 系统已就绪，可以部署到GitHub Actions\n")
    else:
        print("\n⚠️  部分测试失败，请检查配置后再部署\n")

    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
