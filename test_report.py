from nansen_client import NansenClient
from signal_scorer import SignalScorer
from config import NANSEN_API_KEY, WEIGHTS

client = NansenClient(NANSEN_API_KEY)
scorer = SignalScorer(WEIGHTS)

print("正在扫描...")

for chain in ['ethereum', 'solana', 'base']:
    netflow = client.get_smart_money_netflow(chain, '1h', 50)
    screener = client.get_token_screener(chain, '1h', 50)

    merged = {}
    for token in screener:
        address = token.get('token_address')
        if address:
            merged[address] = {
                'address': address,
                'symbol': token.get('token_symbol', 'UNKNOWN'),
                'chain': token.get('chain', ''),
                'price': token.get('price_usd', 0),
                'price_change_1h': 0,
                'price_change_24h': token.get('price_change') or 0,
                'netflow_1h': 0,
                'netflow_24h': 0,
                'smart_money_count': 0,
                'smart_money_avg_roi': 150,
                'smart_money_total_amount': 0,
                'volume_24h': token.get('volume', 0),
                'holder_concentration': 0.3
            }

    for token in netflow:
        address = token.get('token_address')
        if address in merged:
            merged[address]['netflow_1h'] = token.get('net_flow_1h_usd', 0)
            merged[address]['smart_money_count'] = token.get('trader_count', 1)

    results = []
    for token in merged.values():
        result = scorer.score_token(token)
        results.append((token, result))

    results.sort(key=lambda x: x[1]['score'], reverse=True)

    with open(f'report_{chain}.txt', 'w', encoding='utf-8') as f:
        f.write(f'Top 10 Signals - {chain.upper()}\n')
        f.write('='*80 + '\n\n')
        for token, result in results[:10]:
            f.write(f"Symbol: {token['symbol']}\n")
            f.write(f"Price: ${token['price']:.4f}\n")
            f.write(f"Score: {result['score']}/100\n")
            f.write(f"Recommendation: {result['recommendation']}\n")
            f.write(f"Volume 24h: ${token['volume_24h']:,.0f}\n")
            f.write(f"Smart Money Count: {token['smart_money_count']}\n")
            f.write(f"Netflow 1h: ${token['netflow_1h']:,.0f}\n")
            f.write('-'*40 + '\n\n')

print("报告已生成: report_ethereum.txt, report_solana.txt, report_base.txt")
