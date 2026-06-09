"""对话 API — 简历生成核心交互"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume
from server.services.llm_service import llm_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = ""           # 用户消息
    action: str = "next"        # next / regenerate / polish / generate_all
    module: str = ""            # 当前模块
    custom_text: str = ""       # 自定义输入（润色用）


@router.post("/resumes/{resume_id}/chat")
async def chat(resume_id: int, req: ChatRequest, db: Session = Depends(get_db)):
    """核心对话接口"""
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    collected = resume.data or {}
    selections = resume.selections or {}
    role = resume.role

    # 获取当前进度（personal 通过 data.personal 判断是否完成）
    modules = ["personal", "education", "awards", "experience", "projects", "skills", "summary"]
    current_module = "personal"
    for m in modules:
        if m == "personal":
            if collected.get("personal", {}).get("name"):  # personal 已填
                continue
            current_module = "personal"
            break
        elif m not in selections:
            current_module = m
            break
    else:
        current_module = "done"

    if current_module == "done":
        return {"code": 0, "data": {"reply": "所有模块已完成！请点击生成简历。", "module": None, "options": None, "status": "ready"}}

    # 按 action 分发
    if req.action == "polish" and req.custom_text:
        polished = await llm_service.polish_description(req.custom_text, role)
        return {"code": 0, "data": {"reply": f"已润色：\n\n{polished}", "polished": polished}}

    if req.action == "generate_all":
        return await _generate_full_resume(resume, db)

    if req.action == "regenerate":
        return await _get_module_options(current_module, role, collected, selections)

    # 默认：获取当前模块的选项
    return await _get_module_options(current_module, role, collected, selections)


async def _get_module_options(module: str, role: str, collected: dict, selections: dict) -> dict:
    """为当前模块生成选项"""
    option_map = {
        "education": ("education_courses", "📚 教育背景 — 请勾选相关课程"),
        "awards": ("awards", "🏆 奖项荣誉 — 请勾选你获得的荣誉"),
        "experience": ("experience", "💼 实习经历 — 请勾选你做过的内容"),
        "projects": ("projects", "📦 项目经历 — 请勾选你做过的项目类型"),
        "skills": ("skills_must", "🛠️ 必备技能 — 请勾选你掌握的技能"),
    }

    if module == "personal":
        return {
            "code": 0,
            "data": {
                "reply": "请填写你的基本信息。",
                "module": "personal",
                "options": None,
                "status": "chatting",
            }
        }

    if module == "summary":
        versions = []
        for style, label in [("technical", "技术深度向"), ("balanced", "全面发展向"), ("growth", "成长潜力向")]:
            text = await llm_service.generate_self_evaluation(role, collected, style)
            versions.append({"id": style, "label": text, "style": label})
        return {
            "code": 0,
            "data": {
                "reply": "请选择你喜欢的自我评价风格（可修改）：",
                "module": "summary",
                "options": versions,
                "status": "chatting",
            }
        }

    if module == "skills":
        must = await llm_service.generate_module_options("skills_must", role, collected)
        plus = await llm_service.generate_module_options("skills_plus", role, collected)
        optional = await llm_service.generate_module_options("skills_optional", role, collected)
        return {
            "code": 0,
            "data": {
                "reply": "🛠️ 技能 — 请勾选你掌握的技能",
                "module": "skills",
                "options": {"must": must, "plus": plus, "optional": optional},
                "status": "chatting",
            }
        }

    if module in option_map:
        key, greeting = option_map[module]
        options = await llm_service.generate_module_options(key, role, collected)
        return {
            "code": 0,
            "data": {
                "reply": greeting,
                "module": module,
                "options": options,
                "status": "chatting",
            }
        }

    return {"code": 0, "data": {"reply": "请继续", "module": module, "options": None}}


async def _generate_full_resume(resume: Resume, db: Session):
    """一键生成完整简历"""
    selections = resume.selections or {}
    custom = resume.data or {}
    role = resume.role

    content = await llm_service.generate_resume_content(role, selections, custom)
    resume.data = content
    resume.status = "draft"
    db.commit()

    return {
        "code": 0,
        "data": {
            "reply": "简历已生成！请前往编辑页面查看和完善。",
            "content": content,
            "status": "draft",
            "module": None,
        }
    }


@router.post("/resumes/{resume_id}/generate")
async def generate_resume(resume_id: int, db: Session = Depends(get_db)):
    """触发完整生成 + 审查"""
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    selections = resume.selections or {}
    custom = resume.data or {}
    content = await llm_service.generate_resume_content(resume.role, selections, custom)
    resume.data = content
    resume.status = "draft"
    db.commit()

    return {"code": 0, "data": {"content": content, "status": "draft"}}


@router.post("/resumes/{resume_id}/jd-optimize")
async def optimize_by_jd(resume_id: int, req: dict, db: Session = Depends(get_db)):
    """JD 靶向优化"""
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    jd_text = req.get("jd", "")
    if not jd_text:
        return {"code": 1, "message": "请提供 JD 文本"}

    jd_info = await llm_service.analyze_jd(jd_text)
    return {"code": 0, "data": {"keywords": jd_info.get("keywords", []), "suggestions": jd_info.get("suggestions", [])}}
