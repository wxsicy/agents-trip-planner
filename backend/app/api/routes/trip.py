import json
from fastapi import APIRouter
from app.models.schemas import TripPlanRequest, TripPlan
from app.agents.langgraph_builder import get_trip_app
from app.agents.langgraph_state import TripState
from app.services.preference_store import UserPreferenceStore
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# 初始化
preference_store = UserPreferenceStore()


@router.post("/plan", response_model=TripPlan)
async def create_trip_plan(request: TripPlanRequest) -> TripPlan:
    """
    生成旅行计划（LangGraph + Function Calling + RAG）
    图片来源：高德 POI 实拍图
    """
    logger.info(f"收到旅行规划请求: {request.city}, {request.days}天, user_id={request.user_id}")

    # 构建 LangGraph 初始状态
    initial_state: TripState = {
        "city": request.city,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "days": request.days,
        "people_count": request.people_count,
        "preferences": request.preferences,
        "pace": request.pace,
        "budget": request.budget,
        "transportation": request.transportation,
        "accommodation": request.accommodation,
        "food_preferences": request.food_preferences,
        "extra_requirements": request.extra_requirements,
        "user_id": request.user_id,
        "attraction_data": None,
        "attraction_raw": None,
        "weather_data": None,
        "hotel_data": None,
        "rag_context": None,
        "plan_json": None,
        "trip_plan": None,
        "error": None,
        "retry_count": 0,
    }

    # 执行 LangGraph
    app = get_trip_app()
    final_state = await app.ainvoke(initial_state)

    # 提取行程计划
    plan_data = final_state.get("trip_plan")
    if not plan_data:
        raise ValueError("行程计划生成失败")

    trip_plan = TripPlan(**plan_data) if isinstance(plan_data, dict) else plan_data

    # 按景点名逐一搜索高德 POI 图片
    from app.services.tools import AmapToolExecutor
    amap = AmapToolExecutor()
    photo_count = 0

    for day in trip_plan.days:
        for attraction in day.attractions:
            if attraction.image_url:
                continue
            try:
                raw = amap.execute("search_attractions", {"city": trip_plan.city, "keywords": attraction.name})
                data = json.loads(raw)
                for poi in data.get("pois", []):
                    photo = poi.get("photo", "")
                    if photo:
                        attraction.image_url = photo
                        photo_count += 1
                        break
            except Exception:
                pass

    logger.info(f"旅行规划完成: {trip_plan.city}, {len(trip_plan.days)}天, 图片{photo_count}张")
    return trip_plan


@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str):
    """获取用户偏好统计"""
    stats = preference_store.get_user_stats(user_id)
    return {"user_id": user_id, **stats}


@router.post("/preferences/{user_id}")
async def save_user_preferences(user_id: str, preferences: dict):
    """保存用户偏好"""
    preference_store.save_preferences(user_id, preferences)
    return {"status": "ok", "message": "偏好已保存"}
