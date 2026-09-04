import pandas as pd
from pathlib import Path


# ========================================
# 데이터 경로
# ========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_2023_2025 = BASE_DIR / "data" / "지역별_관광현황_2023_2025.csv"
DATA_2026 = BASE_DIR / "data" / "지역별_관광현황_2026.csv"


# ========================================
# 데이터 불러오기
# ========================================

def load_data():
    """2023~2026 관광 데이터를 불러와 하나로 합친다."""

    df_2023_2025 = pd.read_csv(DATA_2023_2025)
    df_2026 = pd.read_csv(DATA_2026)

    df = pd.concat(
        [df_2023_2025, df_2026],
        ignore_index=True
    )

    # 기준년월을 문자열로 통일
    df["기준년월"] = df["기준년월"].astype(str)

    # 방문자수가 0인 데이터는 결측으로 처리
    df.loc[
        df["방문자수"] == 0,
        "방문자수"
    ] = pd.NA

    # -100%는 현재 데이터에서
    # 광주/전남 202607의 미집계 데이터로 판단
    df.loc[
        df["방문자수증감률"] == -100,
        "방문자수증감률"
    ] = pd.NA

    return df


# ========================================
# ① 지역 관광 현황 분석
# ========================================

def get_region_status(region):
    """특정 지역의 관광 현황을 분석한다."""

    df = load_data()

    region_df = df[
        df["지역"] == region
    ].copy()

    if region_df.empty:
        return {
            "지역": region,
            "오류": "해당 지역의 데이터가 없습니다."
        }

    region_df = region_df.sort_values(
        "기준년월"
    )

    # 실제 방문자수가 존재하는 가장 최근 데이터
    valid_df = region_df.dropna(
        subset=["방문자수"]
    )

    latest = valid_df.iloc[-1]

    # 평균 증감률
    average_growth = (
        region_df["방문자수증감률"].mean()
    )

    # 증가 월
    increase_months = region_df[
        region_df["방문자수증감률"] > 0
    ]["기준년월"].tolist()

    # 감소 월
    decrease_months = region_df[
        region_df["방문자수증감률"] < 0
    ]["기준년월"].tolist()

    # 최근 3개월 추세
    recent_growth = (
        region_df["방문자수증감률"]
        .dropna()
        .tail(3)
    )

    recent_average = recent_growth.mean()

    if recent_average > 0:
        trend = "증가"
    elif recent_average < 0:
        trend = "감소"
    else:
        trend = "보합"

    return {
        "지역": region,
        "분석기간": (
            f"{region_df['기준년월'].iloc[0]}"
            f"~"
            f"{region_df['기준년월'].iloc[-1]}"
        ),
        "최근 기준월": latest["기준년월"],
        "최근 방문자수": latest["방문자수"],
        "최근 증감률": latest["방문자수증감률"],
        "평균 증감률": average_growth,
        "최근 추세": trend,
        "증가 월수": len(increase_months),
        "감소 월수": len(decrease_months)
    }


# ========================================
# ② 지역 관광 비교 분석
# ========================================

def compare_regions(region1, region2):
    """두 지역의 관광 현황을 비교한다."""

    df = load_data()

    result = {}

    for region in [region1, region2]:

        region_df = df[
            df["지역"] == region
        ].copy()

        region_df = region_df.sort_values(
            "기준년월"
        )

        valid_df = region_df.dropna(
            subset=["방문자수"]
        )

        if valid_df.empty:
            result[region] = {
                "오류": "데이터가 없습니다."
            }
            continue

        latest = valid_df.iloc[-1]

        result[region] = {
            "최근 기준월": latest["기준년월"],
            "최근 방문자수": latest["방문자수"],
            "최근 증감률": latest["방문자수증감률"],
            "평균 방문자수": valid_df["방문자수"].mean(),
            "평균 증감률": (
                region_df["방문자수증감률"].mean()
            )
        }

    return result


# ========================================
# ③ 관광객 증감 분석
# ========================================

