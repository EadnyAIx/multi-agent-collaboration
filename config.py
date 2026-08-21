"""多 Agent 协作系统配置。"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """全局配置。"""

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    AGENT_MODEL: str = os.getenv("AGENT_MODEL", "gpt-4o-mini")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.4"))

    MAX_REVIEW_ROUNDS: int = int(os.getenv("MAX_REVIEW_ROUNDS", "3"))
    REVIEW_PASS_THRESHOLD: int = int(os.getenv("REVIEW_PASS_THRESHOLD", "7"))

    @classmethod
    def validate(cls) -> None:
        if not cls.OPENAI_API_KEY:
            raise ValueError("未设置 OPENAI_API_KEY，请配置 .env 文件。")
