# 山东省专项债信息爬虫

每日自动抓取中国地方政府债券信息披露网站（celma.org.cn）的专项债信息披露文件和项目情况汇总表。

## 功能

- 📥 自动下载 **信息披露文件**（河北、河南两省）
- 📥 自动下载 **项目情况汇总表**（山东、河北、河南三省）
- ⏰ **每日 08:00 自动执行**（GitHub Actions）
- 📤 下载的 PDF 保存为 Actions Artifacts（保留 7 天）
- 📱 **执行结果推送至个人微信**（PushPlus）

## 脚本说明

| 文件 | 说明 |
|------|------|
| `download_bonds_disclosure.py` | 下载文件名含"信息披露文件"的 PDF |
| `download_bonds_summary.py` | 下载文件名含"项目情况汇总表"的 PDF |
| `run_all.py` | 统一入口，依次运行两个爬虫 + 汇总通知 |

## 微信通知

使用 **PushPlus** 推送执行结果到个人微信。Token 已配置在 GitHub Actions Secrets 中（`PUSHPLUS_TOKEN`）。

每次执行完成后，你会收到类似这样的消息：

> **债券爬虫日报 2026-07-04 20:00**
> 执行状态：✅ 全部成功
> - ✅ 信息披露文件：执行完成
> - ✅ 项目情况汇总表：执行完成
>
> [查看 Actions 详情](https://github.com/Tamato-112/shandong-bond-scraper/actions)
