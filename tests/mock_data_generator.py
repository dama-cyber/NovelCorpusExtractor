"""
Mock数据生成器
用于测试时生成模拟数据
"""

import random
import string
from typing import Dict, List, Any
from datetime import datetime, timedelta


class MockDataGenerator:
    """Mock数据生成器"""
    
    @staticmethod
    def generate_id(length: int = 8) -> str:
        """生成随机ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def generate_uuid() -> str:
        """生成UUID格式的ID"""
        parts = [
            ''.join(random.choices(string.hexdigits.lower(), k=8)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=12))
        ]
        return '-'.join(parts)
    
    @staticmethod
    def generate_text(length: int = 100) -> str:
        """生成随机文本"""
        words = ["测试", "数据", "生成", "随机", "内容", "文本", "示例"]
        return ' '.join(random.choices(words, k=length))
    
    @staticmethod
    def generate_project_data() -> Dict[str, Any]:
        """生成项目数据"""
        return {
            "id": MockDataGenerator.generate_uuid(),
            "name": f"测试项目_{MockDataGenerator.generate_id()}",
            "description": MockDataGenerator.generate_text(20),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": random.choice(["active", "completed", "archived"])
        }
    
    @staticmethod
    def generate_card_data() -> Dict[str, Any]:
        """生成卡片数据"""
        return {
            "id": MockDataGenerator.generate_uuid(),
            "title": f"测试卡片_{MockDataGenerator.generate_id()}",
            "content": MockDataGenerator.generate_text(50),
            "type": random.choice(["character", "location", "event", "item"]),
            "created_at": datetime.now().isoformat(),
            "tags": random.sample(["标签1", "标签2", "标签3"], k=random.randint(0, 3))
        }
    
    @staticmethod
    def generate_workflow_data() -> Dict[str, Any]:
        """生成工作流数据"""
        return {
            "id": MockDataGenerator.generate_uuid(),
            "name": f"工作流_{MockDataGenerator.generate_id()}",
            "stages": [
                {
                    "name": "阶段1",
                    "status": random.choice(["pending", "running", "completed"]),
                    "started_at": (datetime.now() - timedelta(hours=1)).isoformat()
                },
                {
                    "name": "阶段2",
                    "status": "pending",
                    "started_at": None
                }
            ],
            "created_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_chunk_data() -> Dict[str, Any]:
        """生成文本块数据"""
        return {
            "id": MockDataGenerator.generate_uuid(),
            "text": MockDataGenerator.generate_text(200),
            "index": random.randint(0, 100),
            "metadata": {
                "source": "test_file.txt",
                "line_start": random.randint(1, 1000),
                "line_end": random.randint(1, 1000)
            }
        }
    
    @staticmethod
    def generate_batch(count: int, generator_func) -> List[Dict[str, Any]]:
        """批量生成数据"""
        return [generator_func() for _ in range(count)]
    
    @staticmethod
    def generate_api_response(success: bool = True, data: Any = None) -> Dict[str, Any]:
        """生成API响应数据"""
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        if success:
            response["data"] = data or {}
        else:
            response["error"] = {
                "code": random.choice(["VALIDATION_ERROR", "NOT_FOUND", "SERVER_ERROR"]),
                "message": "测试错误消息"
            }
        return response


if __name__ == '__main__':
    # 测试生成器
    generator = MockDataGenerator()
    print("生成项目数据:", generator.generate_project_data())
    print("生成卡片数据:", generator.generate_card_data())
    print("生成工作流数据:", generator.generate_workflow_data())


