#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一入口脚本：依次运行两个爬虫，汇总结果并调用微信通知。
"""

import sys
import subprocess
import json
import os
from datetime import datetime

SCRIPTS = [
    ("信息披露文件", "download_bonds_disclosure.py"),
    ("项目情况汇总表", "download_bonds_summary.py"),
]


def send_wechat_notification(summary: dict):
    """
    通过 PushPlus 推送消息到个人微信。
    需设置环境变量 PUSHPLUS_TOKEN。
    """
    import requests as req

    token = os.environ.get("PUSHPLUS_TOKEN", "")
    if not token:
        print("⚠️ 未设置 PUSHPLUS_TOKEN 环境变量，跳过微信通知", flush=True)
        return

    # 构建消息内容（纯文本，PushPlus 支持 Markdown）
    msg_lines = [
        f"## 📊 债券爬虫日报 {summary['date']}",
        f"",
        f"**执行状态：{'✅ 全部成功' if summary['success'] else '⚠️ 部分失败'}**",
        f"",
        f"---",
        f"",
    ]
    for s in summary["results"]:
        emoji = "✅" if s["success"] else "❌"
        msg_lines.append(f"{emoji} **{s['name']}**：{s['message']}")
    msg_lines.append("")
    msg_lines.append("---")
    msg_lines.append("[查看 Actions 详情](https://github.com/Tamato-112/shandong-bond-scraper/actions)")

    content = "\n".join(msg_lines)

    payload = {
        "token": token,
        "title": f"债券爬虫日报 {summary['date']}",
        "content": content,
        "template": "markdown",
    }

    try:
        print("📤 正在推送 PushPlus 通知...", flush=True)
        resp = req.post("https://www.pushplus.plus/send", json=payload, timeout=10)
        result = resp.json()
        if result.get("code") == 200:
            print("✅ PushPlus 通知发送成功", flush=True)
        else:
            print(f"⚠️ PushPlus 返回异常: {result}", flush=True)
    except Exception as e:
        print(f"❌ PushPlus 发送失败: {e}", flush=True)


def run_script(name, script_path):
    print(f"\n{'=' * 50}", flush=True)
    print(f"▶ 开始执行：{name}", flush=True)
    print(f"{'=' * 50}", flush=True)

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=False,
    )

    success = result.returncode == 0
    message = "执行完成" if success else f"退出码 {result.returncode}"

    return {"name": name, "success": success, "message": message}


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    summary = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "success": True,
        "results": [],
    }

    for name, script in SCRIPTS:
        script_path = os.path.join(base_dir, script)
        if not os.path.exists(script_path):
            summary["results"].append({
                "name": name,
                "success": False,
                "message": f"文件不存在: {script}",
            })
            summary["success"] = False
            continue
        res = run_script(name, script_path)
        summary["results"].append(res)
        if not res["success"]:
            summary["success"] = False
        print("", flush=True)

    # 汇总报告
    print(f"\n{'=' * 50}", flush=True)
    total = len(summary["results"])
    ok = sum(1 for r in summary["results"] if r["success"])
    print(f"📊 汇总：{ok}/{total} 个脚本成功", flush=True)
    print(f"{'=' * 50}", flush=True)

    send_wechat_notification(summary)

    return 0 if summary["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
