"""岗位分析 API"""

from fastapi import APIRouter
from pydantic import BaseModel

from server.services.llm_service import llm_service

router = APIRouter()


class AnalyzeRequest(BaseModel):
    background: str


@router.post("/analyze")
async def analyze_background(req: AnalyzeRequest):
    """分析用户背景，返回推荐岗位（含 Lightcast 技能数据）"""
    roles = await llm_service.analyze_career(req.background)
    return {"code": 0, "data": {"recommendations": roles}}
