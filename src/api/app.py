"""
三段式文案生成器 - FastAPI 后端
"""
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.utils.config import SUPPORTED_FORMATS, CORS_ORIGINS, UPLOAD_DIR
from src.utils.logger import get_logger
from src.core.file_handler import extract_text
from src.core.generator import generate_three_segments

# ==================== 初始化 ====================

# 日志记录器
logger = get_logger(__name__)

# FastAPI 应用
app = FastAPI(
    title="三段式文案生成器",
    description="基于 DeepSeek 的三段式文案生成服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("FastAPI 应用启动成功")


# ==================== 数据模型 ====================

class GenerationResponse(BaseModel):
    """生成响应模型"""
    success: bool
    result: str = None
    error: str = None


# ==================== 工具函数 ====================

def validate_file_extension(filename: str) -> str:
    """验证并返回文件扩展名"""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        logger.warning(f"不支持的文件格式: {ext}")
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持: {', '.join(SUPPORTED_FORMATS)}"
        )
    return ext


async def save_temp_file(file: UploadFile, ext: str) -> str:
    """保存临时文件并返回路径"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=UPLOAD_DIR) as tmp:
        content = await file.read()
        tmp.write(content)
        logger.debug(f"保存临时文件: {tmp.name}, 大小: {len(content)} bytes")
        return tmp.name


def cleanup_files(*paths):
    """清理临时文件"""
    for path in paths:
        if path:
            try:
                os.unlink(path)
                logger.debug(f"清理临时文件: {path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败: {path}, 错误: {e}")


# ==================== API 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    logger.info("健康检查请求")
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerationResponse)
async def generate_copywriting(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """生成三段式文案"""
    logger.info(f"收到文案生成请求: file1={file1.filename}, file2={file2.filename}")
    file1_path = None
    file2_path = None
    
    try:
        # 验证文件格式
        ext1 = validate_file_extension(file1.filename)
        ext2 = validate_file_extension(file2.filename)
        logger.info(f"文件格式验证通过: {ext1}, {ext2}")
        
        # 保存临时文件
        file1_path = await save_temp_file(file1, ext1)
        file2_path = await save_temp_file(file2, ext2)
        logger.info("临时文件保存完成")
        
        # 提取文本
        logger.info("开始提取文本内容")
        text1 = extract_text(file1_path)
        text2 = extract_text(file2_path)
        
        if not text1 or not text2:
            logger.error("文件内容为空")
            raise HTTPException(400, "文件内容为空或无法提取文本")
        
        logger.info(f"文本提取完成: text1 长度={len(text1)}, text2 长度={len(text2)}")
        
        # 生成文案
        logger.info("开始生成文案")
        result = generate_three_segments(text1, text2)
        logger.info("文案生成成功")
        
        return GenerationResponse(success=True, result=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成文案失败: {str(e)}", exc_info=True)
        return GenerationResponse(success=False, error=str(e))
    
    finally:
        # 清理临时文件
        cleanup_files(file1_path, file2_path)


@app.post("/generate-from-text", response_model=GenerationResponse)
async def generate_from_text(text1: str, text2: str):
    """从文本直接生成文案"""
    logger.info("收到文本生成请求")
    try:
        if not text1 or not text2:
            logger.error("文本内容为空")
            raise HTTPException(400, "文本内容不能为空")
        
        logger.info(f"文本长度: text1={len(text1)}, text2={len(text2)}")
        result = generate_three_segments(text1, text2)
        logger.info("文案生成成功")
        return GenerationResponse(success=True, result=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成文案失败: {str(e)}", exc_info=True)
        return GenerationResponse(success=False, error=str(e))


# ==================== 启动 ====================

if __name__ == "__main__":
    import uvicorn
    from src.utils.config import FASTAPI_HOST, FASTAPI_PORT, FASTAPI_RELOAD
    uvicorn.run(
        "src.api.app:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=FASTAPI_RELOAD
    )

