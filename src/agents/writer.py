"""写手 Agent：负责根据研究资料撰写文章。

接收研究员的研究笔记，结合写作要求，
生成结构完整、逻辑清晰的文章。
"""

from typing import Optional

from ..agent_base import BaseAgent, AgentMessage


WRITER_SYSTEM_PROMPT = """你是一位专业的内容创作者，擅长将研究资料转化为结构清晰、引人入胜的文章。

## 你的职责
1. 根据研究笔记和写作要求，撰写完整的文章
2. 确保文章结构合理：引言、正文、结论
3. 语言流畅、逻辑清晰、观点明确
4. 合理引用研究资料中的事实和数据

## 写作原则
- 基于提供的研究资料，不要编造未提及的信息
- 文章要有明确的主题和论点
- 段落之间有逻辑过渡
- 语言专业但不晦涩，适合目标读者
- 如果研究资料中有争议，客观呈现不同观点

## 输出格式
输出完整的文章，包含：
- 标题
- 引言（背景和主题引入）
- 正文（分点论述，每段有明确主题）
- 结论（总结和展望）
"""


class WriterAgent(BaseAgent):
    """写手 Agent。"""

    def __init__(self, name: str = "写手", model: Optional[str] = None):
        super().__init__(
            name=name,
            role="内容撰写与文章创作",
            system_prompt=WRITER_SYSTEM_PROMPT,
            model=model,
        )

    def process(self, message: AgentMessage) -> AgentMessage:
        """处理写作任务。

        Args:
            message: 包含研究笔记和写作要求的消息

        Returns:
            包含撰写文章的消息
        """
        topic = message.metadata.get("topic", "未知主题")
        research_notes = message.content

        print(f"✍️ [{self.name}] 开始撰写: {topic}")

        # 构建写作提示
        writing_prompt = f"""请根据以下研究笔记，撰写一篇关于"{topic}"的完整文章。

【研究笔记】
{research_notes}

【写作要求】
- 文章长度约 800-1200 字
- 结构完整：标题、引言、正文（3-4个段落）、结论
- 语言流畅，逻辑清晰
- 基于研究笔记中的信息，不要编造

请输出完整的文章。"""

        # 调用 LLM 撰写文章
        article = self._call_llm(writing_prompt)

        print(f"✅ [{self.name}] 文章完成，长度: {len(article)} 字符")

        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=article,
            message_type="result",
            metadata={"topic": topic, "article_length": len(article)},
        )

    def revise(self, message: AgentMessage) -> AgentMessage:
        """根据评审反馈修改文章。

        Args:
            message: 包含原文和评审反馈的消息

        Returns:
            修改后的文章
        """
        original_article = message.metadata.get("original_article", "")
        feedback = message.content
        topic = message.metadata.get("topic", "未知主题")

        print(f"✍️ [{self.name}] 根据反馈修改文章: {topic}")

        revision_prompt = f"""请根据以下评审反馈，修改这篇关于"{topic}"的文章。

【原始文章】
{original_article}

【评审反馈】
{feedback}

【修改要求】
- 认真对待评审反馈中的每一条建议
- 保留原文中好的部分，改进有问题的部分
- 修改后输出完整的文章
- 如果对反馈有不同看法，可以在文章中合理处理

请输出修改后的完整文章。"""

        revised_article = self._call_llm(revision_prompt)

        print(f"✅ [{self.name}] 修改完成，长度: {len(revised_article)} 字符")

        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=revised_article,
            message_type="result",
            metadata={"topic": topic, "revised": True, "article_length": len(revised_article)},
        )
