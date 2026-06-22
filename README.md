# 🧳 智能旅行助手

基于多智能体协作的 AI 旅行规划系统，输入目的地和偏好，自动生成包含景点、餐饮、酒店、天气和预算的完整行程。

## 核心特性

- **LangGraph 多智能体编排** — 景点搜索、天气查询、酒店推荐、行程生成由 6 个节点组成的有向图自动调度，支持错误重试和降级兜底
- **OpenAI Function Calling** — 通过原生 Tool Use API 调用高德地图工具，替代文本格式解析，准确率更高
- **RAG 用户偏好系统** — 基于 ChromaDB 向量数据库存储用户偏好和行程历史，检索相似上下文注入行程生成，越用越懂你
- **高德地图 POI 实拍图** — 行程中每个景点自动匹配高德地图实拍照片
- **行程编辑与导出** — 支持景点上下移动、删除，导出为图片或 PDF

## 项目展示

### 首页 — 旅行需求输入

填写目的地城市、出行日期、人数、旅行节奏、住宿偏好、预算，以及旅行偏好和饮食偏好标签，支持自由组合选择。

![首页]

### 规划中 — 多智能体协作进度

点击"开始规划我的旅程"后，系统依次执行景点搜索、天气查询、酒店推荐、RAG 偏好检索、行程生成，进度条实时展示当前阶段。

![规划进度]

### 结果页 — 行程概览与预算

行程生成后自动跳转结果页，顶部展示目的地城市、出行日期和总体建议，下方分项展示景点门票、酒店住宿、餐饮费用、交通费用及预估总费用。

![行程概览]

### 结果页 — 景点地图

集成高德地图 JS SDK，自动标注行程中所有景点位置并编号，点击可查看详情，地图自动缩放适配所有标记点。

![景点地图]

### 结果页 — 每日行程（Day 1）

每天的行程以卡片形式展示，包含景点实拍图（高德 POI 图片）、地址、门票价格、游览时长、交通方式和餐饮安排。

![每日行程]

### 结果页 — 每日行程（Day 2）

每日行程持续滚动展示，支持编辑模式下对景点进行上移、下移、删除操作，餐饮以彩色标签区分早中晚餐。

![每日行程]

### 结果页 — 天气信息

底部展示目的地未来几天的天气预报，包括白天/夜间天气、温度、风向风力，方便用户提前准备行装。

![天气信息]

### 结果页 — 导出与编辑

右下角固定操作栏提供"编辑行程"、"导出行程"（支持导出为图片和 PDF）、"返回首页"功能，随时可操作无需滚动到底部。

![操作栏]

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Ant Design Vue + Vite |
| 后端 | Python + FastAPI + LangGraph |
| AI | OpenAI API（Function Calling + JSON Mode + Embedding） |
| 工具 | 高德地图 REST API（景点搜索、天气、路线规划） |
| 向量数据库 | ChromaDB（用户偏好存储与检索） |
| 地图 | 高德地图 JS SDK（前端地图渲染） |

## 系统架构

```
用户输入需求
    ↓
┌─────────────────────────────────────────────┐
│              LangGraph 状态图                 │
│                                             │
│  search_attractions ──→ query_weather       │
│         ↓                    ↓              │
│   search_hotels ──→ retrieve_context (RAG)  │
│                          ↓                  │
│                    generate_plan             │
│                          ↓                  │
│                    validate_plan             │
│                     ↙        ↘              │
│               重试(≤2次)      END            │
└─────────────────────────────────────────────┘
    ↓
高德 POI 图片匹配 → 返回完整行程
```

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+

### 2. 克隆项目

```bash
git clone https://github.com/wxsicy/agents-trip-planner.git
cd agents-trip-planner
```

### 3. 后端启动

```bash
cd backend
pip install -r requirements.txt
```

创建 `backend/.env` 文件：

```env
# LLM API
LLM_API_KEY=你的API密钥
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 高德地图
AMAP_API_KEY=你的高德Key
AMAP_JS_KEY=你的高德JS Key
```

启动后端：

```bash
python run.py
```

后端运行在 `http://localhost:8000`

### 4. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:5173`

## 项目结构

```
agents-trip-planner/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py              # FastAPI 入口
│   │   │   └── routes/trip.py       # API 路由
│   │   ├── agents/
│   │   │   ├── langgraph_state.py   # LangGraph 状态定义
│   │   │   ├── langgraph_nodes.py   # 6 个节点函数
│   │   │   └── langgraph_builder.py # 状态图编排
│   │   ├── services/
│   │   │   ├── tools.py             # Function Calling 工具 + 高德 API
│   │   │   └── preference_store.py  # RAG 偏好存储（ChromaDB）
│   │   ├── models/schemas.py        # Pydantic 数据模型
│   │   └── config.py                # 配置管理
│   ├── data/chromadb/               # 向量数据库存储（自动生成）
│   ├── requirements.txt
│   └── run.py                       # 启动脚本
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue             # 输入表单页
│   │   │   └── Result.vue           # 结果展示页
│   │   ├── services/api.ts          # API 请求封装
│   │   ├── types/index.ts           # TypeScript 类型定义
│   │   ├── router/index.ts          # 路由配置
│   │   ├── App.vue                  # 根组件
│   │   └── main.ts                  # 入口文件
│   ├── public/
│   │   └── default-attraction.png   # 默认景点占位图
│   ├── package.json
│   └── vite.config.ts
├── .gitignore
└── README.md
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/trip/plan` | 生成旅行计划 |
| GET | `/api/trip/preferences/{user_id}` | 获取用户偏好统计 |
| POST | `/api/trip/preferences/{user_id}` | 保存用户偏好 |

## 许可

MIT
