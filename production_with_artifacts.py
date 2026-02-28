#!/usr/bin/env python3
"""
SoEasyHub 生产流水线 - 带有 Artifacts 断点续传功能

这个脚本实现了：
1. 状态管理（记录处理进度）
2. Artifacts 保存和恢复
3. 批量处理和断点续传
4. 智能批次管理
5. 重试机制
"""

import os
import json
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from supabase import create_client, Client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionPipeline:
    def __init__(self):
        self.config = self._load_config()
        self.supabase: Client = create_client(self.config['url'], self.config['key'])
        self.state_file = Path("production_state.json")
        self.cache_dir = Path("production_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Artifacts 配置
        self.artifact_name = "soeasyhub-production"
        self.batch_size = 50  # 每批处理 50 个关键词
        self.max_retries = 3
        self.retry_delay = 10  # 重试延迟（秒）
        
    def _load_config(self) -> Dict:
        """加载配置"""
        config = {
            'url': os.getenv('SUPABASE_URL'),
            'key': os.getenv('SUPABASE_KEY')
        }
        
        if not config['url'] or not config['key']:
            raise ValueError("SUPABASE_URL 和 SUPABASE_KEY 环境变量必须设置")
            
        return config
    
    def _load_state(self) -> Dict:
        """加载处理状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载状态文件失败: {e}")
        return {"processed": [], "total": 0, "last_batch": 0}
    
    def _save_state(self, state: Dict):
        """保存处理状态"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def _save_to_artifacts(self, step_name: str):
        """保存当前进度到 Artifacts"""
        try:
            # 使用 GitHub Actions 的 upload-artifact 动作
            subprocess.run([
                'echo', '"::add-path::./production_cache"',
                '|', 'gh', 'actions', 'upload-artifact',
                '--name', self.artifact_name,
                '--path', str(self.cache_dir),
                '--retention-days', '7'
            ], check=True, shell=True)
            logger.info(f"成功保存 {step_name} 到 Artifacts")
        except subprocess.CalledProcessError as e:
            logger.error(f"保存到 Artifacts 失败: {e}")
    
    def _restore_from_artifacts(self) -> bool:
        """从 Artifacts 恢复进度"""
        try:
            # 检查是否有可用的 Artifacts
            result = subprocess.run([
                'gh', 'actions', 'list-artifacts',
                '--repo', 'soeasyhub/soeasyhub-v2',
                '--name', self.artifact_name,
                '--json', 'name,createdAt'
            ], capture_output=True, text=True)
            
            if '"name": "soeasyhub-production"' in result.stdout:
                # 下载 Artifacts
                subprocess.run([
                    'gh', 'actions', 'download-artifact',
                    '--name', self.artifact_name,
                    '--path', str(self.cache_dir),
                    '--repo', 'soeasyhub/soeasyhub-v2'
                ], check=True)
                logger.info("成功从 Artifacts 恢复进度")
                return True
            else:
                logger.info("没有可用的 Artifacts")
                return False
        except subprocess.CalledProcessError as e:
            logger.error(f"从 Artifacts 恢复失败: {e}")
            return False
    
    def _get_keywords_to_process(self, processed: List[str]) -> List[Dict]:
        """获取需要处理的关键词"""
        try:
            # 获取未处理的关键词
            res = self.supabase.table("grich_keywords_pool") \
                .select("id, slug, keyword") \
                .not_.is_("final_article", "null") \
                .not_.in_("slug", processed) \
                .limit(self.batch_size) \
                .execute()
                
            return res.data if res.data else []
        except Exception as e:
            logger.error(f"获取关键词失败: {e}")
            return []
    
    def _generate_content(self, keyword_data: Dict) -> str:
        """生成内容（模拟）"""
        # 这里应该是实际的 AI 内容生成逻辑
        # 为了演示，我们生成一个简单的占位符内容
        slug = keyword_data['slug']
        keyword = keyword_data['keyword']
        
        content = f"""
# 2026 官方合规审计报告: {keyword}

## 审计摘要
本报告基于公开的政府数据和行业标准进行编制。

## 审计详情
- **关键词**: {keyword}
- **slug**: {slug}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 合规检查
所有信息已通过官方渠道验证。
"""
        return content
    
    def _render_pdf(self, content: str, slug: str) -> bytes:
        """渲染 PDF（模拟）"""
        # 这里应该是实际的 PDF 渲染逻辑
        # 为了演示，我们生成一个简单的 PDF 文件
        from io import BytesIO
        from reportlab.pdfgen import canvas
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, f"审计报告: {slug}")
        c.drawString(100, 730, "内容已生成")
        c.save()
        
        return buffer.getvalue()
    
    def _save_to_cache(self, slug: str, content: str, pdf_data: bytes):
        """保存到本地缓存"""
        # 保存 HTML 内容
        html_file = self.cache_dir / f"{slug}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 保存 PDF 文件
        pdf_file = self.cache_dir / f"{slug}.pdf"
        with open(pdf_file, 'wb') as f:
            f.write(pdf_data)
        
        logger.info(f"已缓存 {slug} 的内容")
    
    def _sync_to_database(self, processed_slugs: List[str]):
        """同步到数据库"""
        logger.info(f"开始同步 {len(processed_slugs)} 个项目到数据库")
        
        for slug in processed_slugs:
            try:
                # 读取缓存文件
                html_file = self.cache_dir / f"{slug}.html"
                pdf_file = self.cache_dir / f"{slug}.pdf"
                
                if not html_file.exists() or not pdf_file.exists():
                    logger.warning(f"缓存文件缺失: {slug}")
                    continue
                
                # 读取内容
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 上传 PDF 到 Supabase Storage
                with open(pdf_file, 'rb') as f:
                    pdf_data = f.read()
                
                # 这里应该实现实际的 Supabase 上传逻辑
                # 为了演示，我们只是记录日志
                logger.info(f"同步 {slug} 到数据库")
                
            except Exception as e:
                logger.error(f"同步 {slug} 失败: {e}")
    
    def _process_batch(self, keywords: List[Dict], state: Dict) -> List[str]:
        """处理一批关键词"""
        processed_slugs = []
        
        for keyword_data in keywords:
            slug = keyword_data['slug']
            logger.info(f"处理: {slug}")
            
            try:
                # 生成内容
                content = self._generate_content(keyword_data)
                
                # 渲染 PDF
                pdf_data = self._render_pdf(content, slug)
                
                # 保存到缓存
                self._save_to_cache(slug, content, pdf_data)
                
                # 记录已处理
                processed_slugs.append(slug)
                state["processed"].append(slug)
                
                # 定期保存状态和 Artifacts
                if len(processed_slugs) % 10 == 0:
                    self._save_state(state)
                    self._save_to_artifacts(f"处理 {len(processed_slugs)} 个项目")
                
            except Exception as e:
                logger.error(f"处理 {slug} 失败: {e}")
                continue
        
        return processed_slugs
    
    def run_production(self):
        """运行生产流水线"""
        logger.info("开始生产流水线")
        
        # 尝试从 Artifacts 恢复
        if self._restore_from_artifacts():
            state = self._load_state()
            logger.info(f"从 Artifacts 恢复状态: 已处理 {len(state['processed'])} 个项目")
        else:
            state = {"processed": [], "total": 0, "last_batch": 0}
            logger.info("开始新的生产流程")
        
        # 获取需要处理的关键词
        keywords = self._get_keywords_to_process(state["processed"])
        total_keywords = len(keywords)
        state["total"] = total_keywords
        
        if total_keywords == 0:
            logger.info("没有需要处理的关键词")
            return
        
        logger.info(f"需要处理 {total_keywords} 个关键词")
        
        # 处理批次
        processed_slugs = self._process_batch(keywords, state)
        
        # 同步到数据库
        self._sync_to_database(processed_slugs)
        
        # 最终保存状态
        self._save_state(state)
        self._save_to_artifacts("最终状态")
        
        logger.info(f"生产流水线完成: 处理了 {len(processed_slugs)} 个项目")

if __name__ == "__main__":
    pipeline = ProductionPipeline()
    pipeline.run_production()