"""Agent 基类：定义所有 Agent 的通用接口和消息传递机制。"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import Config


@dataclass
class AgentMessage:
    """Agent 之间传递的消息。"""
    sender: str
    receiver: str
    content: str
    message_type: str = "text"  # text / task / feedback / result
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent(ABC):
    """Agent 基类。

    所有具体 Agent（研究员、写手、评审等）都继承此类，
    实现各自的 process 方法。
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """初始化 Agent。

        Args:
            name: Agent 名称
            role: Agent 角色描述
            system_prompt: 系统提示词
            model: 使用的模型
            temperature: 温度参数
        """
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

        self.llm = ChatOpenAI(
            model=model or Config.AGENT_MODEL,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_BASE_URL,
            temperature=temperature if temperature is not None else Config.TEMPERATURE,
        )

        self._message_history: List[AgentMessage] = []
        self._conversation: List = [SystemMessage(content=system_prompt)]

    @abstractmethod
    def process(self, message: AgentMessage) -> AgentMessage:
        """处理输入消息并返回输出消息。

        Args:
            message: 输入消息

        Returns:
            输出消息
        """
        pass

    def _call_llm(self, user_input: str) -> str:
        """调用 LLM 并返回响应文本。

        Args:
            user_input: 用户输入

        Returns:
            LLM 响应文本
        """
        self._conversation.append(HumanMessage(content=user_input))
        response = self.llm.invoke(self._conversation)
        self._conversation.append(AIMessage(content=response.content))
        return response.content

    def _call_llm_with_context(self, system_addition: str, user_input: str) -> str:
        """带额外系统上下文的 LLM 调用。

        Args:
            system_addition: 追加的系统提示
            user_input: 用户输入

        Returns:
            LLM 响应文本
        """
        messages = [
            SystemMessage(content=self.system_prompt + "\n\n" + system_addition),
            HumanMessage(content=user_input),
        ]
        response = self.llm.invoke(messages)
        return response.content

    def receive_message(self, message: AgentMessage) -> None:
        """接收并记录消息。"""
        self._message_history.append(message)

    def get_history(self) -> List[AgentMessage]:
        """获取消息历史。"""
        return self._message_history.copy()

    def reset(self) -> None:
        """重置 Agent 状态。"""
        self._message_history.clear()
        self._conversation = [SystemMessage(content=self.system_prompt)]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name} role={self.role}>"
