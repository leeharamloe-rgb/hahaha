import streamlit as st
import pandas as pd

st.set_page_config(page_title="음식 영양소 분석기", layout="wide")

# --------------------------
# CSV 파일 로드
# --------------------------
@st.cache_data
def load_data():
    # 여러 인코딩 자동 시도
    for enc in ["utf-8", "cp949", "latin1"]:
        try:
            return pd.read_csv("food.csv", encoding=enc)
        except:
            pass
    st.error("❌ CSV 파일을 읽는 중 오류가 발생했습니다.")
    return None

df = load_data()

st.title("🥗 음식 영양소 분석기")
st.write("음식을 검색하면 영양 정보를 쉽게 보여주고, 함께 먹기 좋은 음식도 추천해드려요!")

# --------------------------
# 음식 검색 입력창
# --------------------------
search = st.text_input("🔍 영양소를 확인하고 싶은 음식을 입력하세요:")

if search:
    # 사용자 입력 포함된 음식 찾기
    result = df[df["음식"].str.contains(search, case=False, na=False)]

    if result.empty:
        st.error("❌ 해당 음식이 데이터에 없습니다.")
    else:
        # 첫 번째 결과 사용
        food_row = result.iloc[0]
        food_name = food_row["음식"]

        st.subheader(f"🍱 '{food_name}' 영양 정보 요약")

        # --------------------------
        # 영양소 정보 테이블
        # --------------------------
        nutrient_cols = [c for c in df.columns if c != "음식"]
        nutrients = food_row[nutrient_cols]

        summary = pd.DataFrame({
            "영양소": nutrients.index,
            "함량": nutrients.values
        }).sort_values(by="함량", ascending=False)

        st.dataframe(summary, use_container_width=True)

        # --------------------------
        # 추천 음식 기능 (sklearn 없이 구현)
        # 가장 높은 영양소 1개 기준으로 추천
        # --------------------------
        top_nutrient = summary.iloc[0]["영양소"]

        st.subheader(f"✨ '{food_name}'와 궁합이 좋은 음식 추천")
        st.write(f"➡️ '{top_nutrient}' 영양소가 풍부한 음식 기반 추천")

        rec_df = df.sort_values(by=top_nutrient, ascending=False)

        # 자신 제외
        rec_df = rec_df[rec_df["음식"] != food_name].head(3)

        st.table(rec_df[["음식", top_nutrient]])
