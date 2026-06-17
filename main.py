import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="AI & 탄소 배출량 분석", layout="wide")

@st.cache_data
def load_and_process():
    # 인코딩 오류 방지: 'cp949'는 윈도우 한글 인코딩 표준입니다.
    # 만약 'cp949'에서도 오류가 난다면 'euc-kr'로 변경해 보세요.
    nvidia_df = pd.read_csv("nvidia.csv", encoding='cp949')
    ms_df = pd.read_csv("msft.csv", encoding='cp949')

    # [엔비디아 데이터 전처리]
    # 회계분기에서 연도만 추출 (FY26 -> 2026)
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    # [마이크로소프트 데이터 전처리]
    # reporting_period 별로 value 합산
    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    # 연도 기준 병합
    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    
    return nvidia_yearly, ms_yearly, merged_df

# 데이터 처리 실행
try:
    nvidia_yearly, ms_yearly, merged_df = load_and_process()
    
    # --- 대시보드 UI ---
    st.title("🌱 AI 기술 성장과 탄소 배출량 관계 분석")
    tab1, tab2 = st.tabs(["📊 지표 추이", "📈 상관관계 분석"])

    with tab1:
        st.subheader("연도별 주요 지표 변화")
        fig1 = px.line(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', markers=True, title="NVIDIA 데이터센터 매출 (연간 합계)")
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', markers=True, title="Microsoft 총 온실가스 배출량 (mtCO2e)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("데이터센터 매출과 탄소 배출량의 상관관계")
        fig3 = px.scatter(merged_df, x='데이터센터 매출 (백만 달러)', y='MSFT_Emissions', 
                          trendline="ols", text="Year", title="매출 증가에 따른 탄소 배출량 추이")
        st.plotly_chart(fig3, use_container_width=True)
        
        corr = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['MSFT_Emissions'])
        st.metric("피어슨 상관계수", f"{corr:.4f}")
        
except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("파일 인코딩 문제일 가능성이 높습니다. 엑셀에서 파일을 열어 '다른 이름으로 저장' -> 'CSV UTF-8(쉼표로 분리)(*.csv)'로 다시 저장 후 업로드해보세요.")
