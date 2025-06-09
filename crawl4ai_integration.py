#!/usr/bin/env python3
"""
Crawl4AI Integration Script for Agent Zero Knowledge Base
Crawls documentation from n8n, Agno, and ACI and formats for Agent Zero's enhanced memory system

NOTE: The documentation has already been pre-crawled and included in this repository.
This script is provided for:
- Updating the documentation with fresh content
- Crawling additional sources
- Customizing the crawling process

To use this script:
1. Install Crawl4AI: pip install crawl4ai
2. Install Playwright browsers: python -m playwright install
3. Run: python crawl4ai_integration.py
"""

import asyncio
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from crawl4ai import AsyncWebCrawler


class DocumentationCrawler:
    """Comprehensive documentation crawler for Agent Zero knowledge base"""
    
    def __init__(self, output_dir: str = "knowledge/custom/main"):
        self.output_dir = Path(output_dir)
        self.session: Optional[aiohttp.ClientSession] = None
        self.crawler: Optional[AsyncWebCrawler] = None
        
        # Create output directories
        self.n8n_dir = self.output_dir / "n8n"
        self.agno_dir = self.output_dir / "agno" 
        self.aci_dir = self.output_dir / "aci"
        
        for dir_path in [self.n8n_dir, self.agno_dir, self.aci_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        self.crawler = AsyncWebCrawler(verbose=True)
        await self.crawler.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.crawler:
            await self.crawler.close()
        if self.session:
            await self.session.close()
    
    def clean_content(self, content: str) -> str:
        """Clean and format content for Agent Zero knowledge base"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove navigation elements and common web artifacts
        patterns_to_remove = [
            r'Skip to main content',
            r'Toggle navigation',
            r'Search\s*$',
            r'Edit this page',
            r'Last updated:.*',
            r'Cookie policy',
            r'Privacy policy',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
        
        return content.strip()
    
    def create_knowledge_file(self, title: str, content: str, source_url: str, 
                            category: str, output_path: Path) -> None:
        """Create a formatted knowledge file for Agent Zero"""
        timestamp = datetime.now().isoformat()
        
        formatted_content = f"""# {title}

**Source:** {source_url}  
**Category:** {category}  
**Crawled:** {timestamp}  

---

{content}

---

*This document was automatically crawled and processed for Agent Zero's knowledge base.*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        print(f"✅ Created knowledge file: {output_path}")
    
    async def download_text_file(self, url: str) -> str:
        """Download a text file directly"""
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise Exception(f"Failed to download {url}: HTTP {response.status}")
    
    async def crawl_n8n_documentation(self) -> None:
        """Crawl n8n documentation from sitemap"""
        print("🔍 Crawling n8n documentation...")
        
        sitemap_url = "https://docs.n8n.io/sitemap.xml"
        
        try:
            # Download sitemap
            sitemap_content = await self.download_text_file(sitemap_url)
            root = ET.fromstring(sitemap_content)
            
            # Extract URLs from sitemap
            urls = []
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    urls.append(loc_elem.text)
            
            print(f"📄 Found {len(urls)} URLs in n8n sitemap")
            
            # Crawl each URL (limit to first 50 for initial implementation)
            for i, url in enumerate(urls[:50]):
                try:
                    print(f"🕷️  Crawling n8n page {i+1}/50: {url}")
                    
                    result = await self.crawler.arun(
                        url=url,
                        word_count_threshold=10,
                        bypass_cache=True
                    )
                    
                    if result.success and result.markdown:
                        # Create filename from URL
                        parsed_url = urlparse(url)
                        filename = parsed_url.path.strip('/').replace('/', '_') or 'index'
                        if not filename.endswith('.md'):
                            filename += '.md'

                        # Clean and save content
                        clean_content = self.clean_content(result.markdown)
                        if len(clean_content) > 100:  # Only save substantial content
                            self.create_knowledge_file(
                                title=f"n8n Documentation: {filename.replace('_', ' ').replace('.md', '').title()}",
                                content=clean_content,
                                source_url=url,
                                category="n8n Workflow Automation",
                                output_path=self.n8n_dir / filename
                            )
                    
                    # Small delay to be respectful
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Failed to crawl {url}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Failed to process n8n sitemap: {e}")
    
    async def crawl_agno_documentation(self) -> None:
        """Crawl Agno LLM documentation"""
        print("🔍 Crawling Agno documentation...")
        
        agno_url = "https://docs.agno.com/llms-full.txt"
        
        try:
            content = await self.download_text_file(agno_url)
            clean_content = self.clean_content(content)
            
            self.create_knowledge_file(
                title="Agno LLM Framework - Complete Documentation",
                content=clean_content,
                source_url=agno_url,
                category="Agno Agent Orchestration",
                output_path=self.agno_dir / "agno_llms_full.md"
            )
            
        except Exception as e:
            print(f"❌ Failed to crawl Agno documentation: {e}")
    
    async def crawl_aci_documentation(self) -> None:
        """Crawl ACI documentation"""
        print("🔍 Crawling ACI documentation...")
        
        aci_url = "https://www.aci.dev/docs/llms-full.txt"
        
        try:
            content = await self.download_text_file(aci_url)
            clean_content = self.clean_content(content)
            
            self.create_knowledge_file(
                title="ACI (AI Code Interpreter) - Complete Documentation",
                content=clean_content,
                source_url=aci_url,
                category="ACI Tool Interface",
                output_path=self.aci_dir / "aci_llms_full.md"
            )
            
        except Exception as e:
            print(f"❌ Failed to crawl ACI documentation: {e}")
    
    async def run_full_crawl(self) -> None:
        """Run the complete documentation crawling process"""
        print("🚀 Starting comprehensive documentation crawl for Agent Zero...")
        print(f"📁 Output directory: {self.output_dir}")
        
        # Run all crawling tasks
        await asyncio.gather(
            self.crawl_n8n_documentation(),
            self.crawl_agno_documentation(), 
            self.crawl_aci_documentation(),
            return_exceptions=True
        )
        
        print("✅ Documentation crawling completed!")
        print(f"📊 Knowledge files saved to:")
        print(f"   • n8n: {self.n8n_dir}")
        print(f"   • Agno: {self.agno_dir}")
        print(f"   • ACI: {self.aci_dir}")


async def main():
    """Main execution function"""
    async with DocumentationCrawler() as crawler:
        await crawler.run_full_crawl()


if __name__ == "__main__":
    asyncio.run(main())
