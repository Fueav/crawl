import asyncio
import json
import os
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from bs4 import BeautifulSoup
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter,
    DomainFilter,
    ContentTypeFilter
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 读取配置文件
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
        return {
            "server": {"host": "0.0.0.0", "port": 8000},
            "crawler": {
                "storage_state": "",
                "browser_type": "chromium",
                "default_headless": True,
                "default_delay": 2.0
            }
        }
    except json.JSONDecodeError as e:
        logger.error(f"配置文件格式错误: {e}")
        raise

config = load_config()
app = FastAPI(title="Solv Crawler Service", version="1.0.0")

class CrawlRequest(BaseModel):
    url: HttpUrl
    headless: bool = True
    max_depth: int = 1
    delay: float = 2.0

class CrawlResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    total_pages: int = 0

async def crawl_website(url: str, headless: bool = True, max_depth: int = 1, delay: float = 2.0) -> List[Dict[str, Any]]:
    """
    爬取指定URL的网站内容 - 完全照搬solv_crawler_v2.py的逻辑
    
    Args:
        url: 要爬取的URL
        headless: 是否使用无头浏览器
        max_depth: 爬取深度
        delay: 请求间隔
    
    Returns:
        包含爬取结果的字典列表
    """
    
    # 完全照搬solv_crawler_v2.py的配置
    crawler_config = CrawlerRunConfig(
        scraping_strategy=LXMLWebScrapingStrategy(),
        mean_delay=delay,
        delay_before_return_html=5.0,
        max_range=0.5,
        semaphore_count=1,
        scroll_delay=1,
        scan_full_page=True
    )

    browser_config = BrowserConfig(
        headless=headless,
        verbose=True,
        browser_type=config["crawler"]["browser_type"],
        storage_state=config["crawler"]["storage_state"]
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(url, config=crawler_config)

        logger.info(f"Crawled {len(results)} pages in total")

        # 完全照搬solv_crawler_v2.py的数据处理逻辑，但不写入文件，直接返回JSON数据
        crawl_results = []
        for idx, res in enumerate(results, 1):
            # 取 URL path 作为文件名，空则用序号
            slug = urlparse(res.url).path.strip("/") or f"article_{idx}"
            slug = slug.replace("/", "_")        # 避免子路径斜杠

            article_data = {
                "url": res.url,
                "depth": res.metadata.get("depth", 0),
                "metadata": res.metadata,
                "links": getattr(res, "links", {})  # write internal/external links if present
            }
            crawl_results.append(article_data)
        
        return crawl_results

@app.get("/")
async def root():
    """API根路径"""
    return {"message": "Solv Crawler Service is running"}

@app.post("/crawl", response_model=CrawlResponse)
async def crawl_endpoint(request: CrawlRequest):
    """
    爬取指定URL的内容
    
    Args:
        request: 包含URL和配置参数的请求
    
    Returns:
        爬取结果的JSON响应
    """
    try:
        logger.info(f"Starting crawl for URL: {request.url}")
        
        # 执行爬取
        results = await crawl_website(
            str(request.url),
            headless=request.headless,
            max_depth=request.max_depth,
            delay=request.delay
        )
        
        logger.info(f"Successfully crawled {len(results)} pages")
        
        return CrawlResponse(
            success=True,
            message=f"Successfully crawled {len(results)} pages",
            data=results,
            total_pages=len(results)
        )
    
    except Exception as e:
        logger.error(f"Error crawling {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "Solv Crawler Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config["server"]["host"], 
        port=config["server"]["port"]
    )