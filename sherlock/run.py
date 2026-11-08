#!/usr/bin/env python3
"""Small launcher for unmodified Sherlock, with readable local HTML reports."""
from __future__ import annotations

import argparse
import csv
import html
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent
VERSION = "0.16.2"
LABELS = {
    "Claimed": "发现同名账号 · 待人工核实",
    "Available": "未检测到 · 不代表一定可注册",
    "Unknown": "查询失败 · 无法判断",
    "WAF": "被网站拦截 · 无法判断",
    "Illegal": "此网站不接受该用户名格式",
}


def checked_username(value: str) -> str:
    # Keep input as data and prevent the original CLI's filename/option semantics.
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise argparse.ArgumentTypeError("用户名须以字母或数字开头，最多 64 位，可含 _ . -。")
    return value


def render_report(rows: list[dict], metadata: dict, directory: Path) -> None:
    esc = html.escape
    count = Counter(row.get("exists", "Unknown") for row in rows)
    blocks = []
    for row in rows:
        status = row.get("exists", "Unknown")
        url = row.get("url_user", "")
        valid_link = urlsplit(url).scheme in ("https", "http") and bool(urlsplit(url).hostname)
        link = (f'<a href="{esc(url, quote=True)}" target="_blank" rel="noopener noreferrer">打开公开主页 ↗</a>'
                if valid_link and status == "Claimed" else "")
        kind = "found" if status == "Claimed" else "neutral" if status == "Available" else "error"
        blocks.append(
            f'<article class="card {kind}"><span class="badge">{esc(LABELS.get(status, status))}</span>'
            f'<h2>{esc(row.get("name", ""))}</h2><p class="username">@{esc(row.get("username", ""))}</p>'
            f'<p class="detail">HTTP {esc(row.get("http_status", ""))} · {esc(status)}</p>{link}</article>'
        )
    uncertainty = sum(v for k, v in count.items() if k not in ("Claimed", "Available"))
    state = "已完成" if metadata["exit_code"] == 0 and rows else "未完成，请查看 run.log"
    body = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Sherlock 查询结果</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f5f6;color:#182a2b;font:16px/1.65 system-ui,-apple-system,sans-serif}}
main{{max-width:1080px;margin:0 auto;padding:40px 20px}}.eyebrow{{letter-spacing:.12em;color:#587174;font-size:12px}}
h1{{font-size:36px;line-height:1.25;margin:8px 0 16px}}h2{{font-size:21px;margin:14px 0 2px}}
.summary{{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0}}.metric{{background:white;padding:16px 24px;border-radius:14px;flex:1;min-width:140px}}
.metric strong{{display:block;font-size:30px;color:#096a55}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(245px,1fr));gap:14px}}
.card{{border-radius:16px;background:white;border:1px solid #dce3e3;padding:22px;overflow-wrap:anywhere}}
.card.found{{border-top:4px solid #13806c}}.card.error{{border-top:4px solid #ae7b28}}.badge{{font-size:12px;color:#536c6e}}
.username{{margin:0}}.detail{{color:#6c7d7e;font-size:12px}}a{{color:#076953;font-weight:600}}.note{{max-width:780px;color:#50696b}}footer{{margin-top:30px;color:#637779;font-size:12px}}
</style></head><body><main><div class="eyebrow">SHERLOCK / USERNAME LOOKUP</div>
<h1>用户名公开足迹</h1><p class="note">同名只是一条线索，不能证明账号属于同一个人。被拦截、超时和未检测到都不等于不存在。</p>
<p>{esc('、'.join(metadata['usernames']))} · {esc(state)}</p>
<div class="summary"><div class="metric"><strong>{len(rows)}</strong>返回结果</div><div class="metric"><strong>{count['Claimed']}</strong>发现同名账号</div><div class="metric"><strong>{count['Available']}</strong>未检测到</div><div class="metric"><strong>{uncertainty}</strong>无法判断 / 格式不适用</div></div>
<section class="grid">{''.join(blocks) or '<p>没有可用结果，请查看同目录 run.log。</p>'}</section>
<footer>原版 Sherlock {VERSION} · 开始时间 {esc(metadata['started_at_utc'])} UTC<br>同目录含原始 CSV / TXT、运行日志和本次参数。</footer>
</main></body></html>'''
    (directory / "report.html").write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="运行原版 Sherlock 并生成中文卡片报告。")
    parser.add_argument("usernames", type=checked_username, nargs="*")
    parser.add_argument("--site", action="append", help="只查指定网站，可重复，如 --site GitHub")
    parser.add_argument("--timeout", type=int, default=15, choices=range(5, 61), metavar="5-60")
    parser.add_argument("--frozen-sites", action="store_true", help="使用发行版内置规则；跳过上游最新排除表，仅用于复现或测试")
    args = parser.parse_args()
    if not args.usernames:
        try:
            args.usernames = [checked_username(input("输入要查询的用户名：").strip())]
        except (argparse.ArgumentTypeError, EOFError) as exc:
            parser.error(str(exc))
    if len(args.usernames) > 5:
        parser.error("每次最多 5 个用户名。")
    if args.site and any(not s.strip() or len(s) > 100 for s in args.site):
        parser.error("网站名不能为空或超过 100 个字符。")
    try:
        installed = importlib.metadata.version("sherlock-project")
    except importlib.metadata.PackageNotFoundError:
        parser.error("尚未安装 Sherlock，请先运行 setup.py。")
    if installed != VERSION:
        parser.error(f"需要 Sherlock {VERSION}，当前是 {installed}；请重新运行 setup.py。")

    now = datetime.now(timezone.utc)
    directory = BASE / "results" / f"{now:%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:6]}"
    directory.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, "-m", "sherlock_project", *args.usernames,
               "--no-color", "--csv", "--txt", "--print-all", "--folderoutput", str(directory),
               "--timeout", str(args.timeout)]
    for site in args.site or []:
        command.extend(["--site", site])
    if args.frozen_sites:
        command.append("--local")
    metadata = {"sherlock_version": VERSION, "started_at_utc": now.isoformat(),
                "usernames": args.usernames, "sites": args.site or "default catalogue",
                "per_site_timeout_seconds": args.timeout, "frozen_sites": args.frozen_sites}
    print("Sherlock 正在查询，结果将保存到：", directory, flush=True)
    try:
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=600,
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        code = result.returncode
        log = result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        code = 124
        chunks = [exc.stdout or b"", exc.stderr or b""]
        log = "\n".join(c.decode("utf-8", "replace") if isinstance(c, bytes) else c for c in chunks)
        log += "\n查询超过 10 分钟，已终止；本次结果可能不完整。\n"
    metadata["exit_code"] = code
    (directory / "run.log").write_text(log, encoding="utf-8")
    rows = []
    for path in sorted(directory.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as source:
            rows.extend(csv.DictReader(source))
    metadata["result_count"] = len(rows)
    (directory / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    render_report(rows, metadata, directory)
    print("结果状态：", dict(Counter(row.get("exists", "Unknown") for row in rows)))
    print("打开查看：", directory / "report.html")
    if code != 0 or not rows:
        print("本次未正常完成，请查看同目录 run.log。", file=sys.stderr)
        return code or 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
