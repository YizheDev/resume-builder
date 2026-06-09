"""DeepSeek LLM 服务 — 岗位分析 / 选项生成 / 内容润色 / 简历生成"""

import json
import logging
import httpx

from server.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """DeepSeek API (OpenAI 兼容) 调用封装"""

    def __init__(self):
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.api_key = settings.DEEPSEEK_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _chat(self, system: str, user: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """发送聊天请求"""
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    # ─── 岗位分析 ─────────────────────────────────

    async def analyze_career(self, background: str) -> list[dict]:
        """分析用户背景，返回推荐岗位列表"""
        system = """你是资深职业规划师。根据用户背景推荐 6 个最适合的岗位。
输出 JSON 数组，每个元素包含 role(岗位名)、score(匹配度0-100)、reason(一句话推荐理由)、skills(该岗位所需技能列表)。
只输出 JSON，不要其他文字。"""
        user = f"用户背景：{background}"
        result = await self._chat(system, user, temperature=0.8)
        return self._parse_json(result, [])

    # ─── 选项生成（各模块） ─────────────────────────

    async def generate_module_options(self, module: str, role: str, collected: dict) -> list[dict]:
        """为指定模块生成可供用户勾选的高质量内容选项"""
        prompts = {
            "education_courses": f"为{role}岗位列出10门最相关的大学课程，输出 JSON 数组 [{{'id':'','label':''}}]",
            "awards": f"为{role}岗位的在校生/应届生列出8项可能获得的荣誉奖项，输出 JSON 数组 [{{'id':'','label':''}}]",
            "experience": f"列出{role}岗位实习生/初级工程师最常做的工作内容，输出 JSON 数组 [{{'id':'','label':''}}]，共12项",
            "projects": f"列出{role}岗位常见的项目类型，输出 JSON 数组 [{{'id':'','label':''}}]，共8项",
            "skills_must": f"列出{role}岗位的必备技能，输出 JSON 数组 [{{'id':'','label':''}}]，共6项",
            "skills_plus": f"列出{role}岗位的加分技能，输出 JSON 数组 [{{'id':'','label':''}}]，共6项",
            "skills_optional": f"列出{role}岗位的了解即可技能，输出 JSON 数组 [{{'id':'','label':''}}]，共4项",
        }
        prompt = prompts.get(module, f"为{role}岗位列出{module}相关的8项内容，输出 JSON 数组 [{{'id':'','label':''}}]")
        result = await self._chat("输出 JSON 数组，不要其他文字。", prompt, temperature=0.9)
        return self._parse_json(result, [])

    async def smart_recommend(self, module: str, role: str, selected: list[str]) -> list[str]:
        """根据用户已选内容，推荐关联选项"""
        result = await self._chat(
            "输出 JSON 字符串数组，只输出 JSON。",
            f"用户在为{role}岗位选择{module}，已选：{selected}。推荐3个关联选项（已选的不重复）。",
            temperature=0.7, max_tokens=200,
        )
        return self._parse_json(result, [])

    # ─── 内容生成 ─────────────────────────────────

    async def generate_resume_content(self, role: str, selections: dict, custom_inputs: dict) -> dict:
        """根据用户选择生成完整简历 JSON"""
        system = """你是顶级简历撰写专家。根据用户的勾选和补充，生成一份完整的一页A4简历。
输出 JSON 格式：{personal:{name,phone,email,city}, education:[{school,major,degree,start,end,courses}],
awards:[{name,level,date,description}], experience:[{company,title,start,end,highlights:[3条]}],
projects:[{name,role,techStack,highlights:[3条]}], skills:[{name,level}], summary:""}
highlight 必须用 STAR 法则，每条15-30字中文。summary 100-150字。
只输出 JSON，不要其他文字。"""
        user = f"岗位：{role}\n用户选择：{json.dumps(selections, ensure_ascii=False)}\n补充内容：{json.dumps(custom_inputs, ensure_ascii=False)}"
        result = await self._chat(system, user, temperature=0.8, max_tokens=8000)
        return self._parse_json(result, {})

    async def polish_description(self, text: str, role: str) -> str:
        """将用户原始描述润色为专业简历措辞"""
        result = await self._chat(
            "用 STAR 法则和量化数据优化以下描述，每条30-50字。直接输出润色后的文字，不要引号。",
            f"岗位：{role}\n原始描述：{text}",
            temperature=0.7, max_tokens=500,
        )
        return result.strip()

    async def generate_self_evaluation(self, role: str, data: dict, style: str = "technical") -> str:
        """生成自我评价（3 种风格）"""
        prompts = {
            "technical": f"为{role}岗位写一段技术深度的自我评价（80-120字），强调技术能力和项目经验",
            "balanced": f"为{role}岗位写一段全面发展的自我评价（80-120字），综合技术+软技能+成长潜力",
            "growth": f"为{role}岗位写一段成长潜力的自我评价（80-120字），适合应届生，强调学习能力和热情",
        }
        result = await self._chat("直接输出自我评价，不要引号不要前缀。", prompts.get(style, prompts["balanced"]))
        return result.strip()

    async def analyze_jd(self, jd_text: str) -> dict:
        """分析 JD，提取关键词和优化建议"""
        system = """分析职位描述，输出 JSON：{keywords:[{word,weight}], suggestions:[{ target字段, action:add/emphasize, detail}]}"""
        result = await self._chat(system, f"JD内容：{jd_text}", temperature=0.5)
        return self._parse_json(result, {})

    async def translate_to_english(self, data: dict) -> dict:
        """中译英简历"""
        result = await self._chat(
            "将以下中文简历翻译成地道英文。保持 JSON 结构不变。只输出 JSON。",
            json.dumps(data, ensure_ascii=False),
            temperature=0.3, max_tokens=4000,
        )
        return self._parse_json(result, data)

    async def generate_from_scratch(self, background: str, role: str) -> dict:
        """零经验用户：从课程/社团/竞赛中挖掘素材生成完整简历"""
        system = """用户没有任何实习经验。你需要从课程设计、社团活动、竞赛经历中挖掘素材，
生成一份完整的一页A4简历 JSON。每个经历至少3条 STAR 法则描述。skills 至少8项。summary 100-150字。
只输出 JSON。"""
        result = await self._chat(system, f"背景：{background}\n目标岗位：{role}", temperature=0.9, max_tokens=8000)
        return self._parse_json(result, {})

    # ─── 工具方法 ─────────────────────────────────

    def _parse_json(self, text: str, default):
        """安全解析 JSON"""
        import logging
        log = logging.getLogger(__name__)
        try:
            text = text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            result = json.loads(text)
            if isinstance(result, list):
                log.info(f"Parsed JSON array with {len(result)} items")
            return result
        except (json.JSONDecodeError, IndexError) as e:
            log.warning(f"JSON parse failed: {e}, raw text: {text[:200]}")
            return default


llm_service = LLMService()
