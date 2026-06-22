"""
LangGraph 节点实现
每个节点是一个纯函数：接收 state，返回部分 state 更新
使用 OpenAI Function Calling 调用高德地图工具
"""
import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from .langgraph_state import TripState
from app.services.tools import AMAP_TOOLS, AmapToolExecutor
from app.services.preference_store import UserPreferenceStore

backend_dir = Path(__file__).parent.parent.parent
load_dotenv(backend_dir / ".env")

logger = logging.getLogger(__name__)

# 全局共享实例
_tool_executor = AmapToolExecutor()
_preference_store = UserPreferenceStore()


def _get_client() -> OpenAI:
    """获取 OpenAI 客户端"""
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    base_url = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    if "/v1/" in base_url:
        base_url = base_url.split("/v1/")[0] + "/v1"
    return OpenAI(api_key=api_key, base_url=base_url)


def _get_model() -> str:
    return os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "mimo-v2.5-pro"))


def _call_with_tools(system_prompt: str, user_message: str) -> str:
    """
    带 Function Calling 的 LLM 调用
    如果模型返回 tool_calls，执行工具后将结果反馈给模型获取最终回答
    """
    client = _get_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=_get_model(),
        messages=messages,
        tools=AMAP_TOOLS,
        tool_choice="auto",
        temperature=0.3,
    )

    msg = response.choices[0].message

    # 如果模型要求调用工具
    if msg.tool_calls:
        messages.append(msg.model_dump())  # 追加 assistant 的 tool_calls 消息
        for tc in msg.tool_calls:
            func_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}
            # 执行工具
            result = _tool_executor.execute(func_name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })
        # 带工具结果再次调用，获取最终回答
        final_response = client.chat.completions.create(
            model=_get_model(),
            messages=messages,
            temperature=0.3,
        )
        return final_response.choices[0].message.content or ""

    return msg.content or ""


# ============================================================
# 节点函数
# ============================================================


def search_attractions(state: TripState) -> dict:
    """节点1：搜索景点（Function Calling）"""
    logger.info(f"[Node] 搜索景点: {state['city']}")
    prompt = "你是景点搜索专家。请使用工具搜索用户指定城市的景点，然后用中文总结搜索结果。"
    user_msg = f"请搜索{state['city']}的{state['preferences']}景点，返回前10个结果。"
    result = _call_with_tools(prompt, user_msg)
    raw_poi = _tool_executor.execute("search_attractions", {"city": state["city"], "keywords": state["preferences"]})
    logger.info(f"[Node] 搜索景点完成，结果长度: {len(result)}")
    return {"attraction_data": result, "attraction_raw": raw_poi}


def query_weather(state: TripState) -> dict:
    """节点2：查询天气（Function Calling）"""
    logger.info(f"[Node] 查询天气: {state['city']}")
    prompt = "你是天气查询专家。请使用工具查询天气，然后用中文总结天气预报。"
    user_msg = f"请查询{state['city']}从{state['start_date']}到{state['end_date']}的天气预报。"
    result = _call_with_tools(prompt, user_msg)
    logger.info(f"[Node] 查询天气完成")
    return {"weather_data": result}


def search_hotels(state: TripState) -> dict:
    """节点3：搜索酒店（Function Calling）"""
    logger.info(f"[Node] 搜索酒店: {state['city']} - {state['accommodation']}")
    prompt = "你是酒店推荐专家。请使用工具搜索酒店，然后用中文总结酒店信息。"
    user_msg = f"请搜索{state['city']}的{state['accommodation']}，预算约{state['budget']}元/人。"
    result = _call_with_tools(prompt, user_msg)
    logger.info(f"[Node] 搜索酒店完成")
    return {"hotel_data": result}


def retrieve_context(state: TripState) -> dict:
    """节点4：RAG 检索用户偏好上下文"""
    user_id = state.get("user_id")
    if not user_id:
        logger.info("[Node] 无 user_id，跳过 RAG 检索")
        return {"rag_context": ""}

    logger.info(f"[Node] RAG 检索偏好上下文: user_id={user_id}")
    query = f"{state['city']} {state['preferences']} {state['accommodation']} {state['budget']}"
    context = _preference_store.retrieve_context(user_id, query, n_results=3)
    logger.info(f"[Node] RAG 检索完成，上下文长度: {len(context)}")

    # 同时保存当前偏好
    _preference_store.save_preferences(user_id, {
        "目的地": state["city"],
        "偏好类型": state["preferences"],
        "节奏偏好": state["pace"],
        "住宿偏好": state["accommodation"],
        "预算范围": state["budget"],
        "饮食偏好": state.get("food_preferences", ""),
    })

    return {"rag_context": context}


