from analysis.tourism_analysis import (
    get_region_status,
    compare_regions,
    analyze_seasonality,
    analyze_changes,
    recommend_promotion_period
)

from gemini_client import ask_gemini


# ========================================
# 지역 목록
# ========================================

REGIONS = [
    "강원", "경기", "경남", "경북",
    "광주", "대구", "대전", "부산",
    "서울", "세종", "울산", "인천",
    "전남", "전북", "제주", "충남", "충북"
]


# ========================================
# 질문에서 지역 찾기
# ========================================

def find_regions(question):
    found_regions = []

    for name in REGIONS:
        if name in question:
            found_regions.append(name)

    return found_regions


# ========================================
# 질문 유형 판단
# ========================================

def classify_question(question, found_regions):
    """
    사용자의 자연어 질문을 분석해서
    어떤 관광 분석 기능을 사용할지 판단한다.
    """

    # ----------------------------------------
    # 1. 지역 비교
    # ----------------------------------------

    if len(found_regions) >= 2:
        return "compare"

    # ----------------------------------------
    # 2. 지역이 없으면 분석 불가
    # ----------------------------------------

    if len(found_regions) == 0:
        return "unknown"

    # ----------------------------------------
    # 3. 관광객 증감 분석
    # ----------------------------------------
    # "가장 많이 증가한 달", "관광객이 줄어든 시기"
    # 같은 질문은 시기 분석보다 먼저 처리한다.

    change_keywords = [
        "증가",
        "감소",
        "늘어난",
        "줄어든",
        "상승",
        "하락",
        "증감",
        "변화"
    ]

    if any(keyword in question for keyword in change_keywords):
        return "changes"

    # ----------------------------------------
    # 4. 홍보 / 추천 분석
    # ----------------------------------------

    promotion_keywords = [
        "홍보",
        "추천",
        "활성화",
        "마케팅",
        "알리",
        "홍보하기",
        "홍보해야",
        "어떻게 홍보"
    ]

    if any(keyword in question for keyword in promotion_keywords):
        return "promotion"

    # ----------------------------------------
    # 5. 최근 관광 현황
    # ----------------------------------------
    # "어때" 같은 표현을 포함한 현황 질문을
    # 시기 질문보다 먼저 처리한다.

    status_keywords = [
        "최근",
        "현재",
        "요즘",
        "현황",
        "상황",
        "관광객 수",
        "방문자 수",
        "방문객 수",
        "관광객이 얼마나",
        "방문자가 얼마나",
        "관광객 규모",
        "관광 규모",
        "추이",
        "알려줘",
        "알려주세요",
        "어때",
        "어떤가",
        "어떤지"
    ]

    if any(keyword in question for keyword in status_keywords):
        return "status"

    # ----------------------------------------
    # 6. 관광 시기 / 계절 분석
    # ----------------------------------------
    # "때"처럼 너무 짧은 단어는 사용하지 않는다.
    # "언제", "몇 월", "어느 달" 등의 표현을 사용한다.

    season_keywords = [
        "언제",
        "몇 월",
        "몇월",
        "어느 달",
        "어느달",
        "시기",
        "많은 시기",
        "많이 찾는",
        "많이 방문",
        "제일 많",
        "가장 많은 달"
    ]

    if any(keyword in question for keyword in season_keywords):
        return "seasonality"

    return "unknown"

# ========================================
# 최근 관광 현황
# ========================================

def run_status(region):

    result = get_region_status(region)

    print("\n=== 지역 관광 현황 ===")
    print(f"지역: {region}")
    print(f"최근 기준월: {result['최근 기준월']}")
    print(f"최근 방문자수: {result['최근 방문자수']:,.0f}명")
    print(f"최근 증감률: {result['최근 증감률']:.1f}%")
    print(f"최근 추세: {result['최근 추세']}")

    prompt = f"""
당신은 지역 관광 담당자를 지원하는 AI 비서입니다.

다음은 {region}의 관광 데이터 분석 결과입니다.

- 최근 기준월: {result['최근 기준월']}
- 최근 방문자수: {result['최근 방문자수']:,.0f}명
- 최근 증감률: {result['최근 증감률']:.1f}%
- 최근 추세: {result['최근 추세']}
- 전체 기간 평균 증감률: {result['평균 증감률']:.2f}%
- 증가 월수: {result['증가 월수']}개월
- 감소 월수: {result['감소 월수']}개월

이 데이터를 바탕으로 관광 담당자가 이해하기 쉽게 2~3문장으로 설명해주세요.

주의사항:
1. 제공된 데이터에 없는 사실은 추측하지 마세요.
2. 숫자를 임의로 계산하거나 변경하지 마세요.
3. 데이터에서 확인되는 사실을 중심으로 설명하세요.
4. 마지막에 관광 담당자가 참고할 수 있는 간단한 시사점을 한 문장으로 덧붙여주세요.
"""

    gemini_answer = ask_gemini(prompt)

    print("\n=== AI 분석 ===")
    print(gemini_answer)


