"""技能搜索 API"""

from fastapi import APIRouter, Query

from server.services.llm_service import llm_service

router = APIRouter()


@router.get("/skills/search")
async def search_skills(q: str = Query(""), role: str = Query(""), limit: int = Query(20)):
    """搜索技能关键词（调用 DeepSeek 生成，后续可接 Lightcast MCP）"""
    if role:
        skills = await llm_service.generate_module_options("skills_must", role, {})
        return {"code": 0, "data": skills[:limit]}
    return {"code": 0, "data": []}
