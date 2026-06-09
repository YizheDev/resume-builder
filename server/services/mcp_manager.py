"""MCP 连接管理器 — 统一管理所有 MCP 服务器的连接和调用"""

import asyncio
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPManager:
    """管理 CV Forge / Lightcast / ATS-Checker 等 MCP 连接"""

    def __init__(self):
        self._sessions: dict[str, ClientSession] = {}

    async def get_session(self, name: str) -> Optional[ClientSession]:
        """获取或创建 MCP 会话"""
        if name in self._sessions:
            return self._sessions[name]

        configs = {
            "cv-forge": {
                "command": "npx",
                "args": ["-y", "@anthropic/cv-forge-mcp-server"],
            },
            "lightcast": {
                "command": "python",
                "args": ["-m", "lightcast_mcp"],
            },
            "ats-checker": {
                "command": "python",
                "args": ["-m", "ats_checker_mcp"],
            },
        }

        if name not in configs:
            return None

        cfg = configs[name]
        params = StdioServerParameters(command=cfg["command"], args=cfg["args"])
        transport = await stdio_client(params).__aenter__()
        read, write = transport
        session = await ClientSession(read, write).__aenter__()
        await session.initialize()
        self._sessions[name] = session
        return session

    async def close_all(self):
        for name, session in self._sessions.items():
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass
        self._sessions.clear()


# 全局单例
mcp_manager = MCPManager()
