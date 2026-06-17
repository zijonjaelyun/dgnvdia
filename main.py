import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI & 탄소 배출량 분석", layout="wide")

@st.cache_data
def load_and_process():
    # 1. 엔비디아 데이터 로드 및 전처리
    nvidia_df = pd.read_csv("nvidia.csv", encoding='utf-8-sig')
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    # 연도별로 그룹화하여 매출 합산
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    # 2. 마이크로소프트 데이터 로드 및 전처리
    ms_df = pd.read_csv("msft.csv", encoding='utf-8-sig')
    # reporting_period 별로 value(배출량) 합산
    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    # 3. 데이터 병합 (연도 기준)
    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    
    return nvidia_yearly, ms_yearly, merged_df

# 데이터 처리 실행
try:
    nvidia_yearly, ms_yearly, merged_df = load_and_process()
except Exception as e:
    st.error(f"데이터 처리 오류: {e}")
    st.stop()

# --- 대시보드 UI ---
st.title("🌱 AI 기술 성장과 탄소 배출량 관계 분석")

# 페이지 구성
tab1, tab2 = st.tabs(["📊 지표 추이", "📈 상관관계 분석"])

with tab1:
    st.subheader("연도별 주요 지표 변화")
    fig1 = px.line(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', title="NVIDIA 데이터센터 매출 (연간 합계)")
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', title="Microsoft 총 온실가스 배출량 (mtCO2e)")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("데이터센터 매출과 탄소 배출량의 상관관계")
    fig3 = px.scatter(merged_df, x='데이터센터 매출 (백만 달러)', y='MSFT_Emissions', 
                      trendline="ols", text="Year", title="매출 대비 탄소 배출량 산점도")
    st.plotly_chart(fig3, use_container_width=True)
    
    corr = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['MSFT_Emissions'])
    st.write(f"### 두 지표 사이의 상관계수: {corr:.4f}")
