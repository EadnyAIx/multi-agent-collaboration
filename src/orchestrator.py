"""协作编排器：管理多 Agent 之间的任务流转和协作流程。

实现研究员→写手→评审员的流水线协作，
支持评审反馈循环，直到文章通过评审或达到最大轮次。
"""

import time
from typing import List, Optional, Dict, Any

from config import Config
from .agent_base import AgentMessage
from .task import Task, TaskResult, TaskStatus, CollaborationResult
from .agents.researcher import ResearcherAgent
from .agents.writer import WriterAgent
from .agents.reviewer import ReviewerAgent


class Orchestrator:
    """多 Agent 协作编排器。

    管理研究员、写手、评审员三个 Agent 的协作流程：
    1. 研究员搜集资料
    2. 写手撰写文章
    3. 评审员评审质量
    4. 如未通过，返回写手修改（循环）
    """

    def __init__(
        self,
        max_review_rounds: Optional[int] = None,
        pass_threshold: Optional[int] = None,
        verbose: bool = True,
    ):
        """初始化编排器。

        Args:
            max_review_rounds: 最大评审修改轮次
            pass_threshold: 通过评审的分数阈值
            verbose: 是否打印过程
        """
        Config.validate()

        self.max_review_rounds = max_review_rounds or Config.MAX_REVIEW_ROUNDS
        self.pass_threshold = pass_threshold or Config.REVIEW_PASS_THRESHOLD
        self.verbose = verbose

        # 初始化三个 Agent
        self.researcher = ResearcherAgent()
        self.writer = WriterAgent()
        self.reviewer = ReviewerAgent(pass_threshold=self.pass_threshold)

        self._task_results: List[TaskResult] = []

    def run(self, topic: str) -> CollaborationResult:
        """执行完整的协作流程。

        Args:
            topic: 研究/写作主题

        Returns:
            协作结果
        """
        start_time = time.time()

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🚀 开始多 Agent 协作: {topic}")
            print(f"{'='*60}")

        # ===== 阶段1: 研究员搜集资料 =====
        if self.verbose:
            print(f"\n📌 阶段 1/3: 研究员搜集资料")

        research_msg = self.researcher.process(
            AgentMessage(sender="orchestrator", receiver=self.researcher.name, content=topic)
        )
        self.researcher.receive_message(research_msg)

        self._task_results.append(TaskResult(
            task_id="research",
            agent_name=self.researcher.name,
            status=TaskStatus.COMPLETED,
            output=research_msg.content,
            metadata={"topic": topic},
        ))

        # ===== 阶段2: 写手撰写文章 =====
        if self.verbose:
            print(f"\n📌 阶段 2/3: 写手撰写文章")

        write_msg = self.writer.process(
            AgentMessage(
                sender="orchestrator",
                receiver=self.writer.name,
                content=research_msg.content,
                metadata={"topic": topic},
            )
        )
        self.writer.receive_message(write_msg)

        current_article = write_msg.content

        self._task_results.append(TaskResult(
            task_id="write",
            agent_name=self.writer.name,
            status=TaskStatus.COMPLETED,
            output=current_article,
            metadata={"topic": topic},
        ))

        # ===== 阶段3: 评审-修改循环 =====
        if self.verbose:
            print(f"\n📌 阶段 3/3: 评审与修改循环")

        review_round = 0
        final_score = 0
        passed = False

        for review_round in range(1, self.max_review_rounds + 1):
            if self.verbose:
                print(f"\n--- 评审轮次 {review_round}/{self.max_review_rounds} ---")

            # 评审员评审
            review_msg = self.reviewer.process(
                AgentMessage(
                    sender="orchestrator",
                    receiver=self.reviewer.name,
                    content=current_article,
                    metadata={"topic": topic},
                )
            )
            self.reviewer.receive_message(review_msg)

            score = review_msg.metadata.get("score", 5)
            round_passed = review_msg.metadata.get("passed", False)
            final_score = score

            self._task_results.append(TaskResult(
                task_id=f"review_round_{review_round}",
                agent_name=self.reviewer.name,
                status=TaskStatus.COMPLETED if round_passed else TaskStatus.NEEDS_REVISION,
                output=review_msg.content,
                score=score,
                metadata={"topic": topic, "round": review_round},
            ))

            if round_passed:
                if self.verbose:
                    print(f"\n✅ 文章通过评审！评分: {score}/10")
                passed = True
                break

            if self.verbose:
                print(f"\n⚠️ 文章未通过评审 (评分: {score}/10)，返回修改...")

            # 写手根据反馈修改
            revise_msg = self.writer.revise(
                AgentMessage(
                    sender="orchestrator",
                    receiver=self.writer.name,
                    content=review_msg.content,
                    metadata={
                        "topic": topic,
                        "original_article": current_article,
                    },
                )
            )
            self.writer.receive_message(revise_msg)
            current_article = revise_msg.content

            self._task_results.append(TaskResult(
                task_id=f"revise_round_{review_round}",
                agent_name=self.writer.name,
                status=TaskStatus.COMPLETED,
                output=current_article,
                metadata={"topic": topic, "round": review_round},
            ))

        # ===== 汇总结果 =====
        total_time = time.time() - start_time

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"🏁 协作完成")
            print(f"   主题: {topic}")
            print(f"   评审轮次: {review_round}")
            print(f"   最终评分: {final_score}/10")
            print(f"   是否通过: {'是' if passed else '否（达到最大轮次）'}")
            print(f"   总耗时: {total_time:.1f} 秒")
            print(f"{'='*60}")

        return CollaborationResult(
            topic=topic,
            final_output=current_article,
            tasks=self._task_results.copy(),
            review_rounds=review_round,
            total_time=total_time,
            success=passed,
        )

    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有 Agent 的状态信息。"""
        return {
            "researcher": {
                "name": self.researcher.name,
                "role": self.researcher.role,
                "messages": len(self.researcher.get_history()),
            },
            "writer": {
                "name": self.writer.name,
                "role": self.writer.role,
                "messages": len(self.writer.get_history()),
            },
            "reviewer": {
                "name": self.reviewer.name,
                "role": self.reviewer.role,
                "messages": len(self.reviewer.get_history()),
            },
        }

    def reset(self) -> None:
        """重置所有 Agent 和任务结果。"""
        self.researcher.reset()
        self.writer.reset()
        self.reviewer.reset()
        self._task_results.clear()
