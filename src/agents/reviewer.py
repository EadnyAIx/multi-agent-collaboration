"""评审员 Agent：负责文章质量评审和反馈。

从内容准确性、结构完整性、语言表达等维度评审文章，
给出评分和具体修改建议。
"""

import re
from typing import Optional, Tuple

from ..agent_base import BaseAgent, AgentMessage


REVIEWER_SYSTEM_PROMPT = """你是一位严格的专业编辑和质量评审员，擅长从多个维度评估文章质量。

## 你的职责
1. 从多个维度评审文章质量
2. 给出具体的评分和修改建议
3. 指出文章中的事实错误、逻辑漏洞、表达问题
4. 决定文章是否通过评审，或需要修改

## 评审维度
1. **内容质量** (权重 30%): 事实准确性、信息完整性、观点深度
2. **结构逻辑** (权重 25%): 结构完整性、段落衔接、论证逻辑
3. **语言表达** (权重 20%): 语言流畅度、用词准确性、文风一致性
4. **原创性** (权重 15%): 观点独特性、分析深度
5. **规范性** (权重 10%): 格式规范、引用标注

## 输出格式
严格按照以下格式输出评审结果：

```
评分: X/10

【评审意见】
1. 内容质量: [评价]
2. 结构逻辑: [评价]
3. 语言表达: [评价]
4. 原创性: [评价]
5. 规范性: [评价]

【具体修改建议】
1. [具体建议1]
2. [具体建议2]
3. [具体建议3]

【评审结论】
通过 / 需要修改
```

## 评审标准
- 9-10分: 优秀，几乎无需修改
- 7-8分: 良好，少量修改即可通过
- 5-6分: 一般，需要较多修改
- 3-4分: 较差，需要大幅修改
- 1-2分: 不合格，需要重写

评分 >= 7 分为通过，否则需要修改。
"""


class ReviewerAgent(BaseAgent):
    """评审员 Agent。"""

    def __init__(
        self,
        name: str = "评审员",
        pass_threshold: int = 7,
        model: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            role="质量评审与反馈",
            system_prompt=REVIEWER_SYSTEM_PROMPT,
            model=model,
        )
        self.pass_threshold = pass_threshold

    def process(self, message: AgentMessage) -> AgentMessage:
        """评审文章。

        Args:
            message: 包含待评审文章的消息

        Returns:
            包含评审结果的消息
        """
        article = message.content
        topic = message.metadata.get("topic", "未知主题")

        print(f"🔍 [{self.name}] 开始评审: {topic}")

        review_prompt = f"""请评审以下关于"{topic}"的文章。

【待评审文章】
{article}

请按照系统提示中的格式输出评审结果。"""

        review_result = self._call_llm(review_prompt)

        # 解析评分和结论
        score, passed = self._parse_review(review_result)

        print(f"📊 [{self.name}] 评审完成: 评分 {score}/10, {'通过' if passed else '需要修改'}")

        return AgentMessage(
            sender=self.name,
            receiver=message.sender,
            content=review_result,
            message_type="feedback",
            metadata={
                "topic": topic,
                "score": score,
                "passed": passed,
            },
        )

    def _parse_review(self, review_text: str) -> Tuple[int, bool]:
        """解析评审结果中的评分和结论。

        Args:
            review_text: 评审文本

        Returns:
            (评分, 是否通过)
        """
        # 提取评分
        score_match = re.search(r"评分[:：]\s*(\d+)(?:\s*/\s*10)?", review_text)
        score = int(score_match.group(1)) if score_match else 5

        # 判断是否通过
        passed = score >= self.pass_threshold

        # 也检查明确的结论
        if "需要修改" in review_text or "不通过" in review_text:
            passed = False
        if "通过" in review_text and "需要修改" not in review_text:
            passed = True

        return score, passed
