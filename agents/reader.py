"""
读取者Agent
负责流式读取原始小说文本并进行智能分块
"""

import re
from typing import List, Dict, Generator, Optional
import logging

logger = logging.getLogger(__name__)


class ReaderAgent:
    """读取者Agent - 负责文本分块"""
    
    def __init__(self, chunk_size: int = 1024, overlap: int = 100):
        """
        初始化读取者
        Args:
            chunk_size: 分块大小（token数，约等于字符数/2）
            overlap: 重叠字符数，保证语义连续性
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def read_file(self, file_path: str) -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content or not content.strip():
                    logger.warning(f"文件 {file_path} 为空或只包含空白字符")
                return content
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise
        except UnicodeDecodeError:
            logger.error(f"文件编码错误，尝试使用其他编码: {file_path}")
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"读取文件失败 {file_path}: {e}")
                raise
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            raise
    
    def semantic_chunking(self, text: str) -> Generator[Dict, None, None]:
        """
        语义分块
        按段落、章节等语义边界切分，而非简单按字符数
        """
        # 先按章节分割
        chapters = self._split_by_chapters(text)
        
        for chapter_idx, chapter in enumerate(chapters):
            # 再按段落分割
            paragraphs = self._split_by_paragraphs(chapter)
            
            current_chunk = []
            current_length = 0
            chunk_idx = 0
            
            for para in paragraphs:
                para_length = len(para)
                
                # 如果当前块加上新段落会超过大小，先输出当前块
                if current_length + para_length > self.chunk_size and current_chunk:
                    chunk_text = ''.join(current_chunk)
                    yield {
                        "chunk_id": f"ch{chapter_idx}_c{chunk_idx}",
                        "chapter": chapter_idx + 1,
                        "text": chunk_text,
                        "length": len(chunk_text),
                        "metadata": {
                            "start_pos": current_chunk[0][:50] if current_chunk else "",
                            "end_pos": current_chunk[-1][-50:] if current_chunk else ""
                        }
                    }
                    chunk_idx += 1
                    
                    # 保留重叠部分
                    overlap_text = chunk_text[-self.overlap:] if len(chunk_text) > self.overlap else ""
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text)
                
                current_chunk.append(para)
                current_length += para_length
            
            # 输出最后一个块
            if current_chunk:
                chunk_text = ''.join(current_chunk)
                yield {
                    "chunk_id": f"ch{chapter_idx}_c{chunk_idx}",
                    "chapter": chapter_idx + 1,
                    "text": chunk_text,
                    "length": len(chunk_text),
                    "metadata": {
                        "start_pos": current_chunk[0][:50] if current_chunk else "",
                        "end_pos": current_chunk[-1][-50:] if current_chunk else ""
                    }
                }
    
    def _split_by_chapters(self, text: str) -> List[str]:
        """按章节分割"""
        if not text or not text.strip():
            return [text] if text else []
        
        # 匹配常见的章节标题模式
        patterns = [
            r'第[一二三四五六七八九十\d]+章[^\n]*\n',
            r'Chapter\s+\d+[^\n]*\n',
            r'第[一二三四五六七八九十\d]+节[^\n]*\n',
            r'^\s*第[一二三四五六七八九十\d]+章',
        ]
        
        chapters = []
        current_pos = 0
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.MULTILINE))
            if matches:
                for i, match in enumerate(matches):
                    start = match.start()
                    if start > current_pos:
                        # 添加前一个章节
                        chapter_text = text[current_pos:start].strip()
                        if chapter_text:
                            chapters.append(chapter_text)
                        current_pos = start
                
                # 添加最后一章
                if current_pos < len(text):
                    last_chapter = text[current_pos:].strip()
                    if last_chapter:
                        chapters.append(last_chapter)
                break
        
        # 如果没有找到章节标记，整个文本作为一章
        if not chapters:
            chapters = [text.strip()] if text.strip() else []
        
        return chapters
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """按段落分割"""
        # 按双换行符分割
        paragraphs = re.split(r'\n\s*\n', text)
        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    def process(self, file_path: str) -> Generator[Dict, None, None]:
        """处理文件，返回分块生成器"""
        text = self.read_file(file_path)
        yield from self.semantic_chunking(text)