def analyze_changes(region):
    """특정 지역의 관광객 증감 현황을 분석한다."""

    df = load_data()

    region_df = df[
        df["지역"] == region
    ].copy()

    region_df = region_df.sort_values(
        "기준년월"
    )

    if region_df.empty:
        return {
            "지역": region,
            "오류": "해당 지역의 데이터가 없습니다."
        }

    # 증감률 데이터가 있는 행만 사용
    valid_df = region_df.dropna(
        subset=["방문자수증감률"]
    )

    # 가장 많이 증가한 달
    max_growth = valid_df.loc[
        valid_df["방문자수증감률"].idxmax()
    ]

    # 가장 많이 감소한 달
    min_growth = valid_df.loc[
        valid_df["방문자수증감률"].idxmin()
    ]

    # 증가 월
    increase_df = valid_df[
        valid_df["방문자수증감률"] > 0
    ]

    # 감소 월
    decrease_df = valid_df[
        valid_df["방문자수증감률"] < 0
    ]

    return {
        "지역": region,
        "최대 증가 월": max_growth["기준년월"],
        "최대 증가율": max_growth["방문자수증감률"],
        "최대 증가 방문자수": max_growth["방문자수"],
        "최대 감소 월": min_growth["기준년월"],
        "최대 감소율": min_growth["방문자수증감률"],
        "최대 감소 방문자수": min_growth["방문자수"],
        "증가 월수": len(increase_df),
        "감소 월수": len(decrease_df)
    }


# ========================================
# ④ 관광 시기 / 계절 분석
# ========================================

def analyze_seasonality(region):
    """특정 지역의 관광객 계절 및 월별 패턴을 분석한다."""

    df = load_data()

    # 완전한 연도인 2023~2025년만 사용
    region_df = df[
        (df["지역"] == region)
        &
        (
            df["기준년월"]
            .str[:4]
            .isin(["2023", "2024", "2025"])
        )
    ].copy()

    if region_df.empty:
        return {
            "지역": region,
            "오류": "해당 지역의 데이터가 없습니다."
        }

    # 월 추출
    region_df["월"] = (
        region_df["기준년월"].str[4:6]
    )

    # 월별 평균 방문자수
    monthly_avg = (
        region_df
        .groupby("월")["방문자수"]
        .mean()
        .sort_values(ascending=False)
    )

    # 가장 많은 달
    peak_month = monthly_avg.idxmax()

    # 가장 적은 달
    low_month = monthly_avg.idxmin()

    return {
        "지역": region,
        "월별 평균 방문자수": monthly_avg.to_dict(),
        "최다 방문 월": peak_month,
        "최다 방문 월 평균": monthly_avg.max(),
        "최소 방문 월": low_month,
        "최소 방문 월 평균": monthly_avg.min()
    }


# ========================================
# ⑤ 관광 홍보 시기 추천
# ========================================

def recommend_promotion_period(region):
    """
    관광객의 계절 및 월별 패턴을 바탕으로
    성수기 홍보 집중 시기와 비수기 활성화 시기를 추천한다.
    """

    seasonality = analyze_seasonality(region)

    if "오류" in seasonality:
        return seasonality

    monthly_avg = seasonality["월별 평균 방문자수"]

    # 관광객이 많은 상위 3개월
    peak_months = list(monthly_avg.keys())[:3]

    # 관광객이 적은 하위 3개월
    low_months = list(monthly_avg.keys())[-3:]

    # 상위 3개월 평균
    peak_average = sum(
        monthly_avg[month]
        for month in peak_months
    ) / len(peak_months)

    # 하위 3개월 평균
    low_average = sum(
        monthly_avg[month]
        for month in low_months
    ) / len(low_months)

    return {
        "지역": region,
        "성수기": peak_months,
        "비수기": low_months,
        "성수기 평균 방문자수": peak_average,
        "비수기 평균 방문자수": low_average,
        "홍보 집중 추천 시기": peak_months,
        "비수기 활성화 추천 시기": low_months
    }


# ========================================
# 테스트 실행
# ========================================

