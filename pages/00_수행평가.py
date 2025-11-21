import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# -----------------------
# 데이터 불러오기
# -----------------------
st.title("🍱 음식 영양소 검색 & 추천 시스템")

@st.cache_data
def load_data():
    return pd.read_csv("food.csv", encoding="cp949")

df = load_data()

st.success("데이터 로딩 완료!")

# -----------------------
# 기본 설정
# -----------------------
# 식품명 컬럼 자동 탐색
name_candidates = ["식품명", "식품 이름", "음식명", "제품명"]
food_name_col = None
for c in name_candidates:
    if c in df.columns:
        food_name_col = c
        break

if food_name_col is None:
    st.error("❌ CSV 파일에서 식품명 컬럼을 찾을 수 없습니다. 컬럼명을 알려주세요!")
    st.stop()

# 숫자형 영양소 목록
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

# -----------------------
# 음식 검색 기능
# -----------------------
st.subheader("🔍 음식 검색하기")

search = st.text_input("음식 이름을 입력하세요:", "")

if search:
    # 검색 결과 필터링
    result = df[df[food_name_col].str.contains(search, case=False, na=False)]

    if result.empty:
        st.warning("검색 결과가 없습니다. 다시 입력해주세요!")
    else:
        st.success(f"총 {len(result)}개의 결과를 찾았습니다.")
        st.dataframe(result.head())

        # 첫 번째 음식 선택
        selected_food = st.selectbox("영양소를 확인할 음식을 선택하세요:", result[food_name_col].tolist())

        # 선택 음식 데이터
        selected_row = df[df[food_name_col] == selected_food].iloc[0]

        st.subheader("📊 선택한 음식의 영양소 정보")
        st.write(selected_row[numeric_cols].to_frame("값"))

        # -----------------------
        # 영양소 시각화
        # -----------------------
        fig = px.bar(
            x=numeric_cols,
            y=selected_row[numeric_cols].values,
            title=f"'{selected_food}' 영양소 구성",
            labels={"x": "영양소", "y": "값"},
        )
        fig.update_layout(xaxis_tickangle=45, height=600)
        st.plotly_chart(fig, use_container_width=True)

        # -----------------------
        # 음식 추천 기능 (유사도 기반)
        # -----------------------
        st.subheader("⭐ 추천 음식 (영양성분이 비슷한 음식)")

        # 수치화 + 정규화
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(df[numeric_cols])

        # 전체 유사도 계산
        sim = cosine_similarity(scaled)

        # 선택 음식 인덱스
        food_index = df[df[food_name_col] == selected_food].index[0]

        # 유사도 점수
        sim_scores = list(enumerate(sim[food_index]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 자기 자신 제외하고 TOP5 추천
        top5 = sim_scores[1:6]

        recommended_foods = [df.iloc[i][food_name_col] for i, _ in top5]

        st.write("🔽 **검색한 음식과 영양 구성이 비슷한 추천 음식 Top 5**")
        for idx, food in enumerate(recommended_foods, 1):
            st.write(f"{idx}. {food}")

