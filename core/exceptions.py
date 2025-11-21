"""
自定义异常类
提供更清晰的错误分类和处理
"""


class NovelExtractorError(Exception):
    """基础异常类"""
    pass


class ConfigurationError(NovelExtractorError):
    """配置错误"""
    pass


class APIError(NovelExtractorError):
    """API调用错误"""
    def __init__(self, message: str, provider: str = None, status_code: int = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class ValidationError(NovelExtractorError):
    """验证错误"""
    pass


class FileProcessingError(NovelExtractorError):
    """文件处理错误"""
    pass


class WorkflowError(NovelExtractorError):
    """工作流错误"""
    pass


class AgentError(NovelExtractorError):
    """Agent执行错误"""
    pass


class MemoryError(NovelExtractorError):
    """记忆体操作错误"""
    pass


class CorpusError(NovelExtractorError):
    """语料库操作错误"""
    pass


