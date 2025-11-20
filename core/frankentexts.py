"""
Frankentexts语料库管理
负责文本片段的提取、模板化、存储和检索
"""

import os
import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FrankentextsManager:
    """Frankentexts语料库管理器"""
    
    def __init__(self, corpus_dir: str = "corpus_samples"):
        self.corpus_dir = Path(corpus_dir)
        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        # 语料库文件映射（扩展支持36+种类型）
        self.corpus_files = {
            # 基础类型
            "言情": self.corpus_dir / "06_言情预料库.txt",
            "玄幻": self.corpus_dir / "07_玄幻预料库.txt",
            "仙侠": self.corpus_dir / "08_仙侠预料库.txt",
            "悬疑": self.corpus_dir / "09_悬疑预料库.txt",
            "科幻": self.corpus_dir / "10_科幻预料库.txt",
            "奇幻": self.corpus_dir / "11_奇幻预料库.txt",
            "脑洞": self.corpus_dir / "12_脑洞预料库.txt",
            "都市": self.corpus_dir / "13_都市预料库.txt",
            "历史": self.corpus_dir / "14_历史预料库.txt",
            "古言": self.corpus_dir / "15_古言预料库.txt",
            "无CP": self.corpus_dir / "16_无CP预料库.txt",
            # 核心情节
            "重生文": self.corpus_dir / "17_重生文预料库.txt",
            "穿越文": self.corpus_dir / "18_穿越文预料库.txt",
            "穿书文": self.corpus_dir / "19_穿书文预料库.txt",
            "系统文": self.corpus_dir / "20_系统文预料库.txt",
            "无限流": self.corpus_dir / "21_无限流预料库.txt",
            "复仇文": self.corpus_dir / "22_复仇文预料库.txt",
            "升级流": self.corpus_dir / "23_升级流预料库.txt",
            # 热门设定
            "爽文": self.corpus_dir / "24_爽文预料库.txt",
            "屌丝逆袭": self.corpus_dir / "25_屌丝逆袭预料库.txt",
            "废柴流": self.corpus_dir / "26_废柴流预料库.txt",
            "打脸爽文": self.corpus_dir / "27_打脸爽文预料库.txt",
            "追妻火葬场": self.corpus_dir / "28_追妻火葬场预料库.txt",
            "马甲文": self.corpus_dir / "29_马甲文预料库.txt",
            "真假千金": self.corpus_dir / "30_真假千金预料库.txt",
            "迪化文": self.corpus_dir / "31_迪化文预料库.txt",
            "发疯文学": self.corpus_dir / "32_发疯文学预料库.txt",
            "虐文": self.corpus_dir / "33_虐文预料库.txt",
            "CP塑造": self.corpus_dir / "34_CP塑造预料库.txt",
            # 背景职业
            "种田文": self.corpus_dir / "35_种田文预料库.txt",
            "宫斗/宅斗": self.corpus_dir / "36_宫斗宅斗预料库.txt",
            "末世文": self.corpus_dir / "37_末世文预料库.txt",
            "娱乐圈文": self.corpus_dir / "38_娱乐圈文预料库.txt",
            "总裁文": self.corpus_dir / "39_总裁文预料库.txt",
            "灵异文": self.corpus_dir / "40_灵异文预料库.txt",
            "赛博朋克": self.corpus_dir / "41_赛博朋克预料库.txt",
            "商战文": self.corpus_dir / "42_商战文预料库.txt",
            "冒险小说": self.corpus_dir / "43_冒险小说预料库.txt",
            # 通用
            "对话": self.corpus_dir / "44_对话预料库.txt",
            "武侠": self.corpus_dir / "45_武侠预料库.txt",  # 保留兼容
        }
        
        # 向量数据库（可选，如果安装了相关库）
        self.vector_db = None
        self._init_vector_db()
    
    def _init_vector_db(self):
        """初始化向量数据库（可选）"""
        try:
            # 尝试使用Chroma作为向量数据库
            import chromadb
            client = chromadb.Client()
            self.vector_db = client.get_or_create_collection(name="frankentexts")
            logger.info("向量数据库初始化成功")
        except ImportError:
            logger.warning("未安装向量数据库库，将使用文件存储模式")
            self.vector_db = None
        except Exception as e:
            logger.warning(f"向量数据库初始化失败: {e}，将使用文件存储模式")
            self.vector_db = None
    
    def extract_fragment(self, text: str, fragment_type: str, metadata: Dict) -> Dict:
        """提取文本片段并添加元数据"""
        fragment = {
            "id": self._generate_fragment_id(),
            "text": text,
            "type": fragment_type,  # 如：战斗场景、对话、环境描写等
            "metadata": metadata,
            "extracted_at": datetime.now().isoformat(),
            "template": None  # 模板化后的文本
        }
        return fragment
    
    def templateize_fragment(self, fragment: Dict, placeholders: Dict[str, str]) -> str:
        """将片段模板化，替换专有名词为占位符"""
        text = fragment["text"]
        template = text
        
        # 替换专有名词
        for original, placeholder in placeholders.items():
            # 使用正则表达式进行替换，保持大小写
            pattern = re.compile(re.escape(original), re.IGNORECASE)
            template = pattern.sub(placeholder, template)
        
        fragment["template"] = template
        return template
    
    def save_fragment(self, fragment: Dict, genre: str = "通用"):
        """保存片段到对应类型的语料库"""
        if genre not in self.corpus_files:
            genre = "通用"
            corpus_file = self.corpus_dir / "通用预料库.txt"
        else:
            corpus_file = self.corpus_files[genre]
        
        # 追加到文件
        with open(corpus_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"片段ID: {fragment['id']}\n")
            f.write(f"类型: {fragment['type']}\n")
            f.write(f"提取时间: {fragment['extracted_at']}\n")
            f.write(f"元数据: {json.dumps(fragment['metadata'], ensure_ascii=False, indent=2)}\n")
            f.write(f"\n原文:\n{fragment['text']}\n")
            if fragment.get('template'):
                f.write(f"\n模板:\n{fragment['template']}\n")
            f.write(f"{'='*80}\n")
        
        # 如果启用了向量数据库，也存储到向量库
        if self.vector_db:
            try:
                self.vector_db.add(
                    ids=[fragment['id']],
                    documents=[fragment['text']],
                    metadatas=[fragment['metadata']]
                )
            except Exception as e:
                logger.warning(f"向量数据库存储失败: {e}")
        
        logger.info(f"片段已保存到 {corpus_file}")
    
    def search_fragments(self, query: str, fragment_type: Optional[str] = None, 
                        genre: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """搜索匹配的片段"""
        results = []
        
        # 如果使用向量数据库
        if self.vector_db:
            try:
                where_clause = {}
                if fragment_type:
                    where_clause["type"] = fragment_type
                if genre:
                    where_clause["genre"] = genre
                
                search_results = self.vector_db.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_clause if where_clause else None
                )
                
                for i, doc_id in enumerate(search_results['ids'][0]):
                    results.append({
                        "id": doc_id,
                        "text": search_results['documents'][0][i],
                        "metadata": search_results['metadatas'][0][i],
                        "score": search_results['distances'][0][i] if 'distances' in search_results else None
                    })
            except Exception as e:
                logger.warning(f"向量数据库搜索失败: {e}")
        
        # 如果向量数据库不可用，使用文件搜索
        if not results:
            results = self._file_search(query, fragment_type, genre, top_k)
        
        return results
    
    def _file_search(self, query: str, fragment_type: Optional[str], 
                    genre: Optional[str], top_k: int) -> List[Dict]:
        """从文件中搜索片段（简单实现）"""
        results = []
        search_files = []
        
        if genre and genre in self.corpus_files:
            search_files = [self.corpus_files[genre]]
        else:
            search_files = list(self.corpus_files.values())
        
        for corpus_file in search_files:
            if not corpus_file.exists():
                continue
            
            try:
                with open(corpus_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的关键词匹配
                    if query.lower() in content.lower():
                        # 提取包含查询的片段
                        fragments = self._parse_fragments_from_file(corpus_file)
                        for fragment in fragments:
                            if query.lower() in fragment['text'].lower():
                                if not fragment_type or fragment.get('type') == fragment_type:
                                    results.append(fragment)
            except Exception as e:
                logger.warning(f"搜索文件 {corpus_file} 失败: {e}")
        
        return results[:top_k]
    
    def _parse_fragments_from_file(self, file_path: Path) -> List[Dict]:
        """从文件中解析片段"""
        fragments = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 按分隔符分割片段
                parts = content.split('=' * 80)
                for part in parts:
                    if not part.strip():
                        continue
                    # 简单解析（实际应该更完善）
                    fragment = {
                        "text": part,
                        "type": "未知",
                        "metadata": {}
                    }
                    fragments.append(fragment)
        except Exception as e:
            logger.warning(f"解析文件 {file_path} 失败: {e}")
        return fragments
    
    def _generate_fragment_id(self) -> str:
        """生成片段ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        return f"FRAG_{timestamp}_{random_suffix}"
    
    def get_fragments_by_type(self, fragment_type: str, genre: Optional[str] = None, 
                             limit: int = 10) -> List[Dict]:
        """按类型获取片段"""
        return self.search_fragments("", fragment_type=fragment_type, genre=genre, top_k=limit)
    
    def stitch_fragments(self, fragments: List[Dict], transitions: Optional[List[str]] = None) -> str:
        """拼接多个片段，生成连贯文本"""
        if not fragments:
            return ""
        
        result_parts = []
        for i, fragment in enumerate(fragments):
            text = fragment.get('template') or fragment.get('text', '')
            result_parts.append(text)
            
            # 添加过渡句
            if transitions and i < len(transitions):
                result_parts.append(transitions[i])
            elif i < len(fragments) - 1:
                # 默认过渡
                result_parts.append("\n\n")
        
        return "".join(result_parts)

