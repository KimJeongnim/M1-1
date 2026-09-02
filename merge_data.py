import pandas as pd
from pathlib import Path
import re

# 원본 CSV 파일이 있는 폴더
data_folder = Path("data/raw")

# CSV 파일 목록 가져오기
files = list(data_folder.glob("*.csv"))

print(f"찾은 CSV 파일 수: {len(files)}")

all_data = []

for file in files:
    print(f"처리 중: {file.name}")

    # 파일명에서 지역명 추출
    # 예: 202301-202406(강원).csv → 강원
    match = re.search(r"\((.*?)\)", file.stem)

    if not match:
        print(f"  → 지역명을 찾을 수 없습니다: {file.name}")
        continue

    region = match.group(1)

    # CSV 파일 읽기
    df = pd.read_csv(file)

    # 지역 컬럼 추가
    df["지역"] = region

    all_data.append(df)

# 모든 파일 합치기
merged_df = pd.concat(all_data, ignore_index=True)

# 컬럼 순서 정리
merged_df = merged_df[
    [
        "기준년월",
        "지역",
        "방문자수",
        "전년동월방문자수",
        "방문자수증감률"
    ]
]

# 기준년월과 지역 기준으로 정렬
merged_df = merged_df.sort_values(
    ["지역", "기준년월"]
).reset_index(drop=True)

# 통합 파일 저장
output_file = Path("data/지역별_관광현황_2023_2025.csv")

merged_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\n===== 통합 완료 =====")
print(f"전체 데이터 수: {len(merged_df)}")
print(f"지역 수: {merged_df['지역'].nunique()}")

print("\n지역별 데이터 개수:")
print(merged_df["지역"].value_counts().sort_index())

print(f"\n저장 위치: {output_file}")