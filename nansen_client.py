"""
Nansen API客户端
"""
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime

class NansenClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nansen.ai/api/v1"
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json"
        }

    def get_smart_money_netflow(
        self,
        chain: str,
        timeframe: str = "1h",
        top_n: int = 50
    ) -> List[Dict]:
        """获取Smart Money净流入数据"""
        url = f"{self.base_url}/smart-money/netflow"

        timeframe_field_map = {
            "1h": "net_flow_1h_usd",
            "24h": "net_flow_24h_usd"
        }
        order_field = timeframe_field_map.get(timeframe, "net_flow_1h_usd")

        payload = {
            "chains": [chain],
            "order_by": [{"field": order_field, "direction": "DESC"}],
            "pagination": {"page": 1, "per_page": top_n}
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")
                return []
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Request Error: {e}")
            return []

    def get_token_screener(
        self,
        chain: str,
        timeframe: str = "1h",
        top_n: int = 50
    ) -> List[Dict]:
        """获取代币筛选数据"""
        url = f"{self.base_url}/token-screener"

        payload = {
            "chains": [chain],
            "timeframe": timeframe,
            "filters": {"liquidity": {"from": 100000}},
            "order_by": [{"field": "netflow", "direction": "DESC"}],
            "pagination": {"page": 1, "per_page": top_n}
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code != 200:
                return []
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            print(f"Request Error: {e}")
            return []

    def get_smart_money_positions(
        self,
        token_address: str,
        chain: str
    ) -> Dict:
        """获取Smart Money持仓详情"""
        url = f"{self.base_url}/smart-money/positions"

        payload = {
            "chain": chain,
            "token_address": token_address
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code != 200:
                return {}
            data = response.json()
            return data
        except Exception as e:
            print(f"Request Error: {e}")
            return {}
