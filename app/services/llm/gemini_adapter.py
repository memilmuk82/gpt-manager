from urllib.parse import quote

from app.services.llm.base import BaseLLMAdapter
from app.services.llm.errors import LLMProviderError


class GeminiAdapter(BaseLLMAdapter):
    provider = "gemini"
    label = "Google Gemini"

    def list_models(self, api_key: str, timeout: int = 15) -> list[str]:
        payload = self._request_json(
            url=f"https://generativelanguage.googleapis.com/v1beta/models?key={quote(api_key)}",
            method="GET",
            headers={},
            timeout=timeout,
        )
        models = []
        for item in payload.get("models", []):
            name = item.get("name", "") if isinstance(item, dict) else ""
            if name.startswith("models/"):
                models.append(name.removeprefix("models/"))
        return sorted({model for model in models if model})

    def generate_text(self, *, api_key: str, model: str, messages: list[dict], options: dict | None = None, timeout: int = 30) -> str:
        options = options or {}
        text = "\n\n".join(message.get("content", "") for message in messages)
        payload = {
            "contents": [{"role": "user", "parts": [{"text": text}]}],
            "generationConfig": {"maxOutputTokens": int(options.get("max_output_tokens", 900))},
        }
        response = self._request_json(
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model)}:generateContent?key={quote(api_key)}",
            method="POST",
            headers={"Content-Type": "application/json"},
            payload=payload,
            timeout=timeout,
        )
        for candidate in response.get("candidates", []):
            parts = candidate.get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
            if text.strip():
                return text.strip()
        raise LLMProviderError(self.provider, None, "Google Gemini 응답에 사용할 텍스트가 없습니다.")
