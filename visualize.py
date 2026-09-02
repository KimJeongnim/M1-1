import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"

# 마이너스 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False


# ========================================
# 데이터 불러오기
# ========================================

df = pd.read_csv("data/지역별_관광현황_2023_2025.csv")

df["연도"] = df["기준년월"].astype(str).str[:4].astype(int)
df["월"] = df["기준년월"].astype(str).str[4:6].astype(int)

# ========================================
# 기준년월을 날짜 형식으로 변환
# ========================================

df["날짜"] = pd.to_datetime(
    df["기준년월"].astype(str),
    format="%Y%m"
)


# ========================================
# 월별 전체 관광객 수 계산
# ========================================

monthly_total = (
    df.groupby("날짜")["방문자수"]
    .sum()
    .sort_index()
)


# ========================================
# 3개월 이동평균 계산
# ========================================

monthly_ma3 = monthly_total.rolling(window=3).mean()


# ========================================
# 그래프 생성
# ========================================

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_total.index,
    monthly_total.values,
    label="월별 전체 방문자수"
)

plt.plot(
    monthly_ma3.index,
    monthly_ma3.values,
    label="3개월 이동평균",
    linewidth=2
)

plt.title("2023~2025년 전체 관광 방문 추세")
plt.xlabel("기간")
plt.ylabel("방문자 수")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()


# ========================================
# 이미지 저장
# ========================================

plt.savefig(
    "images/01_total_trend.png",
    dpi=150
)

plt.show()

print("그래프 저장 완료: images/01_total_trend.png")

# ========================================
# 두 번째 그래프: 월별 계절성
# ========================================

monthly_avg = (
    df.groupby(df["날짜"].dt.month)["방문자수"]
    .mean()
)

plt.figure(figsize=(10, 6))

plt.bar(
    monthly_avg.index,
    monthly_avg.values
)

plt.title("2023~2025년 월별 평균 관광 방문자 수")
plt.xlabel("월")
plt.ylabel("평균 방문자 수")

plt.xticks(range(1, 13))

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "images/02_monthly_seasonality.png",
    dpi=150
)

plt.show()

print("그래프 저장 완료: images/02_monthly_seasonality.png")

# ========================================
# 세 번째 그래프: 지역별 2023 → 2025 변화율
# ========================================

region_year = (
    df.groupby(["지역", "연도"])["방문자수"]
    .mean()
    .unstack()
)

region_change = (
    (region_year[2025] - region_year[2023])
    / region_year[2023] * 100
).sort_values()

plt.figure(figsize=(10, 7))

plt.barh(
    region_change.index,
    region_change.values
)

plt.title("지역별 2023 → 2025 평균 관광 방문자 수 변화율")
plt.xlabel("변화율 (%)")
plt.ylabel("지역")

plt.axvline(
    0,
    linewidth=1
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    "images/03_region_change.png",
    dpi=150
)

plt.show()

print("그래프 저장 완료: images/03_region_change.png")

# ========================================
# 네 번째 그래프: 주요 지역별 관광객 추세
# ========================================

# 비교할 주요 지역
main_regions = ["경기", "서울", "경북", "인천", "부산"]

region_monthly = (
    df[df["지역"].isin(main_regions)]
    .groupby(["날짜", "지역"])["방문자수"]
    .mean()
    .unstack()
)

plt.figure(figsize=(12, 6))

for region in main_regions:
    plt.plot(
        region_monthly.index,
        region_monthly[region],
        label=region,
        linewidth=2
    )

plt.title("2023~2025년 주요 지역별 관광 방문자 수 추세")
plt.xlabel("기간")
plt.ylabel("방문자 수")

plt.legend()

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    "images/04_main_region_trend.png",
    dpi=150
)

plt.show()

print("그래프 저장 완료: images/04_main_region_trend.png")

# ========================================
# 다섯 번째 그래프: 월별 방문자수 증감률
# ========================================

monthly_change = (
    df.groupby("날짜")["방문자수증감률"]
    .mean()
    .sort_index()
)

plt.figure(figsize=(12, 6))

plt.plot(
    monthly_change.index,
    monthly_change.values,
    marker="o",
    linewidth=1.5
)

# 기준선: 증감률 0%
plt.axhline(
    0,
    linewidth=1
)

plt.title("2023~2025년 월별 평균 관광객 수 증감률")
plt.xlabel("기간")
plt.ylabel("전년 동월 대비 증감률 (%)")

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    "images/05_monthly_change_rate.png",
    dpi=150
)

plt.show()

print("그래프 저장 완료: images/05_monthly_change_rate.png")