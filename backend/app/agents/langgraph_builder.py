"""
LangGraph 状态图定义
将所有节点编排为有向图，支持条件路由和错误重试

流程:
  START → search_attractions → query_weather → search_hotels
        → retrieve_context → generate_plan → validate_plan
        → (条件) generate_plan (重试) 或 END
"""
import logging
from langgraph.graph import StateGraph, END

from .langgraph_state import TripState
from .langgraph_nodes import (
    search_attractions,
    query_weather,
    search_hotels,
    retrieve_context,
    generate_plan,
    validate_plan,
    should_retry,
)

logger = logging.getLogger(__name__)


def build_trip_graph() -> StateGraph:
    """构建旅行规划 LangGraph"""
    graph = StateGraph(TripState)

    # 注册节点
    graph.add_node("search_attractions", search_attractions)
    graph.add_node("query_weather", query_weather)
    graph.add_node("search_hotels", search_hotels)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_plan", generate_plan)
    graph.add_node("validate_plan", validate_plan)

    # 串行边
    graph.set_entry_point("search_attractions")
    graph.add_edge("search_attractions", "query_weather")
    graph.add_edge("query_weather", "search_hotels")
    graph.add_edge("search_hotels", "retrieve_context")
    graph.add_edge("retrieve_context", "generate_plan")
    graph.add_edge("generate_plan", "validate_plan")

    # 条件边：验证失败则回到 generate_plan 重试，最多 2 次
    graph.add_conditional_edges(
        "validate_plan",
        should_retry,
        {
            "generate_plan": "generate_plan",
            "end": END,
        },
    )

    return graph


# 编译一次，全局复用
_trip_app = None


def get_trip_app():
    """获取编译后的 LangGraph 应用（单例）"""
    global _trip_app
    if _trip_app is None:
        _trip_app = build_trip_graph().compile()
        logger.info("LangGraph 旅行规划图已编译")
    return _trip_app
