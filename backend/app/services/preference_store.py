"""
RAG 用户偏好系统（ChromaDB 向量数据库版）
- ChromaDB 持久化存储，内置 ANN 索引
- OpenAI Embedding API 生成向量
- 对外接口不变，调用方无需修改
"""
import os
import json
import hashlib
import logging
from datetime import datetime
from typing import List
from pathlib import Path

import chromadb
from openai import OpenAI
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent.parent
load_dotenv(backend_dir / ".env")

CHROMA_DIR = str(Path(__file__).parent.parent.parent / "data" / "chromadb")
logger = logging.getLogger(__name__)


def _get_openai_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    base_url = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    if "/v1/" in base_url:
        base_url = base_url.split("/v1/")[0] + "/v1"
    return OpenAI(api_key=api_key, base_url=base_url)


class UserPreferenceStore:
    """
    用户偏好向量存储（ChromaDB 版）
    - 每用户两个 collection：preferences 和 history
    - ChromaDB 自动管理索引、持久化、相似度检索
    - OpenAI Embedding API 负责生成向量
    """

    def __init__(self):
        os.makedirs(CHROMA_DIR, exist_ok=True)
        self._chroma = chromadb.PersistentClient(path=CHROMA_DIR)
        self._openai = None

    @property
    def openai(self):
        if self._openai is None:
            self._openai = _get_openai_client()
        return self._openai

    def _user_hash(self, user_id: str) -> str:
        return hashlib.md5(user_id.encode()).hexdigest()[:16]

    def _get_collection(self, user_id: str, kind: str):
        """获取用户的偏好或历史 collection"""
        name = f"user_{self._user_hash(user_id)}_{kind}"
        return self._chroma.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def _embed(self, text: str) -> List[float]:
        """调用 OpenAI Embedding API 生成向量"""
        try:
            resp = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding 生成失败: {e}")
            return []

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def save_preferences(self, user_id: str, preferences: dict) -> None:
        """保存用户偏好画像"""
        col = self._get_collection(user_id, "preferences")
        doc = self._preferences_to_text(preferences)
        embedding = self._embed(doc)
        if not embedding:
            return

        doc_id = f"pref_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        col.upsert(
            ids=[doc_id],
            documents=[doc],
            embeddings=[embedding],
            metadatas=[{
                "type": "preference",
                "timestamp": datetime.now().isoformat(),
                **{k: str(v) for k, v in preferences.items() if v},
            }],
        )
        logger.info(f"偏好已保存: user={user_id}, doc={doc_id}")

    def save_trip_history(self, user_id: str, trip_plan: dict) -> None:
        """保存行程历史"""
        col = self._get_collection(user_id, "history")
        city = trip_plan.get("city", "未知")
        days = len(trip_plan.get("days", []))
        attractions = []
        for day in trip_plan.get("days", []):
            for attr in day.get("attractions", []):
                attractions.append(attr.get("name", ""))

        doc = (
            f"目的地: {city}, 天数: {days}天, "
            f"景点: {', '.join(attractions[:10])}, "
            f"建议: {trip_plan.get('overall_suggestions', '')[:200]}"
        )
        embedding = self._embed(doc)
        if not embedding:
            return

        doc_id = f"trip_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        col.upsert(
            ids=[doc_id],
            documents=[doc],
            embeddings=[embedding],
            metadatas=[{
                "type": "trip_history",
                "city": city,
                "days": days,
                "timestamp": datetime.now().isoformat(),
            }],
        )
        logger.info(f"行程历史已保存: user={user_id}, city={city}")

    # ------------------------------------------------------------------
    # 检索
    # ------------------------------------------------------------------

    def retrieve_context(self, user_id: str, query: str, n_results: int = 3) -> str:
        """检索与当前请求最相关的偏好和历史上下文"""
        query_embedding = self._embed(query)
        if not query_embedding:
            return self._fallback_retrieve(user_id, n_results)

        contexts = []

        # 检索偏好
        try:
            pref_col = self._get_collection(user_id, "preferences")
            if pref_col.count() > 0:
                results = pref_col.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, pref_col.count()),
                )
                for doc in results.get("documents", [[]])[0]:
                    contexts.append(f"[用户偏好] {doc}")
        except Exception as e:
            logger.warning(f"偏好检索失败: {e}")

        # 检索行程历史
        try:
            hist_col = self._get_collection(user_id, "history")
            if hist_col.count() > 0:
                results = hist_col.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, hist_col.count()),
                )
                for doc in results.get("documents", [[]])[0]:
                    contexts.append(f"[历史行程] {doc}")
        except Exception as e:
            logger.warning(f"历史检索失败: {e}")

        return "\n".join(contexts) if contexts else ""

    def get_user_stats(self, user_id: str) -> dict:
        """获取用户数据统计"""
        stats = {"preference_count": 0, "history_count": 0}
        try:
            stats["preference_count"] = self._get_collection(user_id, "preferences").count()
        except Exception:
            pass
        try:
            stats["history_count"] = self._get_collection(user_id, "history").count()
        except Exception:
            pass
        return stats

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------

    def _fallback_retrieve(self, user_id: str, n_results: int) -> str:
        """Embedding 不可用时，取最近的记录"""
        contexts = []
        try:
            pref_col = self._get_collection(user_id, "preferences")
            if pref_col.count() > 0:
                results = pref_col.get(limit=n_results)
                for doc in results.get("documents", []):
                    contexts.append(f"[用户偏好] {doc}")
        except Exception:
            pass
        try:
            hist_col = self._get_collection(user_id, "history")
            if hist_col.count() > 0:
                results = hist_col.get(limit=n_results)
                for doc in results.get("documents", []):
                    contexts.append(f"[历史行程] {doc}")
        except Exception:
            pass
        return "\n".join(contexts[:n_results]) if contexts else ""

    @staticmethod
    def _preferences_to_text(prefs: dict) -> str:
        parts = []
        for k, v in prefs.items():
            if v:
                parts.append(f"{k}: {v}")
        return "，".join(parts) if parts else "暂无偏好数据"
