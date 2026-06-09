"""简历 CRUD API"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume

router = APIRouter()


class CreateResumeRequest(BaseModel):
    role: str
    title: str = "未命名简历"


@router.post("/resumes")
def create_resume(req: CreateResumeRequest, db: Session = Depends(get_db)):
    resume = Resume(role=req.role, title=req.title)
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return {"code": 0, "data": resume_to_dict(resume)}


@router.get("/resumes")
def list_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).order_by(Resume.updated_at.desc()).all()
    return {"code": 0, "data": [resume_to_dict(r) for r in resumes]}


@router.get("/resumes/{resume_id}")
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}
    return {"code": 0, "data": resume_to_dict(resume)}


@router.put("/resumes/{resume_id}")
def update_resume(resume_id: int, req: dict, db: Session = Depends(get_db)):
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}
    for key in ["title", "template", "status"]:
        if key in req:
            setattr(resume, key, req[key])
    # 合并 data 字段
    if "data" in req:
        existing_data = resume.data or {}
        incoming = req["data"]
        if isinstance(incoming, str):
            incoming = json.loads(incoming)
        if incoming:
            existing_data.update(incoming)
            from sqlalchemy.orm.attributes import flag_modified
            resume.data = existing_data
            flag_modified(resume, "data")
    # 合并 selections 字段
    if "selections" in req and req["selections"]:
        existing_sel = resume.selections or {}
        existing_sel.update(req["selections"])
        resume.selections = existing_sel
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(resume, "selections")
    db.commit()
    return {"code": 0, "data": resume_to_dict(resume)}


@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    db.query(Resume).filter_by(id=resume_id).delete()
    db.commit()
    return {"code": 0, "message": "已删除"}


def resume_to_dict(r: Resume) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "role": r.role,
        "template": r.template,
        "data": r.data,
        "selections": r.selections or {},
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }
