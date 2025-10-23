"""
三段式文案生成器 - 测试脚本
测试生成两个版本的文案
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger
from src.core.file_handler import find_project_files, extract_text
from src.core.generator import generate_three_segments

# 获取日志记录器
logger = get_logger(__name__)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("三段式文案生成器 - 测试脚本".center(50))
    print("=" * 60 + "\n")
    
    logger.info("三段式文案生成器 - 测试脚本启动")
    
    # 显示当前工作目录和项目根目录
    import os
    from src.utils.config import BASE_DIR
    
    print(f"📍 当前工作目录: {os.getcwd()}")
    print(f"📍 项目根目录: {BASE_DIR}")
    print(f"📍 数据目录: {BASE_DIR / 'data'}\n")
    
    # 查找项目文件
    print("📂 正在查找 data/ 目录中的文件...")
    logger.info("正在从 data/ 目录查找文件...")
    
    files = find_project_files()  # 默认从 data/ 目录查找
    
    if len(files) < 2:
        error_msg = f"❌ 错误: 在 data/ 目录中只找到 {len(files)} 个文件，需要至少 2 个文件！"
        print(f"\n{error_msg}")
        print(f"\n💡 请将至少 2 个文档文件放入以下目录:")
        print(f"   {BASE_DIR / 'data'}")
        print(f"\n   支持格式: PDF、DOCX、TXT、XLSX、PPTX")
        
        # 检查 data 目录是否存在
        data_dir = BASE_DIR / "data"
        if not data_dir.exists():
            print(f"\n⚠️  data 目录不存在！正在创建...")
            data_dir.mkdir(exist_ok=True)
            print(f"   ✅ 已创建: {data_dir}")
        else:
            print(f"\n📁 data 目录存在，但其中没有支持的文件")
            # 列出目录中的所有文件
            try:
                all_files = list(data_dir.iterdir())
                if all_files:
                    print(f"   目录中的文件:")
                    for f in all_files:
                        print(f"   - {f.name}")
                else:
                    print(f"   目录为空")
            except Exception as e:
                print(f"   无法读取目录: {e}")
        
        print()
        logger.error(error_msg)
        return
    
    print(f"\n✅ 找到 {len(files)} 个文件:")
    for i, file in enumerate(files, 1):
        print(f"   {i}. {file}")
    
    logger.info(f"找到 {len(files)} 个文件: {', '.join(files)}")
    
    # 提取文本
    print(f"\n📄 正在提取文本内容...")
    logger.info("正在提取文本内容...")
    
    try:
        text1 = extract_text(files[0])
        text2 = extract_text(files[1])
        print(f"   ✅ 文件1: {len(text1)} 字符")
        print(f"   ✅ 文件2: {len(text2)} 字符")
        logger.info(f"文本提取完成: 文件1={len(text1)} 字符, 文件2={len(text2)} 字符")
    except Exception as e:
        print(f"\n❌ 文本提取失败: {e}\n")
        logger.error(f"文本提取失败: {e}")
        return
    
    # 生成版本 A
    print("\n" + "=" * 60)
    print("🚀 正在生成【官方推荐版本A】...")
    print("=" * 60)
    logger.info("正在生成【官方推荐版本A】...")
    
    try:
        result_a = generate_three_segments(text1, text2)
        print("\n" + "=" * 60)
        print("【官方推荐版本A】".center(50))
        print("=" * 60)
        print(result_a)
        print("=" * 60)
        logger.info("版本 A 生成成功")
    except Exception as e:
        print(f"\n❌ 版本 A 生成失败: {e}\n")
        logger.error(f"版本 A 生成失败: {e}")
        return
    
    # 生成版本 B
    print("\n" + "=" * 60)
    print("🚀 正在生成【官方推荐版本B】...")
    print("=" * 60)
    logger.info("正在生成【官方推荐版本B】...")
    
    try:
        result_b = generate_three_segments(text1, text2)
        print("\n" + "=" * 60)
        print("【官方推荐版本B】".center(50))
        print("=" * 60)
        print(result_b)
        print("=" * 60)
        logger.info("版本 B 生成成功")
    except Exception as e:
        print(f"\n❌ 版本 B 生成失败: {e}\n")
        logger.error(f"版本 B 生成失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ 所有版本生成完成！".center(50))
    print("=" * 60 + "\n")
    logger.info("所有版本生成完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)

