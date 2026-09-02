import pandas as pd
import glob
import os

# 2026년 지역별 CSV가 들어 있는 폴더
folder = "data/2026"

# CSV 파일 찾기
files = glob.glob(os.path.join(folder, "*.csv"))

print(f"찾은 CSV 파일 수: {len(files)}개")

dataframes = []

for file in files:
    # CSV 읽기
    df = pd.read_csv(file, encoding="utf-8-sig")

    # 파일 이름에서 지역명 가져오기
    # 예: 서울.csv → 서울
    region = os.path.splitext(os.path.basename(file))[0].split("(")[-1].replace(")", "")

    # 지역 열 추가
    df["지역"] = region

    dataframes.append(df)

    print(f"완료: {region} ({len(df)}행)")

# 17개 지역 데이터 하나로 합치기
merged = pd.concat(dataframes, ignore_index=True)

# 열 순서 정리
merged = merged[
    ["기준년월", "지역", "방문자수", "전년동월방문자수", "방문자수증감률"]
]

# 기준년월 → 지역 순으로 정렬
merged = merged.sort_values(["기준년월", "지역"])

# 최종 파일 저장
output = "data/지역별_관광현황_2026.csv"

merged.to_csv(
    output,
    index=False,
    encoding="utf-8-sig"
)

print()
print("================================")
print("2026년 데이터 합치기 완료!")
print("================================")
print(f"전체 행 수: {len(merged)}")
print(f"지역 수: {merged['지역'].nunique()}")
print(f"저장 위치: {output}")
print()
print("지역 목록:")
print(sorted(merged["지역"].unique()))