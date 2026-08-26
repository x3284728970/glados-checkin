# GLaDOS Auto Checkin

每日自动签到 [GLaDOS](https://glados.space) 并获取积分。

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
剩余天数: 8.0000000000000000
```