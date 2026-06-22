"""
LangGraph 状态定义
所有 Agent 节点共享的全局状态
"""
from typing import TypedDict, Optional, List, Dict, Any, Annotated
from operator import add


class TripState(TypedDict):
    """旅行规划全局状态"""

    # 输入
    city: str
    start_date: str
    end_date: str
    days: int
    people_count: int
    preferences: str
    pace: str
    budget: str
    transportation: str
    accommodation: str
    food_preferences: str
    extra_requirements: str
    user_id: Optional[str]

    # 中间结果
    attraction_data: Optional[str]
    attraction_raw: Optional[str]
    weather_data: Optional[str]
    hotel_data: Optional[str]
    rag_context: Optional[str]

    # 输出
    plan_json: Optional[str]
    trip_plan: Optional[Dict[str, Any]]
    error: Optional[str]
    retry_count: int
