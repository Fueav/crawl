import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)

import json

async def main():


    config = CrawlerRunConfig(
        scraping_strategy=LXMLWebScrapingStrategy(),
        mean_delay=2.0,
        delay_before_return_html=5.0,
        max_range=0.5,
        semaphore_count=1,
        scroll_delay=1,
        scan_full_page=True
    )

    browser_config = BrowserConfig(
        headless=False,             # 'True' for automated runs
        verbose=True,
        # use_persistent_context=True,
        # use_managed_browser=True,
        browser_type="chromium",
        # cdp_url="ws://localhost:9222/devtools/browser/ee034cb9-9c3a-4e76-9358-3b5e4affe71a",
        # user_data_dir="/Users/fuyiwei/PythonProject/crawl/my_chrome_profile",
        storage_state="/Users/fuyiwei/PythonProject/crawl/medium_storage_state.json"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun("https://medium.com/@Cryptonian_S", config=config)

        print(f"Crawled {len(results)} pages in total")

               # ---- Save each article to its own JSON file ----
        save_dir = "solv_articles_v2"
        os.makedirs(save_dir, exist_ok=True)

        for idx, res in enumerate(results, 1):
            # 取 URL path 作为文件名，空则用序号
            slug = urlparse(res.url).path.strip("/") or f"article_{idx}"
            slug = slug.replace("/", "_")        # 避免子路径斜杠
            file_path = os.path.join(save_dir, f"{slug}.json")

            article_data = {
                "url": res.url,
                "depth": res.metadata.get("depth", 0),
                "metadata": res.metadata,
                "links": getattr(res, "links", {})  # write internal/external links if present
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved {len(results)} articles to directory '{save_dir}'")
        

if __name__ == "__main__":
    asyncio.run(main())
