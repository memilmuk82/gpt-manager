import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from app.services.llm.errors import LLMProviderError, provider_error_message


@dataclass(frozen=True)
class ProviderDefinition:
    key: str
    label: str
    default_model: str
    recommended_models: tuple[str, ...]


class BaseLLMAdapter:
    provider: str
    label: str

    def list_models(self, api_key: str, timeout: int = 15) -> list[str]:
        raise NotImplementedError

    def generate_text(
        self,
        *,
        api_key: str,
        model: str,
        messages: list[dict],
        options: dict | None = None,
        timeout: int = 30,
    ) -> str:
        raise NotImplementedError

    def _request_json(
        self,
        *,
        url: str,
        method: str,
        headers: dict[str, str],
        payload: dict | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            # Provider error bodies can contain request details. Do not forward them to UI or logs.
            raise LLMProviderError(self.provider, exc.code, provider_error_message(self.label, exc.code)) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise LLMProviderError(self.provider, None, provider_error_message(self.label, None)) from exc
