from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol


class ChineseLLM(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass(slots=True)
class LlmSettings:
    api_key: str | None
    base_url: str
    model_name: str

    @classmethod
    def from_env(cls) -> "LlmSettings":
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model_name=os.getenv("MODEL_NAME", "gpt-4.1-mini"),
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


class RuleBasedChineseLLM:
    def generate(self, prompt: str) -> str:
        return (
            "中文研究写作引擎已接收任务。"
            f"输入要点：{prompt[:240]}"
            "。在未配置真实模型时，系统会使用规则化中文输出保证演示链路可运行。"
        )


class OpenAICompatibleLLM:
    def __init__(self, settings: LlmSettings) -> None:
        self.settings = settings

    def generate(self, prompt: str) -> str:
        try:
            from langchain.chat_models import init_chat_model
        except ImportError as error:
            raise RuntimeError("langchain is required for OpenAI-compatible LLM calls.") from error

        model = init_chat_model(
            self.settings.model_name,
            model_provider="openai",
            api_key=self.settings.api_key,
            base_url=self.settings.base_url,
        )
        response = model.invoke(prompt)
        return str(response.content)


def build_llm(settings: LlmSettings | None = None) -> ChineseLLM:
    resolved = settings or LlmSettings.from_env()
    if not resolved.is_configured:
        return RuleBasedChineseLLM()
    return OpenAICompatibleLLM(resolved)
