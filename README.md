<h1 align="center">
bjyouth-qndxx-action
</h1>

<p align="center">
使用 GitHub Actions 自动完成学习打卡。
</p>

<p align="center">
这个 Action 会每两天在 9:00 AM 尝试学习打卡。
</p>

## 使用方法

点击右上角的 Fork 按钮创建自己的 Repository。

然后，在自己的仓库中的 Settings 的 Secrets 中添加以下设置：

- `BJYOUTH_USERNAME`: 用来登录的用户名
- `BJYOUTH_PASSWORD`: 用来登录的密码

> 可以在 https://m.bjyouth.net/site/login 测试登录信息。

## 检查结果

无需任何设置。如果运行失败，GitHub 会向你的邮箱发送一封邮件。

如果你更改了设置，想手动重新运行，可以点进上方的 Actions 栏，点击 Re-run Jobs 来重新运行。

### ServerChan

[Server 酱](https://sct.ftqq.com/) 可以把填报结果推送到微信服务号或者企业微信内。你可以设置如下 Secret 发送结果：

- `SERVERCHAN_KEY`: 你的 SendKey

## 高级设置

你可以在 `.github/workflows/main.yml` 中来设置每天运行的时间：

```
on:
  schedule:
    - cron: '0 0 * * *'
```

格式是标准的 cron 格式，五个数字分别代表分钟、小时、日期、月份和星期。例如，`0 1 * * *` 表示在每天格林尼治时间的 1:00 AM，也就是在北京时间的 9:00 AM 自动运行。