# ========================================
# 지역 비교
# ========================================

def run_compare(region1, region2):

    result = compare_regions(region1, region2)

    data1 = result[region1]
    data2 = result[region2]

    print("\n=== 지역 관광 비교 ===")

    print(f"\n[{region1}]")
    print(f"최근 기준월: {data1['최근 기준월']}")
    print(f"최근 방문자수: {data1['최근 방문자수']:,.0f}명")
    print(f"최근 증감률: {data1['최근 증감률']:.1f}%")
    print(f"평균 방문자수: {data1['평균 방문자수']:,.0f}명")
    print(f"평균 증감률: {data1['평균 증감률']:.2f}%")

    print(f"\n[{region2}]")
    print(f"최근 기준월: {data2['최근 기준월']}")
    print(f"최근 방문자수: {data2['최근 방문자수']:,.0f}명")
    print(f"최근 증감률: {data2['최근 증감률']:.1f}%")
    print(f"평균 방문자수: {data2['평균 방문자수']:,.0f}명")
    print(f"평균 증감률: {data2['평균 증감률']:.2f}%")

    if data1["최근 방문자수"] > data2["최근 방문자수"]:
        higher_region = region1
    else:
        higher_region = region2

    print(f"\n최근 관광객 수가 더 많은 지역: {higher_region}")

    prompt = f"""
당신은 지역 관광 담당자를 지원하는 AI 비서입니다.

다음은 {region1}과 {region2}의 관광 데이터 비교 결과입니다.

[{region1}]
- 최근 기준월: {data1['최근 기준월']}
- 최근 방문자수: {data1['최근 방문자수']:,.0f}명
- 최근 증감률: {data1['최근 증감률']:.1f}%
- 평균 방문자수: {data1['평균 방문자수']:,.0f}명
- 평균 증감률: {data1['평균 증감률']:.2f}%

[{region2}]
- 최근 기준월: {data2['최근 기준월']}
- 최근 방문자수: {data2['최근 방문자수']:,.0f}명
- 최근 증감률: {data2['최근 증감률']:.1f}%
- 평균 방문자수: {data2['평균 방문자수']:,.0f}명
- 평균 증감률: {data2['평균 증감률']:.2f}%

위 데이터를 바탕으로 두 지역의 관광 현황을 비교해서 관광 담당자가 이해하기 쉽게 3~4문장으로 설명해주세요.

반드시 다음 내용을 포함해주세요.
1. 최근 방문자 수가 더 많은 지역
2. 두 지역의 최근 증감률 비교
3. 두 지역의 평균 방문자 수 또는 평균 증감률 비교
4. 마지막에 관광 담당자가 참고할 수 있는 간단한 시사점

주의사항:
1. 제공된 데이터에 없는 사실은 추측하지 마세요.
2. 숫자를 임의로 계산하거나 변경하지 마세요.
3. 관광객 수가 많다는 사실만으로 해당 지역이 더 우수하다고 단정하지 마세요.
4. 데이터에서 확인되는 사실을 중심으로 설명하세요.
"""

    gemini_answer = ask_gemini(prompt)

    print("\n=== AI 비교 분석 ===")
    print(gemini_answer)


# ========================================
# 관광 시기 분석
# ========================================

