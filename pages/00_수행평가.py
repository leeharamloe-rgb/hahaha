import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# 데이터 불러오기
# -----------------------
st.title("🍱 식품 영양소 분석 대시보드")

@st.cache_data
def load_data():
    return pd.read_csv("food.csv", encoding="cp949")

df = load_data()

st.success("데이터 로딩 완료!")

# -----------------------
# 기본 정보 출력
# -----------------------
st.subheader("📌 데이터 미리보기")
st.dataframe(df.head())

# -----------------------
# 영양소 컬럼 자동 추출
# (수분, 단백질, 지방, 탄수화물 등 숫자형 컬럼)
# -----------------------
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

# 식품명 컬럼 찾기
name_candidates = ["식품명", "음식명", "제품명"]
food_name_col = None
for c in name_candidates:
    if c in df.columns:
        food_name_col = c
        break

if food_name_col is None:
   st.error("식품명 컬럼을 찾을 수 없습니다. CSV 파일 내 식품명 컬럼명을 알려주세요.")
   st.stop()

# -----------------------
# 영양소 선택 UI
# -----------------------
st.subheader("🥗 영양소 선택하여 음식별 비교하기")

selected_nutrient = st.selectbox("영양소를 선택하세요:", numeric_cols)

# -----------------------
# Plotly 그래프 생성
# -----------------------
fig = px.bar(
    df.sort_values(selected_nutrient, ascending=False).head(30),
    x=food_name_col,
    y=selected_nutrient,
    title=f"📊 음식별 '{selected_nutrient}' 값 비교 (상위 30개)",
    labels={food_name_col: "식품명", selected_nutrient: selected_nutrient},
)

fig.update_layout(
    xaxis_tickangle=45,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# 영양소 상세 보기
# -----------------------
st.subheader("📄 선택한 영양소 수치 테이블")
st.dataframe(df[[food_name_col, selected_nutrient]].sort_values(selected_nutrient, ascending=False))
