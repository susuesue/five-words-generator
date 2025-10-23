"""
文案生成模块
负责调用 DeepSeek API 生成三段式营销文案
"""

import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.config import (
    DEEPSEEK_API_KEY as api_key,
    DEEPSEEK_API_URL,
    API_TIMEOUT_CONNECT,
    API_TIMEOUT_READ,
    API_RETRY_TOTAL,
    API_RETRY_BACKOFF,
    SUPPORTED_FORMATS,
    MAX_COMBINED_TEXT,
    MAIN_TEMPERATURE,
    MAIN_MAX_TOKENS,
    SUBTITLE_TEMPERATURE,
    SUBTITLE_MAX_TOKENS,
    SUBTITLE_MAX_WORKERS,
    DEFAULT_TITLES
)
from src.utils.logger import get_logger

# ==================== 初始化 ====================

# 获取日志记录器
logger = get_logger(__name__)

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 验证 API 密钥
if not api_key:
    logger.error("DEEPSEEK_API_KEY 未配置")
    raise RuntimeError("DEEPSEEK_API_KEY 未配置")

# 全局 Session（复用连接）
_global_session = None


# ==================== API 调用 ====================

def get_session():
    """获取全局复用的 HTTP Session"""
    global _global_session
    if _global_session is None:
        logger.debug("创建全局 HTTP Session")
        _global_session = requests.Session()
        
        retry_strategy = Retry(
            total=API_RETRY_TOTAL,
            backoff_factor=API_RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=20,
            pool_maxsize=20
        )
        _global_session.mount("http://", adapter)
        _global_session.mount("https://", adapter)
    
    return _global_session


def call_deepseek_api(prompt, temperature=0.5, max_tokens=500):
    """调用 DeepSeek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        logger.debug(f"调用 DeepSeek API - temperature: {temperature}, max_tokens: {max_tokens}")
        response = get_session().post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=(API_TIMEOUT_CONNECT, API_TIMEOUT_READ),
            verify=False
        )
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"].strip()
        logger.debug(f"API 调用成功，返回内容长度: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"API 调用失败: {str(e)}")
        return None


# ==================== 小标题生成 ====================

SUBTITLE_PROMPTS = [
    """请为以下痛点解决方案内容生成一个精炼的小标题（8-18字）。

要求：
1. 用拟人、比喻或动作化的表达，让抽象的痛点变得生动形象
2. 可以使用引号突出关键动词或核心概念（如：让政策补贴不再"躺"在文件里）
3. 语言口语化、有画面感、抓人眼球
4. 直接输出小标题，不要标点符号结尾，不要任何解释

参考风格：让政策补贴不再"躺"在文件里

内容：""",
    
    """请为以下案例成果内容生成一个精炼的小标题（8-18字）。

要求：
1. 突出产品的独特能力，用动词+形容词组合描述（如：能"跨界联想"的AI政策顾问）
2. 可以用引号强调产品的核心特性或创新点
3. 让读者感受到产品的"智能"和"贴心"
4. 直接输出小标题，不要标点符号结尾，不要任何解释

参考风格：能"跨界联想"的AI政策顾问

内容：""",
    
    """请为以下团队优势内容生成一个精炼的小标题（8-18字）。

要求：
1. 用"形容词+团队特征+核心价值"的结构（如：实战派团队打造企业政策外脑）
2. 强调团队的独特定位和专业背景
3. 传递信任感和专业度，让人感觉靠谱
4. 直接输出小标题，不要标点符号结尾，不要任何解释

参考风格：实战派团队打造企业政策外脑

内容："""
]


def generate_single_subtitle(segment: str, prompt_base: str, index: int) -> tuple:
    """生成单个小标题（用于并行处理）"""
    try:
        logger.debug(f"生成第 {index + 1} 个小标题")
        prompt = f"{prompt_base}\n\n{segment}\n\n请直接输出小标题内容（6-15字），不要额外解释。"
        subtitle = call_deepseek_api(prompt, temperature=SUBTITLE_TEMPERATURE, max_tokens=SUBTITLE_MAX_TOKENS)
        
        if subtitle:
            subtitle = subtitle.replace("【", "").replace("】", "").strip()
            logger.info(f"第 {index + 1} 个小标题生成成功: {subtitle}")
            return (index, f"【{subtitle}】\n{segment}")
        else:
            raise Exception("API 返回为空")
    except Exception as e:
        logger.warning(f"第 {index + 1} 个小标题生成失败，使用默认标题: {str(e)}")
        return (index, f"{DEFAULT_TITLES[index]}\n{segment}")


def generate_subtitles(segments: list) -> list:
    """并行生成三个小标题"""
    logger.info("开始并行生成小标题")
    results = [None] * 3
    
    with ThreadPoolExecutor(max_workers=SUBTITLE_MAX_WORKERS) as executor:
        futures = {
            executor.submit(generate_single_subtitle, segment, SUBTITLE_PROMPTS[i], i): i
            for i, segment in enumerate(segments)
        }
        
        for future in as_completed(futures):
            index, subtitled_segment = future.result()
            results[index] = subtitled_segment
    
    return results


# ==================== 文案生成 ====================

def generate_three_segments(text1: str, text2: str) -> str:
    """生成三段式文案"""
    logger.info("开始生成三段式文案")
    
    # 合并文本
    combined_text = f"材料一：{text1}\n\n材料二：{text2}"
    if len(combined_text) > MAX_COMBINED_TEXT:
        logger.warning(f"文本过长（{len(combined_text)} 字符），截断至 {MAX_COMBINED_TEXT} 字符")
        combined_text = combined_text[:MAX_COMBINED_TEXT] + "...(内容已截断)"
    
    # 构建 Prompt
    prompt = f"""
    请基于以下材料，生成三段精炼的营销文案：

    {combined_text}

    **写作要求：**

    第一段（行业痛点 + AI解决方案）：
    - 用生动比喻或具体场景描述行业困境
    - 自然引出AI解决方案，强调其独特价值
    - 语言通俗易懂、有画面感、有传播力
    - 字数：30-60字

    第二段（项目成果与价值）：
    - 用具体案例、数据或生动比喻展现成果
    - 突出产品的独特亮点和实际效果
    - 避免空洞描述，用细节打动人
    - 字数：30-60字

    第三段（团队优势与背景）：
    - 强调团队的专业能力和独特优势
    - 突出"懂技术更懂业务"的特点
    - 传递信任感和专业度
    - 字数：30-60字

    **风格参考示例：**
    "企业常因看不懂、找不到而错失补贴。沃土良桥像一台政策雷达，主动扫描并精准推送匹配机会。

    AI顾问如此周到，为企业申请补贴时，将节能减排资金也贴心纳入，不让任何一笔应得的助力漏掉。

    核心成员兼具AIGC技术深度与SaaS运营经验，真正理解企业痛点，让政策红利精准落入口袋。"

    **输出格式：**
    - 直接输出三段文案，段落之间空一行
    - 不要添加序号、标题或其他标记
    - 不要添加任何解释说明
    - 语言要自然流畅，像是在讲故事
    """
    
    try:
        # 生成主文案
        logger.info("调用 API 生成主文案")
        response_content = call_deepseek_api(prompt, temperature=MAIN_TEMPERATURE, max_tokens=MAIN_MAX_TOKENS)
        
        if not response_content:
            logger.error("主文案生成失败：API 调用返回空")
            return "生成失败：API 调用失败，请检查网络连接和 API 密钥"
        
        logger.info(f"主文案生成成功，长度: {len(response_content)}")
        
        # 分割段落
        segments = [s.strip() for s in re.split(r'\n\s*\n', response_content.strip()) if s.strip()]
        logger.debug(f"第一次分割得到 {len(segments)} 段")
        
        # 如果分割不够，按句号分割
        if len(segments) < 3:
            logger.debug("段落不足，按句号重新分割")
            sentences = re.split(r'[。！？]', response_content.strip())
            segments = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
            logger.debug(f"第二次分割得到 {len(segments)} 段")
        
        # 确保有三个段落
        while len(segments) < 3:
            logger.warning(f"段落不足 3 段，当前 {len(segments)} 段，补充默认内容")
            segments.append("内容生成中...")
        
        segments = segments[:3]
        logger.info("成功提取三段内容")
        
        # 并行生成小标题
        subtitled_result = generate_subtitles(segments)
        
        final_result = "\n\n".join(subtitled_result)
        logger.info(f"文案生成完成，总字数: {len(final_result)}")
        return final_result
    
    except Exception as e:
        logger.error(f"生成文案时出错: {str(e)}", exc_info=True)
        return f"生成失败：{str(e)}\n请检查 API 密钥和网络连接"


# ==================== 文件查找 ====================
# 注意：文件查找功能已移至 src.core.file_handler 模块

