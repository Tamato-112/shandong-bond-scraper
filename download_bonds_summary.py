#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只下载文件名包含'项目情况汇总表'的PDF文件"""

import os
import re
import time
import sys
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.stdout.reconfigure(line_buffering=True)

BASE_URL = "https://www.celma.org.cn"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": BASE_URL,
}

# 支持下载的省份映射（省份名称 -> ad_code）
PROVINCE_CODES = {
    "山东省": "37",
    "河北省": "13",
    "河南省": "41",
}
CHANNEL_ID = "193"
KEYWORD = "项目情况汇总表"
OUTPUT_BASE_DIR = "./province_bonds_summary"


def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except Exception as e:
        print(f"[ERR] fetch {url}: {e}", flush=True)
        return None


def parse_list(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    div = soup.find("div", {"id": "to-print1"})
    if div:
        for li in div.find_all("li", class_="current"):
            a = li.find("a", href=True)
            if a:
                date = li.find("span")
                links.append({
                    "title": a.get_text(strip=True),
                    "url": urljoin(BASE_URL, a["href"]),
                    "date": date.get_text(strip=True) if date else ""
                })
    return links


def parse_pdfs(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    pdfs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if href.lower().endswith(".pdf") and KEYWORD in text:
            pdfs.append({
                "name": text,
                "url": urljoin(base_url, href)
            })
    return pdfs


def get_total_pages(html):
    soup = BeautifulSoup(html, "html.parser")
    total_page_input = soup.find("input", {"id": "totalPage"})
    if total_page_input:
        try:
            return int(total_page_input.get("value", 1))
        except ValueError:
            pass
    match = re.search(r'共\s*(\d+)\s*页', html)
    if match:
        return int(match.group(1))
    return 1


def download_province(province, ad_code, max_pages=20):
    print(f"\n{'=' * 50}", flush=True)
    print(f"开始抓取【{province}】项目情况汇总表...", flush=True)
    print(f"{'=' * 50}", flush=True)

    output_dir = os.path.join(OUTPUT_BASE_DIR, province)
    os.makedirs(output_dir, exist_ok=True)

    # 第1页
    url1 = f"{BASE_URL}/zqsclb.jhtml?ad_code={ad_code}&channelId={CHANNEL_ID}"
    print(f"\n[1] 获取第1页: {url1}", flush=True)
    h1 = fetch(url1)
    if not h1:
        print("第1页获取失败", flush=True)
        return 0

    total_pages = get_total_pages(h1)
    fetch_pages = min(total_pages, max_pages)
    print(f"总页数: {total_pages}, 将抓取前 {fetch_pages} 页", flush=True)

    links = parse_list(h1)

    # 后续页
    for page_num in range(2, fetch_pages + 1):
        page_url = f"{BASE_URL}/zqsclb_{page_num}.jhtml?ad_code={ad_code}&channelId={CHANNEL_ID}"
        print(f"[{page_num}] 获取第{page_num}页...", flush=True)
        page_html = fetch(page_url)
        if page_html:
            links.extend(parse_list(page_html))
        time.sleep(0.3)

    print(f"\n共 {len(links)} 条公告，筛选'{KEYWORD}'中...", flush=True)

    all_pdfs = []
    for i, link in enumerate(links):
        detail = fetch(link["url"])
        if detail:
            pdfs = parse_pdfs(detail, link["url"])
            for p in pdfs:
                p["date"] = link["date"]
            all_pdfs.extend(pdfs)
        time.sleep(0.3)

    print(f"共找到 {len(all_pdfs)} 个匹配PDF，开始下载...", flush=True)

    downloaded = 0
    skipped = 0
    new_files = []
    for p in all_pdfs:
        name = re.sub(r'[\\/*?<>|:\"]', "_", p["name"])
        if not name.lower().endswith(".pdf"):
            name += ".pdf"
        prefix = f"{p['date']}_" if p["date"] else ""
        path = os.path.join(output_dir, prefix + name)
        if os.path.exists(path):
            print(f"[SKIP] {path}", flush=True)
            skipped += 1
            continue
        try:
            r = requests.get(p["url"], headers=HEADERS, timeout=60, stream=True)
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"[OK] {path}", flush=True)
            downloaded += 1
            new_files.append(os.path.abspath(path))
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERR] {p['url']}: {e}", flush=True)

    print(f"\n【{province}】完成！新下载 {downloaded} 个，跳过 {skipped} 个", flush=True)
    return downloaded, new_files


def main():
    print("=" * 50, flush=True)
    print(f"只下载含'{KEYWORD}'的PDF文件", flush=True)
    print("=" * 50, flush=True)

    total = 0
    all_new_files = []
    for province, ad_code in PROVINCE_CODES.items():
        d, files = download_province(province, ad_code, max_pages=20)
        total += d
        all_new_files.extend(files)
        time.sleep(1)

    print(f"\n{'=' * 50}", flush=True)
    print(f"全部完成！总计新下载 {total} 个文件", flush=True)
    print(f"保存位置: {os.path.abspath(OUTPUT_BASE_DIR)}", flush=True)
    print("=" * 50, flush=True)

    return total, all_new_files


if __name__ == "__main__":
    main()
