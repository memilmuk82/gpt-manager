import json
import urllib.error
import urllib.request


class GeminiReviewError(RuntimeError):
    pass


def build_review_prompt(source_prompt: str, review_goal: str) -> str:
    return f"""다음 프롬프트를 교사용 AI 활용 관점에서 점검하세요.

점검 목표: {review_goal}

원본 프롬프트:
{source_prompt}

아래 형식으로 한국어로 답하세요.
1. 핵심 문제
2. 개선 방향
3. 개선된 프롬프트
4. 수업/업무 적용 시 주의점
""".strip()


def call_gemini_review(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    timeout: int = 20,
) -> str:
    payload = {
        "model": model,
        "input": prompt,
        "generation_config": {"max_output_tokens": max_output_tokens},
    }
    request = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GeminiReviewError(f"Gemini API 요청이 실패했습니다. ({exc.code}) {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise GeminiReviewError("Gemini API 응답을 처리하지 못했습니다.") from exc

    output_text = _extract_output_text(response_payload)
    if not output_text:
        raise GeminiReviewError("Gemini API 응답에 점검 결과가 없습니다.")
    return output_text


def _extract_output_text(payload: dict) -> str:
    direct_output = payload.get("output_text") or payload.get("outputText")
    if isinstance(direct_output, str):
        return direct_output.strip()

    output = payload.get("output")
    if isinstance(output, str):
        return output.strip()

    for candidate in payload.get("candidates", []):
        parts = candidate.get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
        if text.strip():
            return text.strip()

    for step in payload.get("steps", []):
        text = _extract_step_text(step)
        if text:
            return text

    return ""


def _extract_step_text(step: dict) -> str:
    chunks: list[str] = []
    for key in ("output", "outputs", "content", "contents"):
        value = step.get(key)
        if isinstance(value, str):
            chunks.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    chunks.append(item)
                elif isinstance(item, dict) and isinstance(item.get("text"), str):
                    chunks.append(item["text"])
    return "".join(chunks).strip()
