# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.extractor import NeedsExtractor  # noqa: E402
from src.core.file_handler import extract_text  # noqa: E402
from src.utils.logger import get_logger  # noqa: E402

app = FastAPI(title="五大需求提取器 API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = get_logger(__name__)
extractor = NeedsExtractor()


class ExtractRequest(BaseModel):
    content: str
    projectId: Optional[str] = ""
    projectCode: Optional[str] = ""
    projectDoc: Optional[str] = ""


class ExtractFilesRequest(BaseModel):
    Inquire_Excel: str
    product_Id: str
    product_Code: str
    productDoc: str


class NeedsData(BaseModel):
    projectId: str = ""
    projectCode: str = ""
    projectDoc: str = ""
    inquire_Excel: str = ""
    financing: str = ""
    industry: str = ""
    technology: str = ""
    talent: str = ""
    media: str = ""


class StandardResponse(BaseModel):
    code: str
    msg: str
    data: Optional[NeedsData] = None


def create_response(
    needs_dict: dict = None,
    project_id: str = "",
    project_code: str = "",
    project_doc: str = "",
    inquire_excel: str = "",
    error: str = None,
    code: str = "200",
) -> StandardResponse:
    if error:
        return StandardResponse(code=code, msg=error, data=None)

    data = NeedsData(
        projectId=project_id,
        projectCode=project_code,
        projectDoc=project_doc,
        inquire_Excel=inquire_excel,
        financing=needs_dict.get("融资", ""),
        industry=needs_dict.get("产业", ""),
        technology=needs_dict.get("技术", ""),
        talent=needs_dict.get("人才", ""),
        media=needs_dict.get("媒体", ""),
    )
    return StandardResponse(code="200", msg="生成成功", data=data)


@app.get("/")
async def index():
    return {"service": "五大需求提取器", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/extract", response_model=StandardResponse)
async def extract_needs(request: ExtractRequest):
    """从文本内容提取五大需求"""
    if not request.content or not request.content.strip():
        return JSONResponse(
            status_code=400,
            content=create_response(error="内容为空", code="400").model_dump(),
        )

    try:
        needs = extractor.extract(request.content)
        return create_response(
            needs, request.projectId, request.projectCode, request.projectDoc
        )
    except Exception as e:
        logger.error(f"提取失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=create_response(error=str(e), code="500").model_dump(),
        )


@app.post("/extract/files", response_model=StandardResponse)
async def extract_from_backend_files(request: ExtractFilesRequest):
    """从问卷Excel文件提取五大需求"""
    file_path = Path(request.Inquire_Excel)
    if not file_path.exists():
        return JSONResponse(
            status_code=404,
            content=create_response(
                error=f"文件不存在: {request.Inquire_Excel}", code="404"
            ).model_dump(),
        )

    try:
        inquiry_content = extract_text(str(file_path))
        combined = (
            f"【问卷调查】\n{inquiry_content}\n\n{'='*70}\n\n"
            f"【产品文档】\n{request.productDoc}"
        )

        needs = extractor.extract(combined)
        return create_response(
            needs,
            request.product_Id,
            request.product_Code,
            request.productDoc,
            inquiry_content,
        )
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=create_response(error=str(e), code="500").model_dump(),
        )


if __name__ == '__main__':
    import uvicorn
    from src.utils.config import FASTAPI_HOST, FASTAPI_PORT, FASTAPI_RELOAD
    uvicorn.run(
        "src.api.app_fastapi:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=FASTAPI_RELOAD,
    )
