#!/usr/bin/env python3
"""
Crawl4AI Integration Script for Agent Zero Documentation

This script crawls and updates documentation from n8n, Agno, and ACI sources
using Crawl4AI, organizing them into the Agent Zero knowledge base structure.

Usage:
    python crawl4ai_integration.py [--update-all] [--n8n] [--agno] [--aci]
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json
import re

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    print("❌ Crawl4AI not available. Install with: pip install crawl4ai")
    CRAWL4AI_AVAILABLE = False
    sys.exit(1)

# Configuration
KNOWLEDGE_BASE_PATH = Path("knowledge/custom/main")
SOURCES = {
    "n8n": {
        "sitemap_url": "https://docs.n8n.io/sitemap.xml",
        "base_url": "https://docs.n8n.io",
        "output_dir": KNOWLEDGE_BASE_PATH / "n8n",
        "category": "n8n Workflow Automation"
    },
    "agno": {
        "urls": ["https://docs.agno.com/llms-full.txt"],
        "output_dir": KNOWLEDGE_BASE_PATH / "agno",
        "category": "Agno Agent Orchestration"
    },
    "aci": {
        "urls": ["https://www.aci.dev/docs/llms-full.txt"],
        "output_dir": KNOWLEDGE_BASE_PATH / "aci", 
        "category": "ACI Unified Tools"
    }
}


class DocumentationCrawler:
    """Main crawler class for documentation sources"""
    
    def __init__(self):
        self.crawler = None
        self.timestamp = datetime.now().isoformat()
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.crawler = AsyncWebCrawler(verbose=True)
        await self.crawler.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
    
    def create_markdown_header(self, title: str, source_url: str, category: str) -> str:
        """Create standardized markdown header for knowledge files"""
        return f"""# {title}

**Source:** {source_url}  
**Category:** {category}  
**Crawled:** {self.timestamp}  

---

"""
    
    def sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename"""
        # Remove or replace unsafe characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = re.sub(r'\s+', '-', text.strip())
        text = text.lower()
        return text[:100]  # Limit length
    
    async def crawl_n8n_sitemap(self) -> List[Dict[str, Any]]:
        """Crawl n8n documentation from sitemap"""
        print("🔍 Crawling n8n sitemap...")
        
        sitemap_url = SOURCES["n8n"]["sitemap_url"]
        result = await self.crawler.arun(url=sitemap_url)
        
        if not result.success:
            print(f"❌ Failed to crawl sitemap: {sitemap_url}")
            return []
        
        # Extract URLs from sitemap XML
        import xml.etree.ElementTree as ET
        root = ET.fromstring(result.markdown)
        
        urls = []
        for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc_elem is not None:
                urls.append(loc_elem.text)
        
        print(f"📄 Found {len(urls)} URLs in sitemap")
        return urls[:50]  # Limit to first 50 for demo
    
    async def crawl_single_page(self, url: str, output_dir: Path, category: str) -> bool:
        """Crawl a single page and save as markdown"""
        try:
            print(f"📄 Crawling: {url}")
            
            result = await self.crawler.arun(url=url)
            
            if not result.success:
                print(f"❌ Failed to crawl: {url}")
                return False
            
            # Extract title from URL or content
            title_parts = url.replace("https://", "").replace("http://", "").split("/")
            title = " ".join(title_parts[1:]).replace("-", " ").replace("_", " ").title()
            if not title.strip():
                title = f"Documentation from {url}"
            
            # Create filename from URL path
            filename = self.sanitize_filename("_".join(title_parts[1:]))
            if not filename:
                filename = "index"
            filename += ".md"
            
            # Create markdown content
            header = self.create_markdown_header(title, url, category)
            content = header + result.markdown
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = output_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Saved: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error crawling {url}: {e}")
            return False
    
    async def crawl_n8n_docs(self) -> int:
        """Crawl n8n documentation"""
        print("🚀 Starting n8n documentation crawl...")
        
        urls = await self.crawl_n8n_sitemap()
        if not urls:
            return 0
        
        output_dir = SOURCES["n8n"]["output_dir"]
        category = SOURCES["n8n"]["category"]
        
        success_count = 0
        for url in urls:
            if await self.crawl_single_page(url, output_dir, category):
                success_count += 1
        
        print(f"✅ n8n crawl complete: {success_count}/{len(urls)} pages")
        return success_count
    
    async def crawl_text_source(self, source_name: str) -> int:
        """Crawl text-based documentation sources (agno, aci)"""
        print(f"🚀 Starting {source_name} documentation crawl...")
        
        config = SOURCES[source_name]
        output_dir = config["output_dir"]
        category = config["category"]
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for url in config["urls"]:
            try:
                print(f"📄 Crawling: {url}")
                
                result = await self.crawler.arun(url=url)
                
                if not result.success:
                    print(f"❌ Failed to crawl: {url}")
                    continue
                
                # Create filename
                filename = f"{source_name}_llms_full.md"
                
                # Create title
                title = f"{source_name.title()} LLM Framework - Complete Documentation"
                
                # Create markdown content
                header = self.create_markdown_header(title, url, category)
                content = header + result.markdown
                
                # Save file
                file_path = output_dir / filename
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Saved: {file_path}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Error crawling {url}: {e}")
        
        print(f"✅ {source_name} crawl complete: {success_count} files")
        return success_count


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Crawl4AI Documentation Integration")
    parser.add_argument("--update-all", action="store_true", help="Update all documentation sources")
    parser.add_argument("--n8n", action="store_true", help="Update n8n documentation")
    parser.add_argument("--agno", action="store_true", help="Update agno documentation")
    parser.add_argument("--aci", action="store_true", help="Update ACI documentation")
    
    args = parser.parse_args()
    
    if not any([args.update_all, args.n8n, args.agno, args.aci]):
        print("Please specify which documentation to update. Use --help for options.")
        return
    
    if not CRAWL4AI_AVAILABLE:
        print("❌ Crawl4AI not available")
        return
    
    print("🚀 Starting Crawl4AI Documentation Integration...")
    
    async with DocumentationCrawler() as crawler:
        total_files = 0
        
        if args.update_all or args.n8n:
            total_files += await crawler.crawl_n8n_docs()
        
        if args.update_all or args.agno:
            total_files += await crawler.crawl_text_source("agno")
        
        if args.update_all or args.aci:
            total_files += await crawler.crawl_text_source("aci")
    
    print(f"🎉 Documentation integration complete! Total files: {total_files}")


if __name__ == "__main__":
    asyncio.run(main())
