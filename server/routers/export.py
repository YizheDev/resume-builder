"""简历导出 API"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume
from server.services.llm_service import llm_service

router = APIRouter()


@router.get("/resumes/{resume_id}/export")
async def export_resume(
    resume_id: int,
    format: str = Query("html", pattern="^(html|pdf)$"),
    lang: str = Query("cn"),
    db: Session = Depends(get_db),
):
    """导出简历（HTML 或 PDF）"""
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    data = resume.data or {}

    # 中译英
    if lang == "en":
        data = await llm_service.translate_to_english(data)

    # 渲染 HTML
    html = render_resume_html(data, resume.role, resume.template or "classic")

    if format == "html":
        return HTMLResponse(content=html)

    # PDF 由前端 html2pdf 生成，这里返回 HTML
    return HTMLResponse(content=html)


def render_resume_html(data: dict, role: str, template: str) -> str:
    """渲染简历 HTML"""
    p = data.get("personal", {})
    edu = data.get("education", [])
    exp = data.get("experience", [])
    proj = data.get("projects", [])
    skills = data.get("skills", [])
    awards = data.get("awards", [])
    summary = data.get("summary", "")

    edu_html = "".join(
        f'<div style="margin-bottom:8px"><strong>{e.get("school","")}</strong> — {e.get("major","")} · {e.get("degree","")}<br>'
        f'<span style="color:#666;font-size:13px">{e.get("start","")} - {e.get("end","")} · {e.get("courses","")}</span></div>'
        for e in edu
    )

    exp_html = "".join(
        f'<div style="margin-bottom:10px"><strong>{e.get("company","")}</strong> — {e.get("title","")}<br>'
        f'<span style="color:#666;font-size:13px">{e.get("start","")} - {e.get("end","")}</span>'
        f'<ul style="margin:4px 0 0 16px;font-size:13px">{"".join(f"<li>{h}</li>" for h in e.get("highlights",[]))}</ul></div>'
        for e in exp
    )

    proj_html = "".join(
        f'<div style="margin-bottom:10px"><strong>{p.get("name","")}</strong> — {p.get("role","")} · <span style="color:#666;font-size:13px">{p.get("techStack","")}</span>'
        f'<ul style="margin:4px 0 0 16px;font-size:13px">{"".join(f"<li>{h}</li>" for h in p.get("highlights",[]))}</ul></div>'
        for p in proj
    )

    skills_html = "".join(
        f'<span style="display:inline-block;background:#f0f0f0;padding:2px 8px;margin:2px;border-radius:4px;font-size:12px">{s.get("name","")} <span style="color:#999">{s.get("level","")}</span></span>'
        for s in skills
    )

    awards_html = "".join(
        f'<div style="margin-bottom:4px;font-size:13px">🏅 {a.get("name","")} — {a.get("level","")} · {a.get("date","")}</div>'
        for a in awards
    )

    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<style>body{{font-family:'Microsoft YaHei','PingFang SC',sans-serif;font-size:14px;color:#333;line-height:1.6;margin:0;padding:0}}
.a4{{width:210mm;min-height:297mm;margin:0 auto;padding:20mm;background:#fff;box-sizing:border-box}}
h1{{font-size:24px;margin:0 0 4px}}h2{{font-size:16px;color:#1a1a2e;border-bottom:1px solid #ddd;padding-bottom:4px;margin:16px 0 8px}}
.contact{{font-size:12px;color:#666;margin-bottom:12px}}</style></head><body><div class="a4">
<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:16px">
<div><h1>{p.get("name","")}</h1><p class="contact">{p.get("phone","")} · {p.get("email","")} · {p.get("city","")}</p>
<p style="font-size:13px;color:#444">求职意向：{role}</p></div>
</div>
{f'<h2>📝 自我评价</h2><p style="font-size:13px">{summary}</p>' if summary else ""}
<h2>💼 工作经历</h2>{exp_html or '<p style="color:#999;font-size:13px">无</p>'}
<h2>📦 项目经历</h2>{proj_html or '<p style="color:#999;font-size:13px">无</p>'}
<h2>🎓 教育背景</h2>{edu_html or '<p style="color:#999;font-size:13px">无</p>'}
{f'<h2>🏆 奖项荣誉</h2>{awards_html}' if awards else ""}
<h2>🛠️ 技能</h2><div>{skills_html}</div>
</div></body></html>"""
