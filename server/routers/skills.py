"""技能搜索 API（Lightcast MCP）"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/skills/search")
def search_skills(q: str = "", role: str = "", limit: int = 20):
    """
    搜索技能关键词。
    优先使用 Lightcast MCP (48000+ 标准化技能库)，
    不可用时 fallback 到 DeepSeek 生成。
    """
    # TODO: 集成 Lightcast MCP
    return {"code": 0, "data": []}
