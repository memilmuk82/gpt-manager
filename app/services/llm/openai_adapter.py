from app.services.llm.base import BaseLLMAdapter
from app.services.llm.errors import LLMProviderError


class OpenAIAdapter(BaseLLMAdapter):
    provider = "openai"
    label = "OpenAI"

    def list_models(self, api_key: str, timeout: int = 15) -> list[str]:
        payload = self._request_json(
            url="https://api.openai.com/v1/models",
            method="GET",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        models = [item.get("id", "") for item in payload.get("data", []) if isinstance(item, dict)]
        return sorted({model for model in models if model})

    def generate_text(self, *, api_key: str, model: str, messages: list[dict], options: dict | None = None, timeout: int = 30) -> str:
        options = options or {}
        input_text = "\n\n".join(f"{message.get('role', 'user')}: {message.get('content', '')}" for message in messages)
        payload = {
            "model": model,
            "input": input_text,
            "max_output_tokens": int(options.get("max_output_tokens", 900)),
        }
        response = self._request_json(
            url="https://api.openai.com/v1/responses",
            method="POST",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            payload=payload,
            timeout=timeout,
        )
        text = response.get("output_text")
        if isinstance(text, str) and text.strip():
            return text.strip()
        for item in response.get("output", []):
            for content in item.get("content", []):
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    return content["text"].strip()
        raise LLMProviderError(self.provider, None, "OpenAI 응답에 사용할 텍스트가 없습니다.")
