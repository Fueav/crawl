# export_storage_from_mac.py
from pathlib import Path
from playwright.sync_api import sync_playwright

# macOS 上的 Chrome/Chromium 用户数据目录
# 注意：Playwright 需要直接指向 profile 所在目录，而不是更深的子目录
MAC_PROFILE_DIR = "/Users/fuyiwei/PythonProject/crawl/my_chrome_profile"

# 导出的 JSON 存放路径
OUTPUT_PATH = "medium_storage_state.json"

with sync_playwright() as p:
    # 以“持久化上下文”模式启动（会直接读取该目录所有 Cookie/LocalStorage 等）
    context = p.chromium.launch_persistent_context(
        user_data_dir=MAC_PROFILE_DIR,
        headless=True,            # headless=True 也行，只要能启动
        args=["--no-sandbox"]
    )

    # 等待浏览器启动，并让 Playwright 从 profile 中自动加载登录态
    # 此时 context 里就已经有基于 macOS Chrome 的所有登录 Cookie
    # 只要你之前在 macOS Chrome “Default” 里已经登录了 Medium，就可以直接导出
    context.storage_state(path=OUTPUT_PATH)
    print(f"✅ 已经从 mac profile 导出 storage_state 到 {OUTPUT_PATH}")
    context.close()