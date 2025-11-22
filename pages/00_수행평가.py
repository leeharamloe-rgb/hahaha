import streamlit as st
import pandas as pd

st.set_page_config(page_title="음식 영양소 & 궁합 추천", layout="wide")

# --------------------------
# CSV 불러오기
# --------------------------
@st.cache_data
def load_data():
    for enc in ["utf-8", "cp949", "latin1"]:
        try:
            return pd.read_csv("food.csv", encoding=enc)
        except:
            pass
    st.error("❌ CSV 파일을 불러올 수 없습니다.")
    return None

df = load_data()

st.title("🍱 음식 영양소 분석 & 궁합 추천기")

st.write("음식을 검색하면 영양소 정보를 보여주고, 함께 먹으면 좋은 음식도 추천해드려요!")

# --------------------------
# 검색 입력창
# --------------------------
search = st.text_input("🔍 영양소를 알고 싶은 음식 이름을 입력하세요:")

if search and df is not None:

    # 검색
    result = df[df["식품명"].str.contains(search, case=False, na=False)]

    if result.empty:
        st.error("❌ 해당 음식이 데이터에 없습니다.")
    else:
        food = result.iloc[0]
        food_name = food["식품명"]
        food_group = food["식품군"]

        st.subheader(f"🍽️ '{food_name}' 영양 정보")

        # --------------------------
        # 주요 영양소 추출
        # --------------------------
        nutrient_cols = ["에너지", "단백질", "지방", "수분"]
        nutrient_data = food[nutrient_cols]

        nutrient_df = pd.DataFrame({
            "영양소": nutrient_cols,
            "함량": nutrient_data.values
        })

        st.table(nutrient_df)

        # --------------------------
        # 음식 궁합 추천 (같은 식품군에서 단백질/지방 균형 고려)
        # --------------------------
        st.subheader(f"✨ '{food_name}'와 함께 먹으면 좋은 음식 추천")

        group_df = df[df["식품군"] == food_group]

        # 가장 영양 균형 맞는 음식 TOP3
        group_df["영양점수"] = (
            group_df["단백질"] * 1.2 +
            group_df["수분"] * 0.5 -
            group_df["지방"] * 0.3
        )

        rec = group_df[group_df["식품명"] != food_name].sort_values(
            by="영양점수",
            ascending=False
        ).head(3)

        st.write(f"✅ 같은 식품군 기준 영양 균형이 좋은 음식 추천!")

        st.table(rec[["식품명", "에너지", "단백질", "지방", "수분"]])
