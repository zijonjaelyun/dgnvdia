import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI & 탄소 배출 분석", layout="wide")

# (이전의 read_csv_robust 함수와 load_and_process 함수는 그대로 사용)

# --- 상단 요약 카드 (Metric Cards) ---
st.title("🌱 AI 기술 성장과 환경적 비용: 종합 분석 리포트")
st.markdown("데이터센터의 비약적 성장과 기업의 환경 발자국을 시각화합니다.")

nvidia_yearly, ms_yearly, merged_df = load_and_process()

# 최근 매출과 탄소 배출량을 하이라이트
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("최근 NVIDIA 매출", f"${nvidia_yearly['데이터센터 매출 (백만 달러)'].iloc[-1]:,.0f}M")
with col2:
    st.metric("최근 MS 탄소 배출량", f"{ms_yearly['MSFT_Emissions'].iloc[-1]:,.0f} mtCO2e")
with col3:
    st.metric("데이터 가용 연도", f"{len(merged_df)}년")

st.divider()

# --- 내용 배치: 데이터 밀도 높이기 ---
c1, c2 = st.columns([0.6, 0.4])
with c1:
    st.subheader("📊 연간 지표 추이 시각화")
    # 두 그래프를 한 번에 보여주기 위해 탭 활용
    tab1, tab2 = st.tabs(["NVIDIA 매출", "Microsoft 탄소 배출"])
    with tab1:
        fig = px.bar(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', color='데이터센터 매출 (백만 달러)')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = px.area(ms_yearly, x='Year', y='MSFT_Emissions', color_discrete_sequence=['red'])
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("📋 데이터셋 상세 정보")
    st.dataframe(merged_df.style.highlight_max(axis=0), use_container_width=True)
    st.caption("※ 연도별 합산된 데이터 요약 테이블입니다.")
