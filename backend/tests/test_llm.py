from app.llm import LlmSettings, OpenAICompatibleLLM, RuleBasedChineseLLM, build_llm


def test_build_llm_falls_back_to_rule_based_when_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    llm = build_llm()

    assert isinstance(llm, RuleBasedChineseLLM)


def test_rule_based_llm_returns_chinese_text() -> None:
    llm = RuleBasedChineseLLM()

    text = llm.generate("请总结研究证据")

    assert "中文" in text
    assert "请总结研究证据" in text


def test_llm_settings_read_openai_compatible_environment(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-model-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("MODEL_NAME", "demo-model")

    settings = LlmSettings.from_env()

    assert settings.api_key == "test-model-key"
    assert settings.base_url == "https://example.com/v1"
    assert settings.model_name == "demo-model"


def test_openai_compatible_llm_uses_langchain_init_chat_model(monkeypatch) -> None:
    calls = {}

    class FakeModel:
        def invoke(self, prompt: str):
            calls["prompt"] = prompt

            class Response:
                content = "模型返回中文研究摘要"

            return Response()

    def fake_init_chat_model(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return FakeModel()

    monkeypatch.setattr("langchain.chat_models.init_chat_model", fake_init_chat_model)
    llm = OpenAICompatibleLLM(
        LlmSettings(
            api_key="fake-key",
            base_url="https://example.com/v1",
            model_name="demo-model",
        )
    )

    assert llm.generate("生成摘要") == "模型返回中文研究摘要"
    assert calls["args"] == ("demo-model",)
    assert calls["kwargs"]["api_key"] == "fake-key"
