# -*- coding: utf-8 -*-
"""
五大需求提取器核心模块
从问卷中提取：融资、产业、技术、人才、媒体五大主题需求
"""

import re
import json
from typing import Dict
import requests
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NeedsExtractor:
    """五大需求提取器"""

    # 五大主题定义
    THEMES = {
        "融资": "与资金、投资、融资、财务相关的需求",
        "产业": "与产业发展、市场拓展、商业合作相关的需求",
        "技术": "与技术研发、技术支持、技术创新相关的需求",
        "人才": "与人才招聘、人才培养、团队建设相关的需求",
        "媒体": "与宣传推广、媒体报道、品牌建设相关的需求"
    }

    def __init__(self):
        """初始化提取器"""
        self.config = Config()
        self.session = requests.Session()
        # 禁用代理，避免代理连接错误
        self.session.trust_env = False
        logger.info("五大需求提取器初始化成功")

    def extract(self, questionnaire_content: str) -> Dict[str, str]:
        """
        从问卷内容中提取五大主题需求

        Args:
            questionnaire_content: 问卷文本内容

        Returns:
            dict: {
                "融资": "需求描述文字。",
                "产业": "需求描述文字。",
                "技术": "",
                "人才": "需求描述文字。",
                "媒体": ""
            }
        """
        logger.info("="*70)
        logger.info("开始提取五大需求")
        logger.info("="*70)
        logger.debug(f"问卷内容长度: {len(questionnaire_content)} 字符")

        # 构建提示词
        prompt = self._build_prompt(questionnaire_content)

        try:
            # 调用AI提取需求
            logger.info("🤖 调用AI分析问卷...")
            response = self._call_api(prompt)

            # 解析结果
            needs_dict = self._parse_response(response)

            # 确保所有主题都存在
            result = {}
            for theme in self.THEMES.keys():
                result[theme] = needs_dict.get(theme, "")

            # 统计信息
            themes_with_needs = [k for k, v in result.items() if v]

            logger.info("="*70)
            logger.info("✅ 提取完成")
            logger.info(f"   涉及 {len(themes_with_needs)} 个主题: {', '.join(themes_with_needs)}")
            logger.info("="*70)

            return result

        except Exception as e:
            logger.error(f"❌ 提取需求失败: {str(e)}", exc_info=True)
            # 返回空结果
            return {theme: "" for theme in self.THEMES.keys()}

    def _build_prompt(self, questionnaire_content: str) -> str:
        """构建AI提示词"""
        return f"""你是一位擅长需求提炼的分析专家。请根据Excel问卷表格，用一句话分别概括其在融资、产业、人才、技术、媒体方面的核心需求，突出项目"缺什么"和"要什么"。

🚨🚨🚨 格式要求（必须遵守）🚨🚨🚨
❌ 句子不要有任何序号（如 "1. " "① " "1、" 等）
✅ 每句话末尾必须加句号 "。"
✅ 直接描述需求，不要任何前缀

🚨🚨🚨 重要提醒：请仔细阅读问卷内容，逐个检查五大主题，确保不遗漏任何需求！ 🚨🚨🚨

【五大主题定义】
1. 融资：资金、投资、融资轮次等方面的需求
2. 产业：产业合作、客户拓展、市场开拓等方面的需求
3. 技术：技术研发、算力支持、技术突破等方面的需求
4. 人才：人才招聘、团队建设、专家引进等方面的需求
5. 媒体：媒体报道、品牌建设、行业影响力等方面的需求

【问卷内容】
{questionnaire_content}

【核心要求】🚨
1. ✅ 仔细检查问卷中每一个主题的需求，确保不遗漏
2. ✅ 严格对照问卷表格内容进行提取
3. ✅ 确保每一句都源自表格内容，不添加任何引申或脑补信息
4. ✅ 若问卷中没有提到对应的需求，则该主题为空列表 []
5. ✅ 每句话字数控制在 20-40 字之间（确保表达完整准确）
6. ✅ 语言要生动有表现力，可使用行业术语和生动比喻
7. ✅ 信息传达必须保持准确，突出"缺什么"和"要什么"
8. ✅ 结构：需求内容 + 目的/结果

【标准样例参考】✨
请严格模仿以下样例的风格和表达方式：

【融资样例】
"需要Pre-A轮融资，将我们的AI Agent从技术原型转化为商业产品。"
→ 特点：具体轮次 + 明确转化目标

【产业样例】
"寻找XX行业的标杆客户，共同打造AI Agent的'灯塔式'示范案例。"
→ 特点：标杆客户 + 生动比喻（灯塔式）

【技术样例】
"希望获得大规模、低延迟的算力支持，以突破我们AI Agent的性能瓶颈。"
→ 特点：技术细节（大规模、低延迟）+ 明确目的（突破瓶颈）

【人才样例】
"以极具竞争力的待遇诚聘能手撕底层代码的顶级人才。"
→ 特点：生动表达（手撕代码）+ 强调待遇

【媒体样例】
"希望被主流科技媒体报道，确立我们在大模型智能体赛道上的领先者形象。"
→ 特点：明确媒体类型 + 战略定位（赛道、领先者）

【表达技巧】💡
1. 使用行业热词：AI Agent、大模型、算力、性能瓶颈、赛道、智能体
2. 生动比喻：灯塔式、标杆、领先者、手撕代码
3. 具体细节：融资轮次（天使轮/Pre-A/A轮）、技术指标（低延迟/大规模）
4. 战略表达：从...转化为...、突破...瓶颈、确立...形象、共同打造...
5. 竞争视角：顶级人才、领先者、标杆客户、极具竞争力

【输出格式】⚠️
请严格按照以下JSON格式返回，不要添加任何其他文字：
{{
    "融资": "需求描述文字，末尾必须加句号。",
    "产业": "需求描述文字，末尾必须加句号。",
    "技术": "需求描述文字，末尾必须加句号。",
    "人才": "需求描述文字，末尾必须加句号。",
    "媒体": "需求描述文字，末尾必须加句号。"
}}

【格式规范】🚨
1. ❌ 句子不要有任何序号（如"1. "或"①"）
2. ✅ 每句话末尾必须加句号"。"
3. ✅ 直接描述需求内容，不要有前缀
4. ✅ 如果某主题无需求，返回空字符串 ""
5. 🚨 每个主题只需一句话概括，不要列表形式

【重要说明】⚠️
上述格式只是结构示例，实际输出必须根据问卷内容动态决定：
- ✅ 如果问卷中提到该主题需求 → 用一句话概括并美化表达（末尾加句号）
- ✅ 如果问卷中未提到该主题 → 该主题返回空字符串 ""
- ✅ 不要固定某些主题为空，要看实际问卷内容

【输出示例1】（五个主题都有需求）
{{
    "融资": "寻求1000万Pre-A轮融资，将AI产品从技术原型推向商业市场。",
    "产业": "寻找金融行业的标杆客户，共同打造智能风控的'灯塔式'案例。",
    "技术": "希望获得大规模GPU算力支持，突破AI模型训练的性能瓶颈。",
    "人才": "以极具竞争力的待遇诚聘能攻克算法难题的顶尖工程师。",
    "媒体": "期待主流科技媒体深度报道，确立我们在AI赛道上的创新者形象。"
}}

【输出示例2】（部分主题有需求）
{{
    "融资": "寻求500万天使轮融资，加速产品研发与市场验证。",
    "产业": "",
    "技术": "希望获得云端算力支持，提升产品性能与用户体验。",
    "人才": "",
    "媒体": ""
}}

【输出示例3】（不同组合）
{{
    "融资": "",
    "产业": "寻找医疗行业的战略合作伙伴，共同开拓智慧医疗市场。",
    "技术": "",
    "人才": "高薪诚聘全栈工程师，加速产品迭代与功能完善。",
    "媒体": "希望通过行业展会与媒体报道，提升品牌影响力。"
}}

【❌ 错误示例 - 千万不要这样写】
{{
    "融资": "1. 寻求1000万Pre-A轮融资，将AI产品从技术原型推向商业市场",
    "产业": "① 寻找金融行业的标杆客户，共同打造智能风控的'灯塔式'案例",
    "技术": "1、希望获得大规模GPU算力支持，突破AI模型训练的性能瓶颈"
}}
错误原因：
- ❌ 有序号前缀（1. / ① / 1、）
- ❌ 末尾没有句号

【✅ 正确示例 - 请务必这样写】
{{
    "融资": "寻求1000万Pre-A轮融资，将AI产品从技术原型推向商业市场。",
    "产业": "寻找金融行业的标杆客户，共同打造智能风控的'灯塔式'案例。",
    "技术": "希望获得大规模GPU算力支持，突破AI模型训练的性能瓶颈。"
}}
正确特点：
- ✅ 没有序号前缀
- ✅ 末尾有句号
- ✅ 每个主题一句话，不是列表

⚠️ 关键注意：
- 直接返回JSON，不要有任何前缀或后缀说明
- 必须严格基于问卷内容，不能脑补
- 有需求就提取，没需求就空字符串，动态判断
- 每句话必须在20-40字之间
- 风格必须参考上述标准样例
- 🚨 每个主题的值是字符串，不是数组/列表

🚨🚨🚨 再次强调格式（这很重要！）🚨🚨🚨
❌ 绝对不要写："1. 需求内容" 或 "① 需求内容" 或 "1、需求内容"
❌ 绝对不要用列表格式：["需求内容"]
✅ 必须直接写："需求内容。"（字符串，不是列表）
✅ 每句话末尾必须有句号 "。"
✅ 句子开头直接是内容，不要任何数字或符号前缀"""

    def _call_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        url = f"{self.config.DEEPSEEK_BASE_URL}/chat/completions"

        payload = {
            "model": self.config.DEEPSEEK_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位擅长需求提炼和诗意表达的分析专家。"
                        "你能准确理解问卷内容，并用有表现力的语言概括需求。"
                        "请仔细检查所有五个主题（融资、产业、技术、人才、媒体），"
                        "确保不遗漏任何需求。只返回JSON格式结果，不添加任何解释。"
                        "\n\n【格式要求 - 必须严格遵守】\n"
                        "❌ 绝对不要在句子前面加序号（如 1. / ① / 1、 等）\n"
                        "❌ 绝对不要用列表/数组格式（如 [\"内容\"]）\n"
                        "✅ 每个主题的值必须是字符串，不是列表\n"
                        "✅ 每句话末尾必须加句号\n"
                        "✅ 直接描述需求内容，句子开头不要任何数字或符号\n"
                        "✅ 如果某主题无需求，返回空字符串 \"\""
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2500
        }

        headers = {
            "Authorization": f"Bearer {self.config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.API_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content'].strip()

            logger.debug(f"API响应成功，内容长度: {len(content)}")
            return content

        except requests.exceptions.Timeout:
            logger.error("API调用超时")
            raise Exception("API调用超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            logger.error(f"API调用失败: {str(e)}")
            raise Exception(f"API调用失败: {str(e)}")

    def _parse_response(self, response: str) -> Dict[str, str]:
        """解析AI响应中的JSON"""
        try:
            # 尝试直接解析JSON
            needs_dict = json.loads(response)
            logger.debug("直接JSON解析成功")
        except json.JSONDecodeError:
            # 尝试提取JSON
            logger.debug("尝试提取JSON内容")
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    needs_dict = json.loads(json_match.group(0))
                    logger.debug("提取JSON解析成功")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {str(e)}")
                    return {}
            else:
                logger.warning("无法找到JSON格式数据")
                return {}

        # 后处理：确保格式正确（去除序号、添加句号）
        needs_dict = self._post_process_needs(needs_dict)
        return needs_dict

    def _post_process_needs(self, needs_dict: Dict[str, str]) -> Dict[str, str]:
        """后处理需求文本，确保格式正确"""
        processed = {}
        has_changes = False

        for theme, text in needs_dict.items():
            if not text or not isinstance(text, str):
                processed[theme] = ""
                continue

            original = text
            # 去除前面的序号（支持多种格式）
            cleaned = text.strip()

            # 匹配并去除各种序号格式：
            # 1. / 1、 / 1) / 1） / ① / 一、 / (1) / 【1】 等
            patterns = [
                r'^[\d]+[.．。、,，)\）]\s*',      # 阿拉伯数字 + 标点
                r'^[①②③④⑤⑥⑦⑧⑨⑩]\s*',          # 圆圈数字
                r'^[一二三四五六七八九十]+[.．。、,，)\）]\s*',  # 中文数字 + 标点
                r'^\([0-9]+\)\s*',                # (1)
                r'^【[0-9]+】\s*',                # 【1】
                r'^\[[0-9]+\]\s*',                # [1]
            ]

            for pattern in patterns:
                cleaned = re.sub(pattern, '', cleaned)

            # 去除可能的前导空格
            cleaned = cleaned.lstrip()

            # 确保末尾有句号
            if cleaned and not cleaned.endswith('。'):
                cleaned += '。'

            # 记录修改
            if original != cleaned:
                has_changes = True
                logger.info(f"[后处理修正] [{theme}]:")
                logger.info(f"   原始: {original}")
                logger.info(f"   修正: {cleaned}")

            processed[theme] = cleaned

        if has_changes:
            logger.info("[完成] 需求格式后处理完成（已修正序号）")
        else:
            logger.debug("[完成] 需求格式后处理完成（无需修正）")

        return processed

    def format_result(self, needs: Dict[str, str]) -> str:
        """
        格式化输出结果

        Args:
            needs: 提取的需求字典

        Returns:
            str: 格式化的文本
        """
        output = []
        output.append("\n" + "="*70)
        output.append("五大需求提取结果")
        output.append("="*70)

        # 统计信息
        themes_with_needs = [k for k, v in needs.items() if v]

        output.append("\n📊 统计信息：")
        output.append(f"   - 涉及 {len(themes_with_needs)} 个主题")
        if themes_with_needs:
            output.append(f"   - 主题: {', '.join(themes_with_needs)}")

        output.append("\n" + "="*70)
        output.append("详细需求列表")
        output.append("="*70)

        # 按顺序显示五大主题
        for theme in ["融资", "产业", "技术", "人才", "媒体"]:
            output.append(f"\n【{theme}】")
            need_text = needs.get(theme, "")
            if need_text:
                output.append(f"  {need_text}")
            else:
                output.append("  (暂无相关需求)")

        output.append("\n" + "="*70)

        return "\n".join(output)

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
