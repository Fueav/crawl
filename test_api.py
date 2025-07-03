import requests
import json

# 测试API
def test_crawler_api():
    base_url = "http://localhost:8000"
    
    print("Testing Crawler API...")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # 测试爬取接口
    try:
        crawl_data = {
            "url": "https://medium.com/@Cryptonian_S",
            "headless": True,
            "delay": 2.0
        }
        
        response = requests.post(
            f"{base_url}/crawl",
            json=crawl_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Crawl test: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            print(f"Total pages: {result['total_pages']}")
            
            # 打印爬取结果
            print("\n=== 爬取结果 ===")
            if result.get('data'):
                for idx, article in enumerate(result['data'], 1):
                    print(f"\n--- Article {idx} ---")
                    print(f"URL: {article.get('url', 'N/A')}")
                    print(f"Depth: {article.get('depth', 'N/A')}")
                    
                    # 打印metadata的主要信息
                    metadata = article.get('metadata', {})
                    if metadata:
                        print(f"Title: {metadata.get('title', 'N/A')}")
                        print(f"Description: {metadata.get('description', 'N/A')}")
                        print(f"Keywords: {metadata.get('keywords', 'N/A')}")
                    
                    # 打印links信息
                    links = article.get('links', {})
                    if links:
                        internal_links = links.get('internal', [])
                        external_links = links.get('external', [])
                        print(f"Internal links: {len(internal_links)}")
                        print(f"External links: {len(external_links)}")
                        
                        # 打印前3个内部链接作为示例
                        if internal_links:
                            print("Sample internal links:")
                            for link in internal_links[:30]:
                                print(f"  - {link}")
                    
                    print("-" * 50)
            else:
                print("No crawl data returned")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Crawl test failed: {e}")

if __name__ == "__main__":
    test_crawler_api()