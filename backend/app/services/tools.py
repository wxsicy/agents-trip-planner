"""
Function Calling 工具定义
用 OpenAI 原生 Tool Use API 
"""
import httpx
import json
from typing import Any
from app.config import get_settings

# ============================================================
# 1. OpenAI Function Schema 定义
# ============================================================

AMAP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_attractions",
            "description": "搜索目的地城市的景点信息，返回景点名称、地址、坐标等",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如'北京'、'上海'"
                    },
                    "keywords": {
                        "type": "string",
                        "description": "搜索关键词，如'景点'、'博物馆'、'公园'"
                    }
                },
                "required": ["city", "keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_weather",
            "description": "查询指定城市的天气预报信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如'北京'"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_hotels",
            "description": "搜索目的地城市的酒店住宿信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    },
                    "keywords": {
                        "type": "string",
                        "description": "酒店类型关键词，如'经济型酒店'、'豪华酒店'、'民宿'"
                    }
                },
                "required": ["city", "keywords"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_directions",
            "description": "查询两个地点之间的路线和交通信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "起点坐标，格式：经度,纬度"
                    },
                    "destination": {
                        "type": "string",
                        "description": "终点坐标，格式：经度,纬度"
                    }
                },
                "required": ["origin", "destination"]
            }
        }
    }
]

# ============================================================
# 2. 工具执行器：调用高德地图 API
# ============================================================


class AmapToolExecutor:
    """高德地图工具执行器 - 真实 API 调用"""

    BASE_URL = "https://restapi.amap.com/v3"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.amap_api_key

    def execute(self, tool_name: str, arguments: dict) -> str:
        """根据工具名称分发执行，返回 JSON 字符串结果"""
        dispatch = {
            "search_attractions": self._search_poi,
            "query_weather": self._query_weather,
            "search_hotels": self._search_poi,
            "get_directions": self._get_directions,
        }
        handler = dispatch.get(tool_name)
        if not handler:
            return json.dumps({"error": f"未知工具: {tool_name}"})
        try:
            return handler(tool_name, arguments)
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _search_poi(self, tool_name: str, args: dict) -> str:
        """POI 搜索（景点/酒店共用）"""
        city = args.get("city", "")
        keywords = args.get("keywords", "景点")
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "city": city,
            "citylimit": "true",
            "output": "json",
            "offset": 10,
        }
        resp = httpx.get(f"{self.BASE_URL}/place/text", params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "1":
            return json.dumps({"error": data.get("info", "搜索失败")})

        results = []
        for poi in data.get("pois", [])[:10]:
            loc = poi.get("location", "0,0").split(",")
            # 提取 POI 图片
            photos = [p.get("url", "") for p in poi.get("photos", []) if p.get("url")]
            results.append({
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": {
                    "longitude": float(loc[0]) if len(loc) > 1 else 0,
                    "latitude": float(loc[1]) if len(loc) > 1 else 0,
                },
                "type": poi.get("type", ""),
                "rating": poi.get("biz_ext", {}).get("rating", ""),
                "cost": poi.get("biz_ext", {}).get("cost", ""),
                "photo": photos[0] if photos else "",
            })
        return json.dumps({"count": len(results), "pois": results}, ensure_ascii=False)

    def _query_weather(self, tool_name: str, args: dict) -> str:
        """天气查询"""
        city = args.get("city", "")
        params = {
            "key": self.api_key,
            "city": city,
            "extensions": "all",
            "output": "json",
        }
        resp = httpx.get(f"{self.BASE_URL}/weather/weatherInfo", params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "1":
            return json.dumps({"error": data.get("info", "天气查询失败")})

        forecasts = []
        for cast in data.get("forecasts", [{}])[0].get("casts", []):
            forecasts.append({
                "date": cast.get("date", ""),
                "day_weather": cast.get("dayweather", ""),
                "night_weather": cast.get("nightweather", ""),
                "day_temp": int(cast.get("daytemp", 0)),
                "night_temp": int(cast.get("nighttemp", 0)),
                "wind_direction": cast.get("daywind", ""),
                "wind_power": cast.get("daypower", ""),
            })
        return json.dumps({"forecasts": forecasts}, ensure_ascii=False)

    def _get_directions(self, tool_name: str, args: dict) -> str:
        """路线规划"""
        origin = args.get("origin", "")
        destination = args.get("destination", "")
        params = {
            "key": self.api_key,
            "origin": origin,
            "destination": destination,
            "strategy": 0,
        }
        resp = httpx.get(f"{self.BASE_URL}/direction/driving", params=params, timeout=10)
        data = resp.json()
        if data.get("status") != "1":
            return json.dumps({"error": data.get("info", "路线查询失败")})

        route = data.get("route", {})
        paths = []
        for p in route.get("paths", [])[:3]:
            paths.append({
                "distance": p.get("distance", ""),
                "duration": p.get("duration", ""),
                "strategy": p.get("strategy", ""),
            })
        return json.dumps({"paths": paths}, ensure_ascii=False)
