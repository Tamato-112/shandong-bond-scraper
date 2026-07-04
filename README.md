# 山东省专项债信息爬虫

每日自动抓取中国地方政府债券信息披露网站（celma.org.cn）的专项债信息披露文件和项目情况汇总表。

## 功能

- 📥 自动下载 **信息披露文件**（河北、河南两省）
- 📥 自动下载 **项目情况汇总表**（山东、河北、河南三省）
- ⏰ **每日 08:00 自动执行**（GitHub Actions）
- 📤 下载的 PDF 保存为 Actions Artifacts（保留 7 天）
- 📱 **预留微信通知接口**，后续可对接推送结果

## 脚本说明

| 文件 | 说明 |
|------|------|
| `download_bonds_disclosure.py` | 下载文件名含"信息披露文件"的 PDF |
| `download_bonds_summary.py` | 下载文件名含"项目情况汇总表"的 PDF |
| `run_all.py` | 统一入口，依次运行两个爬虫 + 汇总通知 |

## 微信通知接入

`run_all.py` 中的 `send_wechat_notification()` 函数已预留以下三种方式的接入点：

1. **企业微信群机器人** - Webhook URL
2. **PushPlus** - 推送至个人微信
3. **WxPusher** - 消息推送服务

选择一种方式后，填入对应的 Token/Key 即可启用。