if __name__ == "__main__":

    # ------------------------------------
    # ① 지역 관광 현황 분석
    # ------------------------------------

    print("=== 지역 관광 현황 분석 ===")

    result = get_region_status("충북")

    print(
        f"지역: {result['지역']}"
    )

    print(
        f"분석기간: {result['분석기간']}"
    )

    print(
        f"최근 기준월: {result['최근 기준월']}"
    )

    print(
        f"최근 방문자수: "
        f"{result['최근 방문자수']:,.0f}명"
    )

    print(
        f"최근 증감률: "
        f"{result['최근 증감률']:.1f}%"
    )

    print(
        f"평균 증감률: "
        f"{result['평균 증감률']:.2f}%"
    )

    print(
        f"최근 추세: "
        f"{result['최근 추세']}"
    )

    print(
        f"증가 월수: "
        f"{result['증가 월수']}개월"
    )

    print(
        f"감소 월수: "
        f"{result['감소 월수']}개월"
    )


    # ------------------------------------
    # ② 지역 비교 분석
    # ------------------------------------

    print()
    print("=== 지역 비교 분석 ===")

    comparison = compare_regions(
        "충북",
        "충남"
    )

    for region, data in comparison.items():

        print()
        print(f"[{region}]")

        print(
            f"최근 기준월: "
            f"{data['최근 기준월']}"
        )

        print(
            f"최근 방문자수: "
            f"{data['최근 방문자수']:,.0f}명"
        )

        print(
            f"최근 증감률: "
            f"{data['최근 증감률']:.1f}%"
        )

        print(
            f"평균 방문자수: "
            f"{data['평균 방문자수']:,.0f}명"
        )

        print(
            f"평균 증감률: "
            f"{data['평균 증감률']:.2f}%"
        )


    # ------------------------------------
    # ③ 관광객 증감 분석
    # ------------------------------------

    print()
    print("=== 관광객 증감 분석 ===")

    changes = analyze_changes("충북")

    print(
        f"지역: "
        f"{changes['지역']}"
    )

    print(
        f"가장 많이 증가한 달: "
        f"{changes['최대 증가 월']} "
        f"({changes['최대 증가율']:.1f}%)"
    )

    print(
        f"당시 방문자수: "
        f"{changes['최대 증가 방문자수']:,.0f}명"
    )

    print(
        f"가장 많이 감소한 달: "
        f"{changes['최대 감소 월']} "
        f"({changes['최대 감소율']:.1f}%)"
    )

    print(
        f"당시 방문자수: "
        f"{changes['최대 감소 방문자수']:,.0f}명"
    )

    print(
        f"증가 월수: "
        f"{changes['증가 월수']}개월"
    )

    print(
        f"감소 월수: "
        f"{changes['감소 월수']}개월"
    )


    # ------------------------------------
    # ④ 관광 시기 / 계절 분석
    # ------------------------------------

    print()
    print("=== 관광 시기 / 계절 분석 ===")

    seasonality = analyze_seasonality("충북")

    print(
        f"지역: "
        f"{seasonality['지역']}"
    )

    print(
        f"관광객이 가장 많은 월: "
        f"{seasonality['최다 방문 월']}월"
    )

    print(
        f"해당 월 평균 방문자수: "
        f"{seasonality['최다 방문 월 평균']:,.0f}명"
    )

    print(
        f"관광객이 가장 적은 월: "
        f"{seasonality['최소 방문 월']}월"
    )

    print(
        f"해당 월 평균 방문자수: "
        f"{seasonality['최소 방문 월 평균']:,.0f}명"
    )

    print()
    print("월별 평균 방문자수:")

    for month, visitors in seasonality[
        "월별 평균 방문자수"
    ].items():

        print(
            f"{month}월: "
            f"{visitors:,.0f}명"
        )


    # ------------------------------------
    # ⑤ 관광 홍보 시기 추천
    # ------------------------------------

    print()
    print("=== 관광 홍보 시기 추천 ===")

    promotion = recommend_promotion_period("충북")

    print(
        f"지역: "
        f"{promotion['지역']}"
    )

    print(
        f"성수기: "
        f"{', '.join(promotion['성수기'])}월"
    )

    print(
        f"비수기: "
        f"{', '.join(promotion['비수기'])}월"
    )

    print(
        f"성수기 평균 방문자수: "
        f"{promotion['성수기 평균 방문자수']:,.0f}명"
    )

    print(
        f"비수기 평균 방문자수: "
        f"{promotion['비수기 평균 방문자수']:,.0f}명"
    )

    print(
        f"홍보 집중 추천 시기: "
        f"{', '.join(promotion['홍보 집중 추천 시기'])}월"
    )

    print(
        f"비수기 활성화 추천 시기: "
        f"{', '.join(promotion['비수기 활성화 추천 시기'])}월"
    )