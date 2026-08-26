# GLaDOS Auto Checkin

每日自动签到 [GLaDOS](https://glados.space) 并获取积分，支持**智能兑换**延长时长。

## 兑换策略

每次签到后会检查积分与剩余天数，自动决定是否兑换：

| 条件 | 操作 |
|------|------|
| 积分 ≥ 500 | 兑换 **100 天**（plan500，消耗 500 积分） |
| 剩余天数 ≤ 3 且积分 ≥ 100 | 兑换 **10 天** 保底（plan100，消耗 100 积分） |
| 其他情况 | 只签到，攒积分 |

> 优先级：够 500 分先换 100 天；不够但快断签（≤3 天）时换 10 天兜底；其余时间只签到攒分。

## 使用方式

### 1. Fork 本仓库

### 2. 添加 Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Name | Value |
|------|-------|
| `GR_COOKIE` | GLaDOS 登录后的完整 Cookie 字符串（如 `koa:sess=...; koa:sess.sig=...`） |

### 3. 手动触发

在 Actions 页面选择 **GLaDOS Auto Checkin** → **Run workflow** 即可手动签到。

## 定时

每天北京时间 **07:15** 自动执行（UTC 23:15）。

## 输出示例

```
邮箱: example@gmail.com
签到结果: 签到成功，获得 3 积分 (连续签到 2 天)
剩余天数: 6.0
当前积分: 151
剩余 6 天 > 3，暂不兑换，继续攒积分
```