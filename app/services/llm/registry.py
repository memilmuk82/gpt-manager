from app.services.llm.anthropic_adapter import AnthropicAdapter
from app.services.llm.base import ProviderDefinition
from app.services.llm.gemini_adapter import GeminiAdapter
from app.services.llm.openai_adapter import OpenAIAdapter


PROVIDER_DEFINITIONS = {
    "openai": ProviderDefinition(
        key="openai",
        label="OpenAI",
        default_model="gpt-5.5",
        recommended_models=("gpt-5.5", "gpt-5.5-mini", "gpt-5.4-mini"),
    ),
    "gemini": ProviderDefinition(
        key="gemini",
        label="Google Gemini",
        default_model="gemini-3.1-flash-lite",
        recommended_models=("gemini-3.1-flash-lite", "gemini-3.1-flash", "gemini-3.1-pro"),
    ),
    "anthropic": ProviderDefinition(
        key="anthropic",
        label="Anthropic Claude",
        default_model="claude-sonnet-4-6",
        recommended_models=("claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"),
    ),
}

_ADAPTERS = {
    "openai": OpenAIAdapter(),
    "gemini": GeminiAdapter(),
    "anthropic": AnthropicAdapter(),
}


def provider_choices() -> list[ProviderDefinition]:
    return [PROVIDER_DEFINITIONS[key] for key in ("openai", "gemini", "anthropic")]


def get_adapter(provider: str):
    normalized = normalize_provider(provider)
    return _ADAPTERS[normalized]


def normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized not in PROVIDER_DEFINITIONS:
        raise ValueError("지원하지 않는 AI Provider입니다.")
    return normalized


def recommended_models(provider: str) -> list[str]:
    return list(PROVIDER_DEFINITIONS[normalize_provider(provider)].recommended_models)


def default_model(provider: str) -> str:
    return PROVIDER_DEFINITIONS[normalize_provider(provider)].default_model


def list_models_with_fallback(provider: str, api_key: str | None = None) -> tuple[list[str], bool, str]:
    normalized = normalize_provider(provider)
    fallback = recommended_models(normalized)
    if not api_key:
        return fallback, False, "API Key가 없어 기본 추천 모델 목록을 표시합니다."
    try:
        models = get_adapter(normalized).list_models(api_key)
    except Exception:
        return fallback, False, "모델 목록 조회에 실패해 기본 추천 모델 목록을 표시합니다."
    return (models or fallback), bool(models), "모델 목록을 새로고침했습니다." if models else "조회 결과가 없어 기본 추천 모델 목록을 표시합니다."


def test_provider_connection(provider: str, api_key: str, model: str) -> str:
    normalized = normalize_provider(provider)
    return get_adapter(normalized).generate_text(
        api_key=api_key,
        model=model or default_model(normalized),
        messages=[{"role": "user", "content": "안녕하세요. 한 문장으로 답하세요."}],
        options={"max_output_tokens": 80},
        timeout=20,
    )
