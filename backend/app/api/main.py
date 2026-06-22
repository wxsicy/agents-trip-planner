from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import trip
app = FastAPI(
    title="智能旅行助手 API",
    description="多智能体旅行规划系统",
    version="1.0.0"
)
# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册路由
app.include_router(trip.router, prefix="/api/trip", tags=["旅行规划"])
@app.get("/")
async def root():
    return {"message": "智能旅行助手 API", "docs": "/docs"}