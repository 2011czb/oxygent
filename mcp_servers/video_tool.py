import base64
import os
import subprocess
from typing import Optional

from pydantic import Field

from mcp.server.fastmcp import FastMCP


mcp = FastMCP("video_tool")


@mcp.tool(description="使用 ffmpeg 抽取视频某时间点的帧（返回base64图片）。若无ffmpeg则返回错误信息。")
async def extract_frame(
    video_path: str = Field(description="视频文件绝对路径或相对路径"),
    timestamp: float = Field(default=0.0, description="抽帧秒数，如0.0为首帧"),
    width: Optional[int] = Field(default=None, description="可选，缩放宽度"),
) -> dict:
    try:
        # 绝对路径
        abs_path = os.path.abspath(video_path)
        if not os.path.exists(abs_path):
            return {"type": "error", "data": f"video not found: {abs_path}"}

        # 检测ffmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            return {"type": "error", "data": "ffmpeg not installed or not in PATH"}

        # 生成临时输出路径
        out_path = abs_path + f".frame_{timestamp}.jpg"
        vf = []
        if width and width > 0:
            vf = ["-vf", f"scale={width}:-1"]

        cmd = [
            "ffmpeg",
            "-ss",
            str(timestamp),
            "-i",
            abs_path,
            *vf,
            "-frames:v",
            "1",
            "-y",
            out_path,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 0 or not os.path.exists(out_path):
            return {"type": "error", "data": f"ffmpeg failed: {proc.stderr.decode(errors='ignore')[:400]}"}

        with open(out_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        # 可选：清理输出文件
        try:
            os.remove(out_path)
        except Exception:
            pass
        return {"type": "image", "data": b64}
    except Exception as e:  # noqa: BLE001
        return {"type": "error", "data": str(e)}


if __name__ == "__main__":
    mcp.run()


