import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="AI와 탄소 배출량 분석", page_icon="🌱", layout="wide")

# 데이터 불러오기 및 전처리 (캐싱을 통해 속도 향상)
@st.cache_data
def load_data():
    # 1. 엔비디아 실적 데이터 처리
    # (실제 파일 경로에 맞게 파일명을 수정해야 할 수 있습니다)
    nvidia_df = pd.read_csv("엔비디아실적보고서.csv")
    
    # 'Q1 FY19' 문자열에서 연도 추출 (예: 19 -> 2019)
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    
    # 연도별 데이터센터 매출 합산
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()
    nvidia_yearly.columns = ['Year', 'Nvidia_Revenue_M']

    # 2. 마이크로소프트 탄소 배출량 데이터 처리
    ms_df = pd.read_csv("tracenable-ghg-emissions-2019-2024-microsoft-20260617.xlsx - Sheet1.csv")
    
    # 연도별(reporting_period) 탄소 배출량 총합 계산
    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    # 3. 데이터 병합 (연도를 기준으로 교집합)
    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    return nvidia_yearly, ms_yearly, merged_df

# 데이터 로드
try:
    nvidia_yearly, ms_yearly, merged_df = load_data()
except Exception as e:
    st.error("데이터 파일을 불러오는 데 실패했습니다. 파일 이름과 경로를 확인해주세요.")
    st.stop()

# --- 사이드바 네비게이션 (2개 이상의 페이지 구성) ---
st.sidebar.title("데이터 분석 메뉴")
page = st.sidebar.radio("페이지 이동", ["1. 프로젝트 개요 및 추이", "2. 상관관계 분석"])

if page == "1. 프로젝트 개요 및 추이":
    st.title("🌱 AI 발전과 탄소 배출량의 상관관계 분석")
    st.markdown("""
    이 프로젝트는 AI 산업을 이끄는 핵심 인프라 기업인 **엔비디아(NVIDIA)의 데이터센터 매출**과 
    클라우드/AI 서비스를 제공하는 **마이크로소프트(Microsoft)의 온실가스(GHG) 배출량**을 비교하여, 
    AI 기술의 눈부신 발전이 환경에 미치는 영향을 분석합니다.
    """)

    st.divider()

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 엔비디아 데이터센터 매출 추이")
        fig1 = px.line(nvidia_yearly, x='Year', y='Nvidia_Revenue_M', markers=True, 
                       title="연도별 매출 (백만 달러)")
        fig1.update_traces(line_color="green")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("☁️ 마이크로소프트 탄소 배출량 추이")
        fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', markers=True, 
                       title="연도별 탄소 배출량 (mtCO2e)")
        fig2.update_traces(line_color="red")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("⚖️ 매출과 탄소 배출량 복합 비교")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=merged_df['Year'], y=merged_df['Nvidia_Revenue_M'], name="NVIDIA 매출", marker_color='green'))
    fig3.add_trace(go.Scatter(x=merged_df['Year'], y=merged_df['MSFT_Emissions'], name="MSFT 탄소배출량", yaxis='y2', line=dict(color='red', width=3), mode='lines+markers'))
    
    fig3.update_layout(
        title="엔비디아 데이터센터 매출 vs 마이크로소프트 탄소배출량",
        yaxis=dict(title="NVIDIA 매출 (백만 달러)"),
        yaxis2=dict(title="MSFT 탄소 배출량 (mtCO2e)", overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig3, use_container_width=True)

elif page == "2. 상관관계 분석":
    st.title("🔍 데이터 상관관계 분석")
    st.markdown("""
    엔비디아의 매출 증가(AI 수요 증가)가 마이크로소프트의 데이터센터 운영으로 인한 탄소 배출량에 
    어떤 직접적인 연관성을 가지는지 산점도와 회귀선을 통해 확인합니다.
    """)

    # 산점도 및 추세선
    fig_scatter = px.scatter(merged_df, x='Nvidia_Revenue_M', y='MSFT_Emissions', 
                             text='Year', trendline='ols',
                             title="NVIDIA 데이터센터 매출 vs Microsoft 탄소 배출량",
                             labels={
                                 'Nvidia_Revenue_M': 'NVIDIA 데이터센터 매출 (백만 달러)',
                                 'MSFT_Emissions': 'Microsoft 온실가스 배출량 (mtCO2e)'
                             })
    fig_scatter.update_traces(textposition='top center', marker=dict(size=10, color='blue'))
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 상관계수 계산
    if not merged_df.empty:
        corr = merged_df['Nvidia_Revenue_M'].corr(merged_df['MSFT_Emissions'])
        st.success(f"💡 **분석 결과:** 두 데이터 간의 상관계수(Pearson)는 **{corr:.3f}** 입니다.")
        
        st.info("""
        **[상관계수 해석 가이드]**
        * **0.7 ~ 1.0**: 매우 강한 양의 상관관계 (AI 발전을 위한 인프라 확장이 탄소 배출 증가와 깊은 연관이 있음)
        * **0.3 ~ 0.7**: 뚜렷한 양의 상관관계
        * **-0.3 ~ 0.3**: 상관관계가 거의 없음
        """)
