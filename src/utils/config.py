"""
配置文件
统一管理项目配置信息
"""
import logging as _logging
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 项目路径 ====================

# 项目根目录（上上级目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 日志目录
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 上传文件临时目录
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ==================== API 配置 ====================

# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"  # API基础URL
DEEPSEEK_MODEL = "deepseek-chat"

# API 超时设置（秒）
API_TIMEOUT_CONNECT = 5  # 连接超时
API_TIMEOUT_READ = 25    # 读取超时
API_TIMEOUT = 120  # 总超时时间

# API 重试设置
API_RETRY_TOTAL = 2           # 重试次数
API_RETRY_BACKOFF = 0.3       # 重试等待时间倍数


# ==================== FastAPI 配置 ====================

# 服务配置
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8080
FASTAPI_RELOAD = True  # 开发模式自动重载

# CORS 配置
CORS_ORIGINS = ["*"]  # 生产环境建议限制具体域名


# ==================== 文件处理配置 ====================

# 支持的文件格式
SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.xlsx', '.pptx'}

# 文件大小限制（MB）
MAX_FILE_SIZE = 10

# 文本提取限制
MAX_PDF_PAGES = 10        # PDF 最多读取页数
MAX_DOCX_PARAGRAPHS = 50  # Word 最多读取段落数
MAX_XLSX_ROWS = 20        # Excel 最多读取行数
MAX_TXT_CHARS = 10000     # TXT 最多读取字符数
MAX_PPTX_SLIDES = 15      # PPTX 最多读取页数

# 文本合并后最大长度
MAX_COMBINED_TEXT = 6000


# ==================== 日志配置 ====================

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志文件
LOG_FILE = LOG_DIR / "app.log"
LOG_ERROR_FILE = LOG_DIR / "error.log"

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志文件大小限制（MB）
LOG_MAX_SIZE = 10

# 日志文件保留数量
LOG_BACKUP_COUNT = 5


# ==================== 验证配置 ====================

def validate_config():
    """验证配置是否正确"""
    errors = []

    if not DEEPSEEK_API_KEY:
        errors.append("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")

    if errors:
        raise RuntimeError("\n".join(errors))

    return True


# 程序启动时验证配置
if __name__ != "__main__":
    try:
        validate_config()
    except RuntimeError as e:
        _logging.warning(f"配置警告：{e}")


# ==================== Config 类（用于兼容） ====================

class Config:
    """配置类，提供便捷的配置访问"""

    def __init__(self):
        """初始化配置"""
        # API配置
        self.DEEPSEEK_API_KEY = DEEPSEEK_API_KEY
        self.DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL
        self.DEEPSEEK_MODEL = DEEPSEEK_MODEL
        self.API_TIMEOUT = API_TIMEOUT

        # 路径配置
        self.BASE_DIR = BASE_DIR
        self.LOG_DIR = LOG_DIR
        self.UPLOAD_DIR = UPLOAD_DIR

        # 文件处理配置
        self.SUPPORTED_FORMATS = SUPPORTED_FORMATS
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
