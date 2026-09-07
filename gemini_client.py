import os

from dotenv import load_dotenv
from google import genai


# ========================================
# 환경 변수 불러오기
# ========================================

load_dotenv()


# ========================================
# Gemini API 키 확인
# ========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY가 설정되지 않았습니다. "
        ".env 파일을 확인해주세요."
    )


# ========================================
# Gemini 클라이언트 생성
# ========================================

client = genai.Client(api_key=api_key)


# ========================================
# Gemini에게 질문 보내기
# ========================================

def ask_gemini(prompt):
    """
    Gemini API에 프롬프트를 전달하고
    자연어 응답을 반환한다.

    서버 오류나 네트워크 오류가 발생하면
    프로그램이 중단되지 않도록 안내 문구를 반환한다.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        error_message = str(e)

        # Gemini 서버 일시적 오류
        if "503" in error_message or "UNAVAILABLE" in error_message:
            return (
                "AI 분석 서버가 일시적으로 응답하지 않습니다. "
                "잠시 후 다시 시도해주세요."
            )

        # 요청이 많은 경우
        if "429" in error_message:
            return (
                "AI 요청이 일시적으로 많습니다. "
                "잠시 후 다시 시도해주세요."
            )

        # 그 외 오류
        return (
            "AI 분석 중 오류가 발생했습니다. "
            "잠시 후 다시 시도해주세요."
        )