class LLMProviderError(RuntimeError):
    def __init__(self, provider: str, status_code: int | None, message: str):
        self.provider = provider
        self.status_code = status_code
        super().__init__(message)


def provider_error_message(provider_label: str, status_code: int | None) -> str:
    if status_code == 401:
        return f"{provider_label} API Key가 잘못되었거나 만료되었습니다."
    if status_code == 403:
        return f"{provider_label} 권한, 결제, 지역 또는 프로젝트 설정을 확인하세요."
    if status_code == 404:
        return f"{provider_label} 모델명이 존재하지 않습니다. 모델 목록을 새로고침하세요."
    if status_code == 429:
        return f"{provider_label} 사용량 한도 초과 또는 속도 제한 상태입니다."
    if status_code and 500 <= status_code < 600:
        return f"{provider_label} 서버 오류입니다. 잠시 후 다시 시도하세요."
    return f"{provider_label} 네트워크 또는 알 수 없는 오류가 발생했습니다."
