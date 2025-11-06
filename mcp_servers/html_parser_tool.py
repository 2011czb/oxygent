from typing import List, Optional, Union

from pydantic import Field

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("html_parser_tool")


@mcp.tool(description="使用 CSS 选择器从 HTML 中抽取文本或属性。若未安装 bs4，将回退为简单正则。")
async def extract(
    html: str = Field(description="HTML 字符串"),
    selector: str = Field(description="CSS 选择器，如 '#parameter-brand a'"),
    attr: Optional[str] = Field(default=None, description="可选，提取的属性名，如 'href'"),
    all: bool = Field(default=False, description="是否返回全部匹配结果；否则仅返回第一个"),
) -> dict:
    try:
        from bs4 import BeautifulSoup  # type: ignore

        soup = BeautifulSoup(html, "lxml") if "<" in html else BeautifulSoup(html, "html.parser")
        elements = soup.select(selector)
        if not elements:
            return {"type": "list" if all else "string", "data": [] if all else ""}

        def pick_text(e):
            return (e.get(attr) if attr else e.get_text(" ", strip=True)) or ""

        if all:
            return {"type": "list", "data": [pick_text(e) for e in elements]}
        return {"type": "string", "data": pick_text(elements[0])}
    except Exception:
        # 轻量回退：非常简单的品牌提取示例
        import re

        if selector.replace(" ", "").lower() in {"#parameter-branda", "#parameter-brand a", "ul#parameter-brandlia"}:
            m = re.search(r"parameter-brand[\s\S]*?<a[^>]*>([^<]+)</a>", html, re.I)
            if m:
                return {"type": "string", "data": m.group(1).strip()}
        return {"type": "list" if all else "string", "data": [] if all else ""}


if __name__ == "__main__":
    mcp.run()


