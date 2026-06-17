import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="AI & 탄소 배출량 분석", layout="wide")

@st.cache_data
def load_data():
    # 파일 인코딩 문제 해결을 위해 utf-8-sig 사용
    nvidia_df = pd.read_csv("nvidia.csv", encoding='utf-8-sig')
    ms_df = pd.read_csv("msft.csv", encoding='utf-8-sig')

    # [엔비디아 데이터 전처리]
    # "Q1 FY19"에서 19를 추출해 2019로 변환
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    # [마이크로소프트 데이터 전처리]
    # reporting_period(연도)별 value(탄소배출량) 합산
    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    # 연도 기준 병합
    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    
    return nvidia_yearly, ms_yearly, merged_df

# 데이터 로드
try:
    nvidia_yearly, ms_yearly, merged_df = load_data()
except Exception as e:
    st.error(f"데이터 로딩 오류: {e}. 파일 이름(nvidia.csv, msft.csv)과 형식을 확인하세요.")
    st.stop()

# --- 사이드바 ---
st.sidebar.title("메뉴")
page = st.sidebar.radio("분석 페이지", ["1. 데이터 추이", "2. 상관관계 분석"])

# --- 페이지 1 ---
if page == "1. 데이터 추이":
    st.title("🌱 AI 산업 성장과 탄소 배출량 추이")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("엔비디아 데이터센터 매출")
        fig1 = px.line(nvidia_yearly, x='Year', y='Nvidia_Revenue_M', markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("마이크로소프트 탄소 배출량")
        fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', markers=True)
        st.plotly_chart(fig2, use_container_width=True)

# --- 페이지 2 ---
elif page == "2. 상관관계 분석":
    st.title("🔍 상관관계 분석")
    st.subheader("매출 vs 탄소 배출량 산점도")
    
    fig3 = px.scatter(merged_df, x='Nvidia_Revenue_M', y='MSFT_Emissions', 
                      trendline="ols", text="Year")
    st.plotly_chart(fig3, use_container_width=True)
    
    corr = merged_df['Nvidia_Revenue_M'].corr(merged_df['MSFT_Emissions'])
    st.metric("피어슨 상관계수", f"{corr:.4f}")
    st.write("상관계수가 1에 가까울수록 매출 증가와 탄소 배출량 증가가 매우 밀접하게 비례함을 의미합니다.")
