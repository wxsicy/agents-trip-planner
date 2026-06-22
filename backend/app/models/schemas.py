from pydantic import BaseModel, Field
from typing import Optional, List
from pydantic import field_validator


class Location(BaseModel):
    """位置信息（经纬度坐标）"""
    longitude: float = Field(default=0, description="经度")
    latitude: float = Field(default=0, description="纬度")


class Attraction(BaseModel):
    """景点信息"""
    name: str = Field(default="", description="景点名称")
    address: str = Field(default="", description="地址")
    location: Location = Field(default_factory=Location, description="经纬度坐标")
    visit_duration: int = Field(default=60, description="建议游览时间(分钟)")
    description: str = Field(default="", description="景点描述")
    category: Optional[str] = Field(default="景点", description="景点类别")
    rating: Optional[float] = Field(default=None, ge=0, le=5, description="评分")
    image_url: Optional[str] = Field(default=None, description="图片URL")
    ticket_price: int = Field(default=0, ge=0, description="门票价格(元)")


class Meal(BaseModel):
    """餐饮信息"""
    type: str = Field(default="lunch", description="餐饮类型：breakfast/lunch/dinner/snack")
    name: str = Field(default="", description="餐饮名称")
    address: Optional[str] = Field(default=None, description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_cost: int = Field(default=0, description="预估费用(元)")


class Hotel(BaseModel):
    """酒店信息"""
    name: str = Field(..., description="酒店名称")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格范围")
    rating: str = Field(default="", description="评分")
    distance: str = Field(default="", description="距离景点距离")
    type: str = Field(default="", description="酒店类型")
    estimated_cost: int = Field(default=0, description="预估费用(元/晚)")

    @field_validator('rating', 'price_range', 'distance', 'type', mode='before')
    def convert_to_string(cls, v):
        if v is None:
            return ""
        return str(v)


class Budget(BaseModel):
    """预算信息"""
    total_attractions: int = Field(default=0, description="景点门票总费用")
    total_hotels: int = Field(default=0, description="酒店总费用")
    total_meals: int = Field(default=0, description="餐饮总费用")
    total_transportation: int = Field(default=0, description="交通总费用")
    total: int = Field(default=0, description="总费用")


class WeatherInfo(BaseModel):
    """天气信息"""
    date: str = Field(default="", description="日期")
    day_weather: str = Field(default="晴", description="白天天气")
    night_weather: str = Field(default="多云", description="夜间天气")
    day_temp: int = Field(default=20, description="白天温度(摄氏度)")
    night_temp: int = Field(default=15, description="夜间温度(摄氏度)")
    wind_direction: str = Field(default="", description="风向")
    wind_power: str = Field(default="", description="风力")
    
    @field_validator('day_temp', 'night_temp', mode='before')
    def parse_temperature(cls, v):
        """解析温度字符串：'16°C' -> 16"""
        if isinstance(v, str):
            v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
            try:
                return int(v)
            except ValueError:
                return 0
        return v
    

class DayPlan(BaseModel):
    """单日行程"""
    date: str = Field(default="", description="日期")
    day_index: int = Field(default=0, description="第几天(从0开始)")
    description: str = Field(default="", description="当日行程描述")
    transportation: str = Field(default="", description="交通方式")
    accommodation: str = Field(default="", description="住宿安排")
    hotel: Optional[Hotel] = Field(default=None, description="酒店信息")
    attractions: List[Attraction] = Field(default_factory=list, description="景点列表")
    meals: List[Meal] = Field(default_factory=list, description="餐饮安排")


class TripPlanRequest(BaseModel):
    """旅行计划请求"""
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    days: int = Field(..., description="旅行天数", gt=0)
    people_count: int = Field(default=2, description="人数", gt=0)
    pace: str = Field(default="适中", description="节奏偏好：轻松/适中/紧凑")
    preferences: str = Field(default="历史文化", description="旅行偏好")
    food_preferences: str = Field(default="", description="饮食偏好")
    extra_requirements: str = Field(default="", description="额外要求")
    budget: str = Field(default="中等", description="预算级别")
    transportation: str = Field(default="公共交通", description="交通方式")
    accommodation: str = Field(default="经济型酒店", description="住宿类型")
    user_id: Optional[str] = Field(default=None, description="用户ID（用于 RAG 偏好检索）")


class TripPlan(BaseModel):
    """旅行计划（完整响应）"""
    city: str = Field(default="", description="目的地城市")
    start_date: str = Field(default="", description="开始日期")
    end_date: str = Field(default="", description="结束日期")
    days: List[DayPlan] = Field(default_factory=list, description="每日行程")
    weather_info: List[WeatherInfo] = Field(default_factory=list, description="天气信息")
    overall_suggestions: str = Field(default="", description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")
