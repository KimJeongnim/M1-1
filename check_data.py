import pandas as pd
from pathlib import Path

# 통합 데이터 파일 위치
file_path = Path("data/지역별_관광현황_2023_2025.csv")

# CSV 불러오기
df = pd.read_csv(file_path)

print("===== 1. 데이터 기본 정보 =====")
print(f"전체 행 수: {len(df)}")
print(f"전체 열 수: {len(df.columns)}")

print("\n컬럼:")
print(df.columns.tolist())


print("\n===== 2. 데이터 기간 =====")
print(f"최소 기준년월: {df['기준년월'].min()}")
print(f"최대 기준년월: {df['기준년월'].max()}")


print("\n===== 3. 지역 확인 =====")
regions = sorted(df["지역"].unique())

print(f"지역 수: {len(regions)}")
print(regions)


print("\n===== 4. 지역별 데이터 개수 =====")
region_counts = df["지역"].value_counts().sort_index()
print(region_counts)


print("\n===== 5. 결측치 확인 =====")
missing = df.isnull().sum()
print(missing)


print("\n===== 6. 중복 데이터 확인 =====")
duplicates = df.duplicated(
    subset=["기준년월", "지역"]
).sum()

print(f"기준년월 + 지역 중복 행 수: {duplicates}")


print("\n===== 7. 숫자형 데이터 확인 =====")
numeric_columns = [
    "방문자수",
    "전년동월방문자수",
    "방문자수증감률"
]

for column in numeric_columns:
    print(f"\n[{column}]")
    print(f"자료형: {df[column].dtype}")
    print(f"최솟값: {df[column].min()}")
    print(f"최댓값: {df[column].max()}")


print("\n===== 8. 지역별 기간 확인 =====")
period_check = df.groupby("지역")["기준년월"].agg(
    ["min", "max", "count"]
)

print(period_check)


print("\n===== 검사 완료 =====")