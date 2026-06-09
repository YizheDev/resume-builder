"""简历导出 API"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume

router = APIRouter()


@router.get("/resumes/{resume_id}/export")
def export_pdf(resume_id: int, format: str = "pdf", db: Session = Depends(get_db)):
    """
    导出简历为 PDF。
    优先使用 resumake-mcp (LaTeX)，失败时用 WeasyPrint 兜底。
    """
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    # TODO: 1) 尝试 resumake-mcp 生成 LaTeX PDF
    #       2) 失败则用 WeasyPrint 渲染 HTML 模板
    #       3) 返回 PDF 文件流

    return Response(content=b"PDF placeholder", media_type="application/pdf")
