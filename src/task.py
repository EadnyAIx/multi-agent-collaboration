"""任务定义与结果管理。"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """任务状态。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVISION = "needs_revision"


@dataclass
class Task:
    """协作任务定义。"""
    id: str
    title: str
    description: str
    assigned_to: str  # Agent 名称
    depends_on: List[str] = field(default_factory=list)  # 依赖的任务 ID
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TaskResult:
    """任务执行结果。"""
    task_id: str
    agent_name: str
    status: TaskStatus
    output: str
    feedback: Optional[str] = None
    score: Optional[int] = None  # 评审分数 1-10
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CollaborationResult:
    """整个协作流程的最终结果。"""
    topic: str
    final_output: str
    tasks: List[TaskResult] = field(default_factory=list)
    review_rounds: int = 0
    total_time: float = 0.0
    success: bool = True
