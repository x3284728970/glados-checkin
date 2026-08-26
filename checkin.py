#!/usr/bin/env python3
"""GLaDOS 自动签到脚本
依赖环境变量 GR_COOKIE（GLaDOS 登录 cookie）
输出: 邮箱 | 签到结果 | 剩余天数
"""
import json
import os
import sys
import urllib.request

BASE = "https://glados.space"


def call(path, cookie, method="GET", body=None):
    url = BASE + path
    headers = {"Cookie": cookie, "User-Agent": "Mozilla/5.0 (Linux; Android 10)"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def main():
    cookie = os.environ.get("GR_COOKIE")
    if not cookie:
        print("签到失败: GR_COOKIE 环境变量未设置")
        sys.exit(1)

    try:
        # 1. 获取用户信息（邮箱）
        _, info = call("/api/user/status", cookie)
        data = info.get("data", {})
        email = data.get("email", "未知邮箱")
        left_days = data.get("leftDays", "?")

        # 2. 执行签到
        _, chk = call("/api/user/checkin", cookie, method="POST", body={})
        code = chk.get("code", -1)
        message = chk.get("message", "")
        points = chk.get("points", 0)
        streak = chk.get("streak", 0)

        if code == 0 and points > 0:
            result = f"签到成功，获得 {points} 积分 (连续签到 {streak} 天)"
        elif code == 1 and "Today's observation logged" in message:
            result = "今日已签到，无需重复"
        else:
            result = f"签到结果: {message} (points={points})"

        print(f"邮箱: {email}")
        print(f"签到结果: {result}")
        print(f"剩余天数: {left_days}")
        sys.exit(0)

    except urllib.error.HTTPError as e:
        print(f"签到失败: HTTP {e.code} - {e.reason}")
        buf = e.read().decode("utf-8", errors="replace")[:200]
        print(f"响应: {buf}")
        sys.exit(2)
    except Exception as e:
        print(f"签到失败: {type(e).__name__}: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()