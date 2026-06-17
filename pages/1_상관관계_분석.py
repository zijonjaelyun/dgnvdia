import streamlit as st
import plotly.express as px

# (데이터 로드 함수는 동일)

st.title("🔍 상관관계 및 환경 전략 분석")

# 분석 차트
st.subheader("매출 vs 탄소 배출량 회귀 분석")
fig = px.scatter(merged_df, x='데이터센터 매출 (백만 달러)', y='MSFT_Emissions', 
                 size='MSFT_Emissions', color='Year', hover_name='Year',
                 trendline="ols", title="인프라 투자 규모와 환경 부하의 비례 관계")
st.plotly_chart(fig, use_container_width=True)

# --- 분석 내용 꽉 채우기 ---
st.markdown("---")
# 섹션 나누기
col_left, col_right = st.columns(2)

with col_left:
    st.warning("### 🧐 분석적 해석")
    st.write("""
    1. **상관관계 결과:** 두 변수 간의 높은 상관계수는 AI 인프라 확장이 탄소 배출과 직접적으로 연동되어 있음을 시사합니다.
    2. **지연 효과:** 매출 성장이 가파른 시점에 탄소 배출량 또한 비례하여 급증하는 경향을 보입니다.
    """)

with col_right:
    st.success("### 🛠️ 대응 과제")
    st.write("""
    1. **에너지 효율 최적화:** AI 연산 효율성을 높이는 'Green AI' 알고리즘의 도입이 필수적입니다.
    2. **친환경 에너지 전환:** 재생 에너지 사용 비율을 100%까지 올리는 에너지 믹스 재구성이 필요합니다.
    """)

# 하단에 분석 레벨 높이기
st.subheader("전략 제언: 2030 Net-Zero 로드맵")
st.markdown("""
* **단기:** 데이터센터 냉각 시스템 효율화 (PUE 최적화)
* **중기:** AI 서버 공급망의 친환경 소재 및 재활용 프로세스 구축
* **장기:** 탄소 포집 기술(DAC) 및 차세대 저전력 반도체 플랫폼 전환
""")
