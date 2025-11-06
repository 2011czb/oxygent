import base64
from typing import Optional

from pydantic import Field

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("browser_tool")


@mcp.tool(description="访问URL并返回页面HTML或截图（若无 Playwright 则回退为 HTTP 抓取）")
async def fetch_page(
    url: str = Field(description="目标URL"),
    wait_for: str = Field(default="", description="等待的CSS选择器（需要 Playwright）"),
    screenshot: bool = Field(default=False, description="是否返回截图（base64）"),
    timeout_ms: int = Field(default=10000, description="等待选择器超时时间，毫秒"),
):
    """最小可用浏览抓取：
    - 优先使用 Playwright（若已安装），支持选择器等待与截图；
    - 否则回退到 httpx 获取静态 HTML。
    返回：{"type": "html"|"image", "data": str}
    """
    # 优先 Playwright
    try:
        from playwright.async_api import async_playwright  # type: ignore

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout_ms)
            if screenshot:
                img_bytes = await page.screenshot(full_page=True)
                await browser.close()
                return {
                    "type": "image",
                    "data": base64.b64encode(img_bytes).decode("utf-8"),
                }
            html = await page.content()
            await browser.close()
            return {"type": "html", "data": html}
    except Exception:
        # 回退 httpx 抓取
        try:
            import httpx  # type: ignore

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            }
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return {"type": "html", "data": resp.text}
        except Exception as e:  # noqa: BLE001
            return {"type": "error", "data": f"fetch failed: {e}"}


if __name__ == "__main__":
    mcp.run()


