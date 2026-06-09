"""对话 API（简历生成的核心交互）"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume

router = APIRouter()


class ChatRequest(BaseModel):
    message: str  # 用户消息或选择


class ChatResponse(BaseModel):
    reply: str              # AI 回复
    module: str | None      # 当前模块名
    options: list[dict] | None  # 下一轮选项列表
    updated_fields: dict | None  # 更新的字段


@router.post("/resumes/{resume_id}/chat", response_model=ChatResponse)
def chat(resume_id: int, req: ChatRequest, db: Session = Depends(get_db)):
    """
    与 AI 对话，逐模块收集简历信息。
    AI 返回追问或选项列表，同时更新简历字段。
    """
    # TODO: 实现 LangGraph Agent Pipeline
    pass


@router.post("/resumes/{resume_id}/generate")
def generate_resume(resume_id: int, db: Session = Depends(get_db)):
    """全部模块收集完毕，一键生成完整简历内容"""
    # TODO: 调用 Agent Pipeline 生成 + Review
    pass
