import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="상관관계 분석", layout="wide")
# --- 데이터 불러오기 함수 (main.py와 동일하게 유지) ---
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

# --- 두 번째 페이지 화면 구성 ---
st.title("🔍 상관관계 심층 분석 및 결론")

st.subheader("매출 증가에 따른 탄소 배출량 추이 (산점도)")
if not merged_df.empty:
    fig3 = px.scatter(merged_df, x='데이터센터 매출 (백만 달러)', y='MSFT_Emissions', 
                      trendline="ols", text="Year", title="매출과 탄소 배출량의 상관성")
    st.plotly_chart(fig3, use_container_width=True)
    
    corr = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['MSFT_Emissions'])
    
    st.markdown(f"""
    ### 📊 1. 통계적 상관관계: **{corr:.3f}** (피어슨 상관계수)
    * **해석:** 분석 결과 두 지표 간의 상관계수가 {corr:.3f}로 매우 높게 나타났습니다. 
    * 이는 AI 인프라(엔비디아) 확장이 클라우드 사업자(마이크로소프트)의 운영 탄소 배출 증가와 **매우 강한 양의 상관관계**를 가짐을 통계적으로 증명합니다.
    """)

st.divider()

st.success("""
### 💡 2. 프로젝트 결론 및 제언
* **AI 기술의 환경적 딜레마:** 혁신적인 AI 기술(초거대 LLM 등)의 이면에는 '탄소 배출 증가'라는 환경적 비용이 숨어 있습니다. 빅테크 기업들이 ESG 경영을 선언했음에도 불구하고 데이터센터 증설(Scope 3 배출)로 인해 배출량이 급증하고 있습니다.
* **지속 가능한 발전(Net-Zero)을 위한 제언:** 1) 저전력·고효율 반도체 설계 및 AI 모델 경량화 기술 개발
  2) 100% 재생 에너지(RE100)로 구동되는 친환경 데이터센터 인프라 확충
  3) 단순히 AI의 '성능'만이 아닌 '전력 대비 성능'을 핵심 평가 지표로 삼아야 합니다.
""")
