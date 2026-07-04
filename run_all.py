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
    微信通知占位函数。
    后续对接个人微信时，在此实现发送消息的逻辑。
    例如：通过企业微信 Bot / Server酱 / PushPlus / WxPusher 等渠道。
    """
    msg = (
        f"📊 债券爬虫日报 {summary['date']}\n"
        f"────────────────\n"
        f"执行状态：{'✅ 成功' if summary['success'] else '⚠️ 部分失败'}\n"
        f"脚本结果：\n"
    )
    for s in summary["results"]:
        emoji = "✅" if s["success"] else "❌"
        msg += f"  {emoji} {s['name']}: {s['message']}\n"
    msg += f"\n详情查看：https://github.com/Tamato-112/shandong-bond-scraper/actions"

    print(f"\n{'=' * 50}", flush=True)
    print("【微信通知预览】", flush=True)
    print(msg, flush=True)
    print(f"{'=' * 50}", flush=True)
    print("⚠️ 微信通知尚未正式接入（预留接口）。", flush=True)

    # === 后续接入点 ===
    # 方法一：企业微信群机器人
    # import requests
    # requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY", json={"msgtype":"text","text":{"content":msg}})
    #
    # 方法二：PushPlus（推送至个人微信）
    # import requests
    # requests.post("https://www.pushplus.plus/send", json={"token":"YOUR_TOKEN","title":"债券爬虫日报","content":msg})
    #
    # 方法三：WxPusher
    # import requests
    # requests.post("https://wxpusher.zjiecode.com/api/send/message", json={"appToken":"YOUR_TOKEN","content":msg,"uids":["YOUR_UID"]})


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
