import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime


ERROR_PATTERNS = [
    re.compile(r"\bERROR\b", re.IGNORECASE),
    re.compile(r"\bWARNING\b", re.IGNORECASE),
    re.compile(r"\bException\b"),
    re.compile(r"\bTraceback \(most recent call last\):"),
    re.compile(r"\bhttpx\.ConnectError\b"),
    re.compile(r"\bhttpcore\.ConnectError\b"),
    re.compile(r"\bNo module named\b"),
    re.compile(r"\bFileNotFoundError\b"),
    re.compile(r"\bModuleNotFoundError\b"),
]


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


async def _read_stream(stream: asyncio.StreamReader, stream_name: str, queue: asyncio.Queue):
    buffer: list[str] = []
    in_traceback = False

    while True:
        line = await stream.readline()
        if not line:
            # flush remaining buffered traceback
            if buffer:
                await queue.put({
                    "time": now_iso(),
                    "level": "ERROR" if in_traceback else stream_name.upper(),
                    "kind": "traceback" if in_traceback else "line",
                    "message": "\n".join(buffer),
                })
            break

        text = line.decode(errors="replace").rstrip("\n")
        print(text)  # mirror to our own stdout

        if re.search(r"^Traceback \(most recent call last\):", text):
            # start grouping traceback
            if buffer:
                await queue.put({
                    "time": now_iso(),
                    "level": stream_name.upper(),
                    "kind": "line",
                    "message": "\n".join(buffer),
                })
                buffer = []
            in_traceback = True
            buffer.append(text)
            continue

        if in_traceback:
            buffer.append(text)
            # traceback usually ends with the exception line; heuristic: blank line ends a block
            if text.strip() == "":
                await queue.put({
                    "time": now_iso(),
                    "level": "ERROR",
                    "kind": "traceback",
                    "message": "\n".join(buffer),
                })
                buffer = []
                in_traceback = False
            continue

        matched = any(p.search(text) for p in ERROR_PATTERNS)
        if matched:
            await queue.put({
                "time": now_iso(),
                "level": "ERROR" if "error" in text.lower() else stream_name.upper(),
                "kind": "line",
                "message": text,
            })


async def run_and_collect(cmd: list[str], out_path: str, summary_path: str | None) -> int:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    queue: asyncio.Queue = asyncio.Queue()

    async def writer():
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "a", encoding="utf-8") as f:
            while True:
                item = await queue.get()
                if item is None:  # sentinel
                    break
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    writer_task = asyncio.create_task(writer())

    readers = [
        asyncio.create_task(_read_stream(proc.stdout, "stdout", queue)),
        asyncio.create_task(_read_stream(proc.stderr, "stderr", queue)),
    ]

    return_code = await proc.wait()
    for r in readers:
        try:
            await r
        except Exception:
            pass
    await queue.put(None)
    await writer_task

    # optional summary
    if summary_path:
        counts = {"ERROR": 0, "WARNING": 0}
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        lvl = str(obj.get("level", "")).upper()
                        if lvl in counts:
                            counts[lvl] += 1
                    except Exception:
                        continue
            with open(summary_path, "w", encoding="utf-8") as sf:
                sf.write(json.dumps({"time": now_iso(), "counts": counts}, ensure_ascii=False, indent=2))
        except Exception:
            pass

    return return_code


def main():
    parser = argparse.ArgumentParser(description="Run a command and collect error/exception lines from its output into JSONL.")
    parser.add_argument("--out", default=".logs/errors.jsonl", help="Path to write JSONL error lines")
    parser.add_argument("--summary", default=".logs/error_summary.json", help="Optional summary JSON path (counts)")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command to run (prefix with --)")
    args = parser.parse_args()

    cmd = [c for c in args.cmd if c != "--"]
    if not cmd:
        print("Usage: python tools/capture_errors.py -- <your command>", file=sys.stderr)
        sys.exit(2)

    return_code = asyncio.run(run_and_collect(cmd, args.out, args.summary))
    sys.exit(return_code)


if __name__ == "__main__":
    main()


