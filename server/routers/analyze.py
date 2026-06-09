"""岗位分析 API"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyzeRequest(BaseModel):
    background: str  # 用户背景描述


class RoleRecommendation(BaseModel):
    role: str
    score: int
    reason: str
    skills: list[str]


class AnalyzeResponse(BaseModel):
    recommendations: list[RoleRecommendation]


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_background(req: AnalyzeRequest):
    """
    分析用户背景，推荐适合的岗位。
    调用 AI 根据教育/经历/技能匹配合适岗位。
    """
    # TODO: 实现 LLM 调用
    pass
