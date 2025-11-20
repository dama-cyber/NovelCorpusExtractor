"""
使用示例
演示如何使用小说语料提取系统
"""

import asyncio
from main import NovelCorpusExtractor

async def example():
    """示例：处理一部玄幻小说"""
    
    # 初始化系统
    extractor = NovelCorpusExtractor("config.yaml")
    
    # 处理小说
    summary = await extractor.process_novel(
        input_file="example_novel.txt",
        novel_type="玄幻"
    )
    
    chunk_results = summary.get("chunk_results", [])
    print(f"处理完成，共处理 {len(chunk_results)} 个文本块")
    if summary.get("workflow"):
        print("创作工作流输出：")
        for stage, payload in summary["workflow"].items():
            print(f"- {stage}: keys={list(payload.keys())}")
    
    # 查看提取的记忆体
    worldview = extractor.memory_manager.load_worldview()
    characters = extractor.memory_manager.load_characters()
    plot = extractor.memory_manager.load_plot()
    foreshadowings = extractor.memory_manager.load_foreshadowing()
    
    print(f"\n世界观设定: {len(worldview)} 项")
    print(f"人物信息: {len(characters)} 个")
    print(f"剧情大纲: {len(plot)} 项")
    print(f"伏笔追踪: {len(foreshadowings)} 个")

if __name__ == "__main__":
    asyncio.run(example())