def run_seasonality(region):

    result = analyze_seasonality(region)

    print("\n=== 관광 시기 분석 ===")
    print(f"지역: {region}")

    print(
        f"관광객이 가장 많은 월: "
        f"{result['최다 방문 월']}월"
    )

    print(
        f"해당 월 평균 방문자수: "
        f"{result['최다 방문 월 평균']:,.0f}명"
    )

    print(
        f"관광객이 가장 적은 월: "
        f"{result['최소 방문 월']}월"
    )

    print(
        f"해당 월 평균 방문자수: "
        f"{result['최소 방문 월 평균']:,.0f}명"
    )

    print("\n월별 평균 방문자수:")

    for month, visitors in result[
        "월별 평균 방문자수"
    ].items():

        print(
            f"{month}월: "
            f"{visitors:,.0f}명"
        )

    monthly_data = "\n".join(
        f"- {month}월: {visitors:,.0f}명"
        for month, visitors in result[
            "월별 평균 방문자수"
        ].items()
    )

    prompt = f"""
당신은 지역 관광 담당자를 지원하는 AI 비서입니다.

다음은 {region}의 2023~2025년 관광 데이터를 바탕으로 분석한 월별 관광 패턴입니다.

[주요 결과]
- 관광객이 가장 많은 월: {result['최다 방문 월']}월
- 해당 월 평균 방문자수: {result['최다 방문 월 평균']:,.0f}명
- 관광객이 가장 적은 월: {result['최소 방문 월']}월
- 해당 월 평균 방문자수: {result['최소 방문 월 평균']:,.0f}명

[월별 평균 방문자수]
{monthly_data}

위 데이터를 바탕으로 {region}의 관광 시기 특징을 관광 담당자가 이해하기 쉽게 3~4문장으로 설명해주세요.

설명에는 다음 내용을 포함해주세요.
1. 관광객이 가장 많은 시기
2. 관광객이 가장 적은 시기
3. 월별 데이터를 통해 확인되는 전반적인 계절적 특징
4. 관광 홍보 계획에 참고할 수 있는 간단한 시사점

주의사항:
1. 제공된 데이터에 없는 사실은 추측하지 마세요.
2. 숫자를 임의로 계산하거나 변경하지 마세요.
3. 특정 월의 방문자 수가 많은 원인을 추측하지 마세요.
4. 날씨, 축제, 휴가철 등의 원인을 데이터만으로 단정하지 마세요.
5. 데이터에서 확인되는 관광객 규모와 월별 패턴을 중심으로 설명하세요.
"""

    gemini_answer = ask_gemini(prompt)

    print("\n=== AI 시기 분석 ===")
    print(gemini_answer)


# ========================================
# 관광객 증감 분석
# ========================================

def run_changes(region):

    result = analyze_changes(region)

    print("\n=== 관광객 증감 분석 ===")
    print(f"지역: {region}")

    print(
        f"가장 많이 증가한 달: "
        f"{result['최대 증가 월']} "
        f"({result['최대 증가율']:.1f}%)"
    )

    print(
        f"당시 방문자수: "
        f"{result['최대 증가 방문자수']:,.0f}명"
    )

    print(
        f"가장 많이 감소한 달: "
        f"{result['최대 감소 월']} "
        f"({result['최대 감소율']:.1f}%)"
    )

    print(
        f"당시 방문자수: "
        f"{result['최대 감소 방문자수']:,.0f}명"
    )

    print(f"증가 월수: {result['증가 월수']}개월")
    print(f"감소 월수: {result['감소 월수']}개월")

    prompt = f"""
당신은 지역 관광 담당자를 지원하는 AI 비서입니다.

다음은 {region}의 관광객 증감 분석 결과입니다.

- 가장 많이 증가한 달: {result['최대 증가 월']}
- 해당 월 증가율: {result['최대 증가율']:.1f}%
- 해당 월 방문자수: {result['최대 증가 방문자수']:,.0f}명

- 가장 많이 감소한 달: {result['최대 감소 월']}
- 해당 월 감소율: {result['최대 감소율']:.1f}%
- 해당 월 방문자수: {result['최대 감소 방문자수']:,.0f}명

- 증가한 월수: {result['증가 월수']}개월
- 감소한 월수: {result['감소 월수']}개월

위 데이터를 바탕으로 {region}의 관광객 증감 흐름을 관광 담당자가 이해하기 쉽게 3~4문장으로 설명해주세요.

반드시 다음 내용을 포함해주세요.
1. 관광객이 가장 많이 증가한 시기와 증가율
2. 관광객이 가장 많이 감소한 시기와 감소율
3. 전체적으로 증가한 달과 감소한 달의 흐름
4. 관광 담당자가 향후 관광 정책이나 홍보 계획을 세울 때 참고할 수 있는 간단한 시사점

주의사항:
1. 제공된 데이터에 없는 사실은 추측하지 마세요.
2. 숫자를 임의로 계산하거나 변경하지 마세요.
3. 특정 시기에 관광객이 증가하거나 감소한 원인을 추측하지 마세요.
4. 데이터에서 확인되는 증감 흐름을 중심으로 설명하세요.
"""

    gemini_answer = ask_gemini(prompt)

    print("\n=== AI 증감 분석 ===")
    print(gemini_answer)


