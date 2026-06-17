import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="AI & 탄소 배출 분석 리포트", page_icon="🌱", layout="wide")

# --- 데이터 불러오기 함수 (자동 인코딩 탐지) ---
def read_csv_robust(filepath):
    encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except UnicodeDecodeError:
            continue
    st.error(f"{filepath} 파일을 읽는 데 실패했습니다.")
    st.stop()

@st.cache_data
def load_and_process():
    nvidia_df = read_csv_robust("nvidia.csv")
    ms_df = read_csv_robust("msft.csv")

    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    return nvidia_yearly, ms_yearly, merged_df

nvidia_yearly, ms_yearly, merged_df = load_and_process()

# --- 첫 번째 페이지 화면 구성 ---
st.title("📊 AI 기술 성장과 환경적 비용 추이")
st.markdown("""
**[교과 융합 프로젝트: 정보과학 × 생태와 환경]** 왼쪽 사이드바를 통해 **1. 지표 추이 분석(현재 페이지)**과 **2. 상관관계 분석**을 확인하실 수 있습니다.
""")

st.divider()
st.subheader("📈 연도별 주요 지표 변화")

col1, col2 = st.columns(2)
with col1:
    fig1 = px.line(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', 
                   title="NVIDIA 데이터센터 연간 매출 추이", markers=True)
    fig1.update_traces(line_color="green")
    st.plotly_chart(fig1, use_container_width=True)
    
with col2:
    fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', 
                   title="Microsoft 총 온실가스 배출량 추이", markers=True)
    fig2.update_traces(line_color="red")
    st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **그래프 해석:** 두 그래프 모두 시간이 지남에 따라(특히 AI가 본격화된 최근 연도에) 우상향하는 모습을 보이고 있습니다. 정확한 연관성은 다음 페이지에서 확인하세요.")
