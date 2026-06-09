"""简历导出 API — 使用 resumake-mcp 生成专业 LaTeX PDF"""

import json
import subprocess
import tempfile
import os
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, HTMLResponse
from sqlalchemy.orm import Session

from server.database import get_db
from server.models.resume import Resume
from server.services.llm_service import llm_service

router = APIRouter()

# MCP 配置
RESUMAKE_MCP_ENABLED = os.getenv("RESUMAKE_MCP_ENABLED", "true").lower() == "true"


@router.get("/resumes/{resume_id}/export")
async def export_resume(
    resume_id: int,
    format: str = Query("pdf"),
    lang: str = Query("cn"),
    template: str = Query("professional"),
    db: Session = Depends(get_db),
):
    """导出简历。优先 resumake-mcp (LaTeX)，fallback HTML"""
    resume = db.query(Resume).get(resume_id)
    if not resume:
        return {"code": 1, "message": "未找到"}

    data = resume.data or {}
    if not data:
        return {"code": 1, "message": "请先生成简历内容"}

    # 中译英
    if lang == "en":
        data = await llm_service.translate_to_english(data)

    # 尝试 resumake-mcp
    if RESUMAKE_MCP_ENABLED:
        try:
            pdf_bytes = await generate_with_resumake(data, template)
            if pdf_bytes and len(pdf_bytes) > 100:
                filename = f"resume_{resume_id}.pdf"
                return Response(content=pdf_bytes, media_type="application/pdf",
                               headers={"Content-Disposition": f'attachment; filename="{filename}"'})
        except Exception as e:
            pass  # fallback to HTML

    # Fallback: 渲染 HTML（浏览器端打印为 PDF）
    html = render_professional_html(data, resume.role)
    if format == "html":
        return HTMLResponse(content=html)
    return HTMLResponse(content=html)


async def generate_with_resumake(data: dict, template: str) -> bytes | None:
    """通过 resumake-mcp 生成 LaTeX PDF"""
    try:
        import httpx
        payload = {
            "data": data,
            "template": template,
            "format": "pdf",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            # resumake-mcp 默认端口 3000
            resp = await client.post("http://localhost:3000/generate", json=payload)
            if resp.status_code == 200:
                return resp.content
    except Exception:
        pass

    # 尝试 npx 方式
    try:
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f, ensure_ascii=False)
            json_path = f.name
        result = subprocess.run(
            ["npx", "-y", "resumake-mcp", "generate", "--input", json_path, "--template", template, "--format", "pdf"],
            capture_output=True, timeout=30,
        )
        os.unlink(json_path)
        if result.returncode == 0 and len(result.stdout) > 100:
            return result.stdout
    except Exception:
        pass
    return None


def render_professional_html(data: dict, role: str) -> str:
    """渲染专业 HTML 简历"""
    p = data.get("personal", {})
    edu = data.get("education", [])
    exp = data.get("experience", [])
    proj = data.get("projects", [])
    skills = data.get("skills", [])
    awards = data.get("awards", [])
    summary = data.get("summary", "")

    name = p.get("name", "")
    contact = " · ".join(filter(bool, [p.get("phone"), p.get("email"), p.get("city")]))

    def render_section(title, items_html):
        if not items_html:
            return ""
        return f'<div class="section"><h2>{title}</h2>{items_html}</div>'

    edu_items = "".join(
        f'<div class="item"><span class="bold">{e.get("school","")}</span> — {e.get("major","")} · {e.get("degree","")}'
        f'<span class="muted"> {e.get("start","")} - {e.get("end","")}</span>'
        f'<p class="sub">{e.get("courses","")}</p></div>'
        for e in edu) if edu else ""

    exp_items = "".join(
        f'<div class="item"><div class="flex-between"><span class="bold">{e.get("title","")}</span><span class="muted">{e.get("start","")} - {e.get("end","")}</span></div>'
        f'<p class="sub">{e.get("company","")}</p>'
        f'<ul>{"".join(f"<li>{h}</li>" for h in (e.get("highlights") or []))}</ul></div>'
        for e in exp) if exp else ""

    proj_items = "".join(
        f'<div class="item"><span class="bold">{p.get("name","")}</span>'
        f'<span class="muted"> · {p.get("techStack","")} · {p.get("role","")}</span>'
        f'<ul>{"".join(f"<li>{h}</li>" for h in (p.get("highlights") or []))}</ul></div>'
        for p in proj) if proj else ""

    skills_html = "".join(
        f'<span class="skill-tag">{s.get("name","")}</span>'
        for s in skills) if skills else ""

    awards_items = "".join(
        f'<div class="item"><span class="bold">{a.get("name","")}</span><span class="muted"> · {a.get("level","")} · {a.get("date","")}</span></div>'
        for a in awards) if awards else ""

    return f"""<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8"><title>{name} - 简历</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'PingFang SC','Microsoft YaHei','Helvetica Neue',sans-serif;font-size:13px;color:#222;line-height:1.6;background:#e8ecf1}}
.page{{width:210mm;min-height:297mm;margin:20px auto;padding:22mm 20mm;background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.12)}}
h1{{font-size:26px;letter-spacing:2px;margin-bottom:2px;color:#1a1a2e}}
.contact-bar{{font-size:12px;color:#555;margin-bottom:14px;padding-bottom:12px;border-bottom:2px solid #2563eb}}
.role-tag{{display:inline-block;background:#2563eb;color:#fff;padding:2px 12px;border-radius:3px;font-size:12px;margin-bottom:14px}}
h2{{font-size:15px;color:#1a1a2e;border-bottom:1.5px solid #2563eb;padding-bottom:3px;margin:16px 0 8px;text-transform:uppercase;letter-spacing:1px}}
.section{{margin-bottom:4px}}
.item{{margin-bottom:10px}}
.bold{{font-weight:600}}
.muted{{color:#777;font-size:12px}}
.sub{{color:#555;font-size:12px;margin-top:2px}}
.flex-between{{display:flex;justify-content:space-between}}
ul{{margin:3px 0 0 16px;font-size:12px;color:#444}}
li{{margin-bottom:2px}}
.skill-tag{{display:inline-block;background:#eef2ff;color:#2563eb;padding:2px 10px;margin:2px;border-radius:4px;font-size:11px}}
</style></head><body><div class="page">
<div class="flex-between" style="align-items:start">
<div><h1>{name}</h1><p class="contact-bar">{contact}</p></div>
<div class="role-tag">{role}</div>
</div>
{render_section("个人总结", f'<p class="sub">{summary}</p>') if summary else ""}
{render_section("工作经历", exp_items)}
{render_section("项目经历", proj_items)}
{render_section("教育背景", edu_items)}
{render_section("荣誉奖项", awards_items)}
{render_section("专业技能", f'<div>{skills_html}</div>')}
</div></body></html>"""