# ========================================
# 관광 홍보 시기 추천
# ========================================

def run_promotion(region):

    result = recommend_promotion_period(region)

    print("\n=== 관광 홍보 시기 추천 ===")
    print(f"지역: {region}")

    print(
        f"\n성수기: "
        f"{', '.join(map(str, result['성수기']))}월"
    )

    print(
        f"비수기: "
        f"{', '.join(map(str, result['비수기']))}월"
    )

    print(
        f"\n성수기 평균 방문자수: "
        f"{result['성수기 평균 방문자수']:,.0f}명"
    )

    print(
        f"비수기 평균 방문자수: "
        f"{result['비수기 평균 방문자수']:,.0f}명"
    )

    print(
        f"\n홍보 집중 추천 시기: "
        f"{', '.join(map(str, result['홍보 집중 추천 시기']))}월"
    )

    print(
        f"비수기 활성화 추천 시기: "
        f"{', '.join(map(str, result['비수기 활성화 추천 시기']))}월"
    )

    # ------------------------------------
    # Gemini에게 홍보 전략 해석 요청
    # ------------------------------------

    prompt = f"""
당신은 지역 관광 담당자를 지원하는 AI 비서입니다.

다음은 {region}의 2023~2025년 관광 데이터를 바탕으로 분석한 홍보 시기 추천 결과입니다.

[분석 결과]
- 성수기: {', '.join(map(str, result['성수기']))}월
- 비수기: {', '.join(map(str, result['비수기']))}월
- 성수기 평균 방문자수: {result['성수기 평균 방문자수']:,.0f}명
- 비수기 평균 방문자수: {result['비수기 평균 방문자수']:,.0f}명
- 홍보 집중 추천 시기: {', '.join(map(str, result['홍보 집중 추천 시기']))}월
- 비수기 활성화 추천 시기: {', '.join(map(str, result['비수기 활성화 추천 시기']))}월

위 분석 결과를 바탕으로 {region}의 관광 홍보 시기를 관광 담당자가 이해하기 쉽게 3~4문장으로 설명해주세요.

반드시 다음 내용을 포함해주세요.
1. 관광객이 많은 성수기와 홍보 집중 추천 시기
2. 관광객이 적은 비수기와 비수기 활성화 추천 시기
3. 성수기와 비수기의 평균 방문자수 차이가 보여주는 특징
4. 관광 담당자가 홍보 계획을 세울 때 참고할 수 있는 간단한 시사점

주의사항:
1. 제공된 데이터에 없는 사실은 추측하지 마세요.
2. 숫자를 임의로 계산하거나 변경하지 마세요.
3. 성수기와 비수기라는 표현은 제공된 분석 결과에 근거해서 사용하세요.
4. 축제, 날씨, 휴가철, 정책 등의 원인을 추측하지 마세요.
5. 데이터에 근거한 홍보 시기와 방문자 규모를 중심으로 설명하세요.
"""

    gemini_answer = ask_gemini(prompt)

    print("\n=== AI 홍보 전략 분석 ===")
    print(gemini_answer)


# ========================================
# 메인 프로그램
# ========================================

def main():

    print("========================================")
    print("       Local Guide AI")
    print(" 지역 관광 담당자를 위한 AI 비서")
    print("========================================")

    question = input("\n질문을 입력하세요: ")

    found_regions = find_regions(question)
    question_type = classify_question(question, found_regions)

    if question_type == "status":
        run_status(found_regions[0])

    elif question_type == "compare":
        run_compare(found_regions[0], found_regions[1])

    elif question_type == "seasonality":
        run_seasonality(found_regions[0])

    elif question_type == "changes":
        run_changes(found_regions[0])

    elif question_type == "promotion":
        run_promotion(found_regions[0])

    else:
        print("\n질문을 이해하지 못했습니다.")
        print("예시:")
        print("- 충북의 최근 관광객 수는?")
        print("- 충북과 충남 중 어디가 관광객이 많아?")
        print("- 충북 관광객은 언제 가장 많아?")
        print("- 충북 관광객이 가장 많이 증가한 달은?")
        print("- 충북은 언제 홍보하는 게 좋아?")


# ========================================
# 프로그램 실행
# ========================================

if __name__ == "__main__":
    main()