def generate_plan(state: TripState) -> dict:
    """节点5：整合信息，生成行程计划（结构化 JSON 输出）"""
    logger.info("[Node] 生成行程计划")

    rag_section = ""
    if state.get("rag_context"):
        rag_section = f"""
**用户历史偏好（RAG 检索结果）：**
{state['rag_context']}
请参考用户的历史偏好来个性化行程安排。
"""

    prompt = """你是行程规划专家。请根据景点、天气、酒店信息和用户偏好，生成详细的旅行计划。

严格按照以下JSON格式返回，不要包含任何其他文本:
{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "当日行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿安排",
      "hotel": {"name": "酒店名", "address": "地址", "price_range": "价格范围", "rating": "评分", "estimated_cost": 300},
      "attractions": [
        {"name": "景点名", "address": "地址", "location": {"longitude": 116.39, "latitude": 39.91}, "visit_duration": 120, "description": "描述", "ticket_price": 60}
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐", "estimated_cost": 60},
        {"type": "dinner", "name": "晚餐", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {"date": "YYYY-MM-DD", "day_weather": "晴", "night_weather": "多云", "day_temp": 25, "night_temp": 18, "wind_direction": "东南风", "wind_power": "3级"}
  ],
  "overall_suggestions": "总体建议",
  "budget": {"total_attractions": 180, "total_hotels": 600, "total_meals": 480, "total_transportation": 100, "total": 1360}
}"""

    user_msg = f"""
请为以下旅行生成详细计划:

**用户需求:**
- 目的地: {state['city']}
- 日期: {state['start_date']} 至 {state['end_date']}（{state['days']}天）
- 人数: {state['people_count']}人
- 偏好: {state['preferences']}
- 节奏: {state['pace']}
- 预算: {state['budget']}元/人
- 交通: {state['transportation']}
- 住宿: {state['accommodation']}
- 饮食: {state.get('food_preferences', '无')}
- 特殊要求: {state.get('extra_requirements', '无')}

**景点信息:**
{state.get('attraction_data', '无')}

**天气信息:**
{state.get('weather_data', '无')}

**酒店信息:**
{state.get('hotel_data', '无')}
{rag_section}

请严格按照 JSON 格式输出。每天安排 2-3 个景点，包含三餐，提供预算明细。"""

    client = _get_client()
    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    plan_json = response.choices[0].message.content or "{}"
    logger.info(f"[Node] 行程计划生成完成，JSON 长度: {len(plan_json)}")

    # 保存行程历史到 RAG
    user_id = state.get("user_id")
    if user_id:
        try:
            plan_data = json.loads(plan_json)
            _preference_store.save_trip_history(user_id, plan_data)
            logger.info("[Node] 行程历史已保存到 RAG")
        except Exception as e:
            logger.warning(f"[Node] 保存行程历史失败: {e}")

    return {"plan_json": plan_json}


def validate_plan(state: TripState) -> dict:
    """节点6：验证行程 JSON 是否合法"""
    logger.info("[Node] 验证行程计划")
    plan_json = state.get("plan_json", "{}")

    try:
        data = json.loads(plan_json)
    except json.JSONDecodeError:
        # 尝试从 markdown 代码块中提取
        cleaned = plan_json.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
        import re
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            data = json.loads(match.group())
        else:
            retry = state.get("retry_count", 0)
            if retry >= 2:
                return {"trip_plan": _create_fallback(state), "error": None}
            return {"error": "JSON 解析失败", "retry_count": retry + 1}

    # 结构验证
    required_keys = ["city", "days", "overall_suggestions"]
    missing = [k for k in required_keys if k not in data]
    if missing:
        retry = state.get("retry_count", 0)
        if retry >= 2:
            return {"trip_plan": _create_fallback(state), "error": None}
        return {"error": f"缺少字段: {missing}", "retry_count": retry + 1}

    logger.info("[Node] 行程计划验证通过")
    return {"trip_plan": data, "error": None}


def should_retry(state: TripState) -> str:
    """条件边：判断是否需要重试"""
    if state.get("error") and state.get("retry_count", 0) < 3:
        return "generate_plan"
    return "end"


def _create_fallback(state: TripState) -> dict:
    """降级方案"""
    from datetime import datetime, timedelta
    start = datetime.strptime(state["start_date"], "%Y-%m-%d")
    days = []
    for i in range(state["days"]):
        d = start + timedelta(days=i)
        days.append({
            "date": d.strftime("%Y-%m-%d"),
            "day_index": i,
            "description": f"第{i+1}天行程",
            "transportation": state["transportation"],
            "accommodation": state["accommodation"],
            "hotel": None,
            "attractions": [],
            "meals": [
                {"type": "breakfast", "name": "早餐", "estimated_cost": 30},
                {"type": "lunch", "name": "午餐", "estimated_cost": 60},
                {"type": "dinner", "name": "晚餐", "estimated_cost": 80},
            ],
        })
    return {
        "city": state["city"],
        "start_date": state["start_date"],
        "end_date": state["end_date"],
        "days": days,
        "weather_info": [],
        "overall_suggestions": "行程生成遇到问题，请手动调整。",
        "budget": {"total_attractions": 0, "total_hotels": 0, "total_meals": 170 * state["days"], "total_transportation": 0, "total": 170 * state["days"]},
    }
