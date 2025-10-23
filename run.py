"""
三段式文案生成器 - 主启动脚本
"""
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("三段式文案生成器".center(50))
    print("=" * 60)
    print("\n请选择运行模式：")
    print("  1. 启动 FastAPI 后端服务")
    print("  2. 启动 Streamlit 前端界面")
    print("  3. 同时启动后端和前端")
    print("  4. 运行测试脚本（生成两份文案）")
    print("  0. 退出")
    print("\n" + "=" * 60)


def run_fastapi():
    """启动 FastAPI 后端"""
    print("\n🚀 启动 FastAPI 后端服务...")
    print("访问地址: http://localhost:8081")
    print("API 文档: http://localhost:8081/docs")
    print("\n按 Ctrl+C 停止服务\n")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.api.app:app",
        "--host", "0.0.0.0",
        "--port", "8081",
        "--reload"
    ])


def run_streamlit():
    """启动 Streamlit 前端"""
    print("\n🎨 启动 Streamlit 前端界面...")
    print("访问地址: http://localhost:8501")
    print("\n按 Ctrl+C 停止服务\n")
    
    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run",
        "src/web/app.py",
        "--server.port", "8501"
    ])


def run_both():
    """同时启动后端和前端"""
    import threading
    
    print("\n🚀 同时启动后端和前端服务...")
    print("FastAPI: http://localhost:8081")
    print("Streamlit: http://localhost:8501")
    print("\n按 Ctrl+C 停止所有服务\n")
    
    # 在线程中启动 FastAPI
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    
    # 等待一会儿让后端启动
    import time
    time.sleep(2)
    
    # 在主线程启动 Streamlit
    run_streamlit()


def run_test():
    """运行测试脚本"""
    print("\n🧪 运行测试脚本...")
    print("\n" + "=" * 60 + "\n")
    
    subprocess.run([
        sys.executable, "tests/test_generator.py"
    ])


def main():
    """主函数"""
    while True:
        show_menu()
        choice = input("\n请输入选项 (0-4): ").strip()
        
        if choice == "0":
            print("\n👋 再见！")
            break
        elif choice == "1":
            run_fastapi()
        elif choice == "2":
            run_streamlit()
        elif choice == "3":
            run_both()
        elif choice == "4":
            run_test()
        else:
            print("\n❌ 无效选项，请重新输入！")
            input("\n按 Enter 继续...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已停止！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)

