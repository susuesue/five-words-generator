"""
三段式文案生成器 - Streamlit 前端
"""
import streamlit as st
import requests

from src.utils.config import STREAMLIT_API_URL

# ==================== 配置 ====================

st.set_page_config(
    page_title="三段式文案生成器",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = STREAMLIT_API_URL


# ==================== 初始化 ====================

def init_session_state():
    """初始化 session state"""
    if 'result_a' not in st.session_state:
        st.session_state.result_a = None
    if 'result_b' not in st.session_state:
        st.session_state.result_b = None
    if 'current_files' not in st.session_state:
        st.session_state.current_files = {}
    if 'generated_results' not in st.session_state:
        st.session_state.generated_results = []


# ==================== API 调用 ====================

def generate_copywriting(api_url, files):
    """调用 API 生成文案"""
    try:
        response = requests.post(
            f"{api_url}/generate",
            files=files,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return result['result'], None
            else:
                return None, result.get('error', '未知错误')
        else:
            return None, f"API 错误: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return None, "请求超时"
    except requests.exceptions.ConnectionError:
        return None, "连接失败，请检查 API 服务是否启动"
    except Exception as e:
        return None, str(e)


def generate_two_versions(api_url, files):
    """生成两份文案"""
    # 生成版本A
    result_a, error_a = generate_copywriting(api_url, files)
    if error_a:
        return None, None, error_a
    
    # 生成版本B
    result_b, error_b = generate_copywriting(api_url, files)
    if error_b:
        return result_a, None, error_b
    
    return result_a, result_b, None


# ==================== UI 组件 ====================

def render_sidebar(api_url):
    """渲染侧边栏"""
    with st.sidebar:
        st.header("⚙️ 使用说明")
        st.markdown("""
        1. 上传两个文档文件
        2. 点击生成按钮
        3. 自动生成两个版本文案
        4. 可独立重新生成每个版本
        
        **支持格式：**  
        PDF、Word、TXT、Excel、PPTX
        """)
        
        # 清空按钮
        if st.button("🗑️ 清空结果", use_container_width=True):
            st.session_state.generated_results = []
            st.session_state.current_files = {}
            st.session_state.result_a = None
            st.session_state.result_b = None
            st.rerun()
        
        # 历史记录（折叠显示）
        if st.session_state.generated_results:
            with st.expander("📚 生成历史", expanded=False):
                st.markdown(f"共 {len(st.session_state.generated_results)} 条记录")
                for idx, record in enumerate(reversed(st.session_state.generated_results), 1):
                    st.markdown(f"**记录 #{idx}**")
                    preview = record['result'][:100] + "..." if len(record['result']) > 100 else record['result']
                    st.text(preview)
                    st.divider()


def render_file_upload():
    """渲染文件上传区域"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 上传第一个文件")
        file1 = st.file_uploader(
            "选择文件1",
            type=['pdf', 'docx', 'txt', 'xlsx', 'pptx'],
            key="file1",
            help="支持 PDF、Word、TXT、Excel、PPTX格式"
        )
        if file1:
            st.info(f"已选择: {file1.name} ({file1.size} bytes)")
    
    with col2:
        st.markdown("### 📄 上传第二个文件")
        file2 = st.file_uploader(
            "选择文件2",
            type=['pdf', 'docx', 'txt', 'xlsx', 'pptx'],
            key="file2",
            help="支持 PDF、Word、TXT、Excel、PPTX 格式"
        )
        if file2:
            st.info(f"已选择: {file2.name} ({file2.size} bytes)")
    
    return file1, file2


def render_result_box(version_name, result, version_key, api_url):
    """渲染单个结果框"""
    st.markdown(f"### 🎯 {version_name}")
    
    if result:
        st.code(result, language="text")
        
        # 重新生成按钮
        if st.button(f"🔄 重新生成 {version_name}", key=f"regen_{version_key}", use_container_width=True):
            if st.session_state.current_files:
                with st.spinner(f"正在重新生成 {version_name}..."):
                    new_result, error = generate_copywriting(api_url, st.session_state.current_files)
                    if new_result:
                        setattr(st.session_state, f"result_{version_key}", new_result)
                        st.session_state.generated_results.append({
                            'version': version_name,
                            'result': new_result
                        })
                        st.success(f"✅ {version_name} 重新生成完成！")
                        st.rerun()
                    else:
                        st.error(f"❌ 重新生成失败: {error}")
    else:
        st.info(f"暂无 {version_name}")


def render_results(api_url):
    """渲染结果区域"""
    if st.session_state.result_a or st.session_state.result_b:
        st.markdown("---")
        st.subheader("📊 生成结果")
        
        # 版本A
        render_result_box("官方推荐版本A", st.session_state.result_a, "a", api_url)
        
        st.markdown("---")
        
        # 版本B
        render_result_box("官方推荐版本B", st.session_state.result_b, "b", api_url)


# ==================== 主程序 ====================

def main():
    """主程序"""
    init_session_state()
    
    # 标题
    st.title("📝 三段式文案生成器")
    st.markdown("基于两份文档材料，自动生成两个版本的三段式营销文案")
    
    # 侧边栏
    render_sidebar(API_BASE_URL)
    
    # 文件上传
    file1, file2 = render_file_upload()
    
    # 生成按钮
    if st.button("🚀 生成两个版本文案", type="primary", use_container_width=True):
        if not file1 or not file2:
            st.error("❌ 请上传两个文件")
            return
        
        # 保存文件信息
        st.session_state.current_files = {
            'file1': (file1.name, file1.getvalue(), file1.type),
            'file2': (file2.name, file2.getvalue(), file2.type)
        }
        
        # 生成两个版本
        with st.spinner("正在生成两个版本的文案，请稍候..."):
            result_a, result_b, error = generate_two_versions(API_BASE_URL, st.session_state.current_files)
            
            if error:
                st.error(f"❌ 生成失败: {error}")
                return
            
            # 保存结果
            if result_a:
                st.session_state.result_a = result_a
                st.session_state.generated_results.append({
                    'version': '版本A',
                    'result': result_a
                })
            
            if result_b:
                st.session_state.result_b = result_b
                st.session_state.generated_results.append({
                    'version': '版本B',
                    'result': result_b
                })
            
            st.success("✅ 两个版本文案生成完成！")
            st.rerun()
    
    # 显示结果
    render_results(API_BASE_URL)


if __name__ == "__main__":
    main()

