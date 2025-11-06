from typing import Optional

from pydantic import Field

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("github_tool")


@mcp.tool(description="查询 GitHub Issue/PR/文件等信息（需公开接口；支持简单 query 直传）")
async def query(
    query: str = Field(description="原始查询文本，包含 repo/issue 等信息"),
    repo: Optional[str] = Field(default=None, description="仓库全名，如 'owner/repo'"),
    issue_number: Optional[int] = Field(default=None, description="Issue/PR 编号"),
    token: Optional[str] = Field(default=None, description="GitHub Token，可选，加速与放宽速率限制"),
):
    """最小可用 GitHub 查询：
    - 若提供 repo+issue_number：请求 issue 或 PR；
    - 否则将 query 发给 GitHub 搜索 API（简单兜底）。
    返回 JSON 字符串。
    """
    import httpx  # type: ignore

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        try:
            if repo and issue_number is not None:
                url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json()

            # 兜底：代码搜索/issue 搜索（公共速率有限）
            search_url = "https://api.github.com/search/issues"
            resp = await client.get(search_url, params={"q": query}, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()


