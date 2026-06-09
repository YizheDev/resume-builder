"""LLM 调用统一封装"""

from server.config import settings


class LLMService:
    """DeepSeek LLM 调用服务"""

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        """发送对话请求，返回 AI 回复"""
        # TODO: 实现 OpenAI 兼容 API 调用
        pass

    async def analyze_career(self, background: str) -> list[dict]:
        """分析用户背景，返回推荐岗位列表"""
        pass

    async def generate_options(self, module: str, role: str, collected: dict) -> list[dict]:
        """为指定模块生成可选的高质量内容选项"""
        pass

    async def polish_content(self, raw_text: str, role: str) -> str:
        """将用户原始描述润色为专业简历措辞"""
        pass
