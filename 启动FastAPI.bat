@echo off
chcp 65001 >nul
echo ================================================
echo 五大需求提取器 - FastAPI 版本
echo ================================================
echo.
echo 正在启动 FastAPI 服务...
echo.
echo 服务地址: http://localhost:8080
echo API 文档: http://localhost:8080/docs
echo 健康检查: http://localhost:8080/health
echo 测试接口: http://localhost:8080/test/a=5/b=3
echo.
echo ================================================
echo.

python src\api\app_fastapi.py

pause

