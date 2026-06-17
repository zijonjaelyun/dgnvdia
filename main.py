import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI & 탄소 배출 분석 리포트", layout="wide")

@st.cache_data
def load_and_process():
    # utf-8-sig는 한글 깨짐을 방지하는 가장 안전한 인코딩입니다.
    nvidia_df = pd.read_csv("nvidia.csv", encoding='utf-8-sig')
    ms_df = pd.read_csv("msft.csv", encoding='utf-8-sig')

    # 데이터 전처리: 연도 추출 및 합산
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    return nvidia_yearly, ms_yearly, merged_df

nvidia_yearly, ms_yearly, merged_df = load_and_process()

# --- 앱 시작 ---
st.title("📊 AI 기술 성장과 환경적 비용: 상관관계 심층 분석")
st.markdown("본 프로젝트는 NVIDIA의 데이터센터 매출 성장이 Microsoft의 탄소 배출량에 미치는 영향을 데이터 기반으로 분석합니다.")

# 1. 시각화 섹션
col1, col2 = st.columns(2)
with col1:
    fig1 = px.line(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', title="NVIDIA 데이터센터 매출 성장세", markers=True)
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', title="Microsoft 총 온실가스 배출량 추이", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# 2. 분석 및 해석 섹션 (가장 중요한 부분)
st.divider()
st.subheader("💡 데이터 분석 인사이트")

corr = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['MSFT_Emissions'])

st.markdown(f"""
### 1. 통계적 상관관계: {corr:.3f}
* **상관계수 해석:** 두 변수 사이의 상관계수가 **{corr:.3f}**로 나타납니다. 
* 이는 AI 인프라(엔비디아)에 대한 투자가 클라우드 사업자(마이크로소프트)의 운영 탄소 배출 증가와 **강한 양의 상관관계**를 가짐을 시사합니다.
""")

st.info("""
### 2. 시사점 (AI 기술과 환경의 딜레마)
* **인프라 확장의 그림자:** AI 모델의 학습과 운영을 위한 연산 능력(NVIDIA 매출)이 폭발적으로 증가함에 따라, 
  이를 구동하는 데이터센터의 에너지 소모도 가파르게 상승하고 있습니다.
* **Scope 3 배출의 중요성:** 마이크로소프트와 같은 기업은 직접적인 탄소 배출(Scope 1, 2)보다 제품 생애주기 전반의 배출(Scope 3) 비중이 큽니다. 
  AI 칩 생산부터 데이터센터 구축까지의 공급망 전반에서 발생하는 '간접 탄소' 관리가 핵심 과제입니다.
""")

st.success("""
### 3. 프로젝트 결론 및 제언
* **결론:** AI 산업의 성장은 필연적으로 막대한 에너지를 소모하며, 이는 환경적 발자국으로 귀결됩니다. 
  데이터 분석 결과, AI 인프라 성장은 탄소 배출을 억제해야 하는 기업의 ESG 목표와 직접적인 충돌을 일으키고 있습니다.
* **제언:** 앞으로 AI 기업들은 단순히 '매출 성장'만 추구할 것이 아니라, 고효율 연산 알고리즘 개발 및 재생 에너지 기반의 
  데이터센터 운영(Net-Zero 달성) 전략을 기술적 우선순위에 두어야 합니다.
""")
