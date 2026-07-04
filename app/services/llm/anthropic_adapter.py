from app.services.llm.base import BaseLLMAdapter
from app.services.llm.errors import LLMProviderError


class AnthropicAdapter(BaseLLMAdapter):
    provider = "anthropic"
    label = "Anthropic Claude"
    api_version = "2023-06-01"

    def list_models(self, api_key: str, timeout: int = 15) -> list[str]:
        payload = self._request_json(
            url="https://api.anthropic.com/v1/models",
            method="GET",
            headers={"x-api-key": api_key, "anthropic-version": self.api_version},
            timeout=timeout,
        )
        models = [item.get("id", "") for item in payload.get("data", []) if isinstance(item, dict)]
        return sorted({model for model in models if model})

    def generate_text(self, *, api_key: str, model: str, messages: list[dict], options: dict | None = None, timeout: int = 30) -> str:
        options = options or {}
        system = "\n\n".join(message.get("content", "") for message in messages if message.get("role") == "system")
        user_messages = [
            {"role": "user", "content": message.get("content", "")}
            for message in messages
            if message.get("role") != "system"
        ]
        payload = {
            "model": model,
            "max_tokens": int(options.get("max_output_tokens", 900)),
            "messages": user_messages or [{"role": "user", "content": ""}],
        }
        if system:
            payload["system"] = system
        response = self._request_json(
            url="https://api.anthropic.com/v1/messages",
            method="POST",
            headers={"x-api-key": api_key, "anthropic-version": self.api_version, "Content-Type": "application/json"},
            payload=payload,
            timeout=timeout,
        )
        chunks = [item.get("text", "") for item in response.get("content", []) if isinstance(item, dict)]
        text = "".join(chunks).strip()
        if text:
            return text
        raise LLMProviderError(self.provider, None, "Anthropic Claude 응답에 사용할 텍스트가 없습니다.")
