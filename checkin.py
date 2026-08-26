#!/usr/bin/env python3
"""GLaDOS 自动签到 + 智能兑换脚本
依赖环境变量 GR_COOKIE（GLaDOS 登录 cookie）

兑换规则（按用户需求）：
  - 积分 >= 500        -> 兑换 500 积分换 100 天
  - 剩余天数 <= 3      -> 兑换 100 积分换 10 天（保底）
  - 其余情况          -> 只签到，攒积分

GLaDOS 兑换方案（planType -> 所需积分 -> 天数）：
  plan100 -> 100 积分 -> 10 天
  plan200 -> 200 积分 -> 30 天
  plan500 -> 500 积分 -> 100 天
"""
import json
import os
import sys
import urllib.request

BASE = "https://glados.space"

# 兑换方案：planType -> (所需积分, 天数)
PLANS = {
    "plan100": (100, 10),
    "plan500": (500, 100),
}


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


def get_balance_points(cookie):
    """从 balance 获取 points 资产的最新余额"""
    _, bal = call("/api/user/balance", cookie)
    for rec in bal.get("data", []):
        if rec.get("asset") == "points":
            return float(rec.get("balance", 0))
    return 0.0


def exchange(cookie, plan_type):
    """执行兑换，返回 (成功, 消息)"""
    _, res = call("/api/user/exchange", cookie, method="POST", body={"planType": plan_type})
    code = res.get("code", 1)
    msg = res.get("message", "")
    if code == 0:
        return True, msg
    return False, msg


def main():
    cookie = os.environ.get("GR_COOKIE")
    if not cookie:
        print("签到失败: GR_COOKIE 环境变量未设置")
        sys.exit(1)

    try:
        # 1. 获取用户信息（邮箱 + 剩余天数）
        _, info = call("/api/user/status", cookie)
        data = info.get("data", {})
        email = data.get("email", "未知邮箱")
        left_days = float(data.get("leftDays", 0) or 0)

        # 2. 签到
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

        # 3. 智能兑换
        exchange_log = []
        balance_points = get_balance_points(cookie)
        exchange_log.append(f"当前积分: {int(balance_points)}")

        # 判断是否满足兑换条件（按优先级: 100天 > 10天保底）
        if balance_points >= PLANS["plan500"][0]:
            ok, msg = exchange(cookie, "plan500")
            exchange_log.append(f"积分满500，兑换100天: {'成功 - ' + str(msg) if ok else '失败 - ' + str(msg)}")
        elif left_days <= 3 and balance_points >= PLANS["plan100"][0]:
            ok, msg = exchange(cookie, "plan100")
            exchange_log.append(f"剩余天数≤3，兑换10天: {'成功 - ' + str(msg) if ok else '失败 - ' + str(msg)}")
        else:
            # 不满足兑换条件，继续攒积分
            if left_days <= 3:
                exchange_log.append(f"剩余天数≤3，但积分不足{PLANS['plan100'][0]}攒够，暂不兑换")
            else:
                exchange_log.append(f"剩余 {int(left_days)} 天 > 3，暂不兑换，继续攒积分")

        # 4. 输出
        print(f"邮箱: {email}")
        print(f"签到结果: {result}")
        print(f"剩余天数: {left_days}")
        for line in exchange_log:
            print(line)
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