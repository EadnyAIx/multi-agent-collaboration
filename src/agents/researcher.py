"""研究员 Agent：负责信息搜集和资料整理。

通过网络搜索获取相关信息，整理成结构化的研究笔记，
为写手提供素材和参考资料。
"""

from typing import Optional

from ..agent_base import BaseAgent, AgentMessage


RESEARCHER_SYSTEM_PROMPT = """你是一位专业的研究分析师，擅长信息搜集、资料整理和事实核查。

## 你的职责
1. 根据给定的主题，系统性地搜集相关信息
2. 整理出结构化的研究笔记，包含关键事实、数据、观点
3. 标注信息来源，确保内容的准确性和可信度
4. 识别不同观点之间的争议和共识

## 输出格式
你的研究笔记应包含以下部分：
- **主题概述**: 用2-3句话概括主题
- **关键事实**: 列出3-5个最重要的事实或数据
- **主要观点**: 整理2-3个不同角度的观点
- **争议与讨论**: 指出存在争议或需要进一步探讨的问题
- **参考来源**: 列出信息来源

## 工作原则
- 基于搜索到的真实信息，不要编造
- 客观中立，呈现不同观点
- 简洁明了，突出重点
- 如果信息不足，明确指出需要进一步研究的方向
"""


class ResearcherAgent(BaseAgent):
    """研究员 Agent。"""

    def __init__(self, name: str = "研究员", model: Optional[str] = None):
        super().__init__(
            name=name,
            role="信息搜集与资料整理",
            system_prompt=RESEARCHER_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, message: AgentMessage) -> AgentMessage:
        """处理研究任务。

        Args:
            message: 包含研究主题的消息

        Returns:
            包含研究笔记的消息
        """
        topic = message.content
        print(f"🔍 [{self.name}] 开始研究: {topic}")

        # 执行网络搜索
        search_results = self._search(topic)

        # 构建研究提示
        research_prompt = f"""请基于以下搜索结果，撰写关于"{topic}"的研究笔记。

【搜索结果】
{search_results}

请按照系统提示中的格式输出研究笔记。"""

        # 调用 LLM 生成研究笔记
        research_notes = self._call_llm(research_prompt)

        print(f"✅ [{self.name}] 研究完成，笔记长度: {len(research_notes)} 字符")

        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=research_notes,
            message_type="result",
            metadata={"topic": topic, "search_results_count": search_results.count("\n\n") + 1},
        )

    def _search(self, query: str, max_results: int = 5) -> str:
        """执行网络搜索。

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            格式化的搜索结果
        """
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            if not results:
                return f"未找到与 '{query}' 相关的搜索结果。"

            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(
                    f"[{i}] {r['title']}\n"
                    f"来源: {r['href']}\n"
                    f"摘要: {r['body']}\n"
                )
            return "\n".join(formatted)

        except ImportError:
            return (
                "注意: duckduckgo-search 未安装，无法进行网络搜索。"
                "请基于你的已有知识进行研究，并在笔记中标注需要验证的信息。"
            )
        except Exception as e:
            return f"搜索出错: {e}，请基于已有知识进行研究。"
