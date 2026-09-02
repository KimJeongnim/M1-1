import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 1. 데이터 불러오기 및 전처리
df_past = pd.read_csv("data/지역별_관광현황_2023_2025.csv")
df_2026 = pd.read_csv("data/지역별_관광현황_2026.csv")

df_past["날짜"] = pd.to_datetime(df_past["기준년월"].astype(str), format="%Y%m")
df_2026["날짜"] = pd.to_datetime(df_2026["기준년월"].astype(str), format="%Y%m")

# 월별 전체 방문자수 합산 및 인덱스 설정
monthly_past = df_past.groupby("날짜")["방문자수"].sum().sort_index()
monthly_past.index = pd.to_datetime(monthly_past.index)
monthly_past = monthly_past.asfreq("MS")

monthly_2026_actual = df_2026.groupby("날짜")["방문자수"].sum().sort_index()

# 2. Holt-Winters 계절성 시계열 모델 학습 및 2026년 1~7월 예측
model = ExponentialSmoothing(monthly_past, trend="add", seasonal="add", seasonal_periods=12).fit()
forecast_values = model.forecast(7)

# 예측 결과 데이터프레임 변환
forecast_dates = pd.date_range(start="2026-01-01", end="2026-07-01", freq="MS")
df_forecast_2026 = pd.DataFrame({"ds": forecast_dates, "yhat": forecast_values.values})

# 3. 실제 데이터와 예측 데이터 병합 및 오차(MAE, RMSE, MAPE) 계산
comparison = pd.merge(monthly_2026_actual.reset_index(), df_forecast_2026, left_on="날짜", right_on="ds")
actual = comparison["방문자수"].values
pred = comparison["yhat"].values

mae = mean_absolute_error(actual, pred)
rmse = np.sqrt(mean_squared_error(actual, pred))
mape = np.mean(np.abs((actual - pred) / actual)) * 100

print(f"[Holt-Winters 모델 성능 평가]")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.2f}%\n")

# 4. 시각화
plt.figure(figsize=(12, 6))

# 과거 실제 데이터 (최근 2년간)
recent_past = monthly_past[monthly_past.index >= "2024-01-01"]
plt.plot(recent_past.index, recent_past.values, label="과거 실제 (2024~2025)", color="gray", alpha=0.7)

# 2026년 실제 값 (인덱스 사용)
plt.plot(monthly_2026_actual.index, monthly_2026_actual.values, label="2026년 실제 (Actual)", marker="o", color="blue", linewidth=2)

# 2026년 예측 값
plt.plot(df_forecast_2026["ds"], df_forecast_2026["yhat"], label="2026년 예측 (Holt-Winters)", marker="x", linestyle="--", color="red", linewidth=2)

plt.title("2026년 관광 방문자 수 예측 vs 실제 비교")
plt.xlabel("기간")
plt.ylabel("방문자 수")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig("images/06_prophet_forecast.png", dpi=150)
plt.show()
print("예측 비교 그래프 저장 완료: images/06_prophet_forecast.png")