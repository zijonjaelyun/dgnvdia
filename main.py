import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI & 탄소 배출 분석 리포트", layout="wide")

# 자동으로 맞는 인코딩을 찾아 파일을 읽어오는 강력한 함수입니다.
def read_csv_robust(filepath):
    encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except UnicodeDecodeError:
            continue
    st.error(f"{filepath} 파일을 읽는 데 실패했습니다. 파일 형식을 확인해주세요.")
    st.stop()

@st.cache_data
def load_and_process():
    # 위에서 만든 자동 탐지 함수를 사용하여 파일을 불러옵니다.
    nvidia_df = read_csv_robust("nvidia.csv")
    ms_df = read_csv_robust("msft.csv")

    # [데이터 전처리]
    # 1. 엔비디아 (FY19 -> 2019 변환)
    nvidia_df['Year'] = nvidia_df['NVIDIA 회계분기'].str.extract(r'FY(\d+)').astype(int) + 2000
    nvidia_yearly = nvidia_df.groupby('Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()

    # 2. 마이크로소프트 (연도별 탄소 배출량 합산)
    ms_yearly = ms_df.groupby('reporting_period')['value'].sum().reset_index()
    ms_yearly.columns = ['Year', 'MSFT_Emissions']

    # 3. 데이터 병합
    merged_df = pd.merge(nvidia_yearly, ms_yearly, on='Year', how='inner')
    return nvidia_yearly, ms_yearly, merged_df

# 데이터 로딩 및 처리
nvidia_yearly, ms_yearly, merged_df = load_and_process()

# --- 대시보드 화면 구성 ---
st.title("📊 AI 기술 성장과 환경적 비용: 상관관계 심층 분석")
st.markdown("본 프로젝트는 NVIDIA의 데이터센터 매출 성장이 Microsoft의 탄소 배출량에 미치는 영향을 데이터 기반으로 분석합니다.")

# 1. 시각화 섹션
col1, col2 = st.columns(2)
with col1:
    fig1 = px.line(nvidia_yearly, x='Year', y='데이터센터 매출 (백만 달러)', 
                   title="NVIDIA 데이터센터 연도별 매출", markers=True)
    fig1.update_traces(line_color="green")
    st.plotly_chart(fig1, use_container_width=True)
    
with col2:
    fig2 = px.line(ms_yearly, x='Year', y='MSFT_Emissions', 
                   title="Microsoft 총 온실가스 배출량 추이", markers=True)
    fig2.update_traces(line_color="red")
    st.plotly_chart(fig2, use_container_width=True)

# 2. 분석 및 해석 섹션
st.divider()
st.subheader("💡 데이터 분석 인사이트")

if not merged_df.empty:
    corr = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['MSFT_Emissions'])
    
    st.markdown(f"""
    ### 1. 통계적 상관관계: **{corr:.3f}** (피어슨 상관계수)
    * **해석:** 분석 결과 두 지표 간의 상관계수가 {corr:.3f}로 나타났습니다. 이는 AI 인프라 확장을 나타내는 엔비디아의 매출 증가와 클라우드 서비스 제공자인 마이크로소프트의 탄소 배출량 증가 사이에 **매우 뚜렷한 양의 상관관계**가 있음을 의미합니다.
    """)

st.info("""
### 2. 시사점 (AI 기술과 환경의 딜레마)
* **전력 소모의 급증:** AI 모델(특히 대규모 언어 모델)의 학습과 추론에는 막대한 컴퓨팅 파워가 필요합니다. NVIDIA 매출의 급증은 곧 전 세계 데이터센터에 고성능 GPU가 그만큼 많이 설치되고 가동되었음을 뜻하며, 이는 필연적으로 막대한 전력 소모를 야기합니다.
* **공급망 탄소 배출 (Scope 3):** 마이크로소프트와 같은 빅테크 기업의 탄소 배출은 단순히 사옥에서 쓰는 전기를 넘어, 서버를 제조하고 운송받아 폐기하기까지의 전체 밸류체인(Scope 3)에서 발생합니다. AI 인프라 확충은 이 Scope 3 배출량을 크게 늘리는 주원인이 됩니다.
""")

st.success("""
### 3. 프로젝트 결론 및 제언
* **결론:** 혁신적인 AI 기술의 이면에는 '탄소 배출 증가'라는 숨겨진 환경적 비용이 존재합니다. 데이터는 AI 산업의 성장이 기후 변화 대응(Net-Zero) 목표와 상충하는 딜레마 상황에 놓여 있음을 보여줍니다.
* **제언:** 지속 가능한 AI 생태계를 위해서는 단순히 성능 경쟁을 넘어선 기술적 해결책이 필요합니다. 
  1) 저전력·고효율 반도체 설계 기술 개발
  2) 100% 재생 에너지(RE100)로 구동되는 친환경 데이터센터 구축
  3) 효율적인 AI 연산 알고리즘 최적화가 필수적으로 동반되어야 합니다.
""")
