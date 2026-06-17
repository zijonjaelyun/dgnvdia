import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 웹페이지 기본 설정
st.set_page_config(
    page_title="BigTech AI & Sustainability Analysis",
    page_icon="🌿",
    layout="wide"
)

# 2. 데이터 로드 및 전처리 함수 (캐싱 적용으로 성능 최적화)
@st.cache_data
def load_and_preprocess_data():
    # ---- (1) 마이크로소프트 탄소 배출 데이터 처리 ----
    # 사용자가 리포지토리에 올려둔 엑셀 파일명 매칭
    ms_file = 'tracenable-ghg-emissions-2019-2024-microsoft-20260617.xlsx'
    df_ms_raw = pd.read_excel(ms_file)
    
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    ms_parsed = []
    
    for y in years:
        # Scope 1 (직접 배출)
        s1 = df_ms_raw[(df_ms_raw['reporting_period'] == y) & (df_ms_raw['metric'] == 'Total Scope 1')]['value'].values[0]
        # Scope 2 (위치 기반 vs 시장 기반)
        s2_loc = df_ms_raw[(df_ms_raw['reporting_period'] == y) & (df_ms_raw['metric'] == 'Total Scope 2') & (df_ms_raw['method'] == 'Location-based')]['value'].values[0]
        s2_mkt = df_ms_raw[(df_ms_raw['reporting_period'] == y) & (df_ms_raw['metric'] == 'Total Scope 2') & (df_ms_raw['method'] == 'Market-based')]['value'].values[0]
        # Scope 3 (공급망 전체 배출)
        s3_all = df_ms_raw[(df_ms_raw['reporting_period'] == y) & (df_ms_raw['metric'] == 'Total Scope 3')]
        if len(s3_all) > 1:
            s3 = s3_all[s3_all['method'] == 'Market-based']['value'].values[0]
        else:
            s3 = s3_all['value'].values[0]
            
        ms_parsed.append({
            'Calendar_Year': y,
            'Scope 1 (직접 배출)': s1,
            'Scope 2 (위치 기반-실제 전력망)': s2_loc,
            'Scope 2 (시장 기반-계약 상쇄)': s2_mkt,
            'Scope 3 (공급망/가치사슬)': s3,
            'Total_Carbon_Market': s1 + s2_mkt + s3
        })
    df_ms_clean = pd.DataFrame(ms_parsed)

    # ---- (2) 엔비디아 분기 매출 데이터 처리 ----
    df_nvda_raw = pd.read_csv('nvidia.csv')
    
    # NVIDIA 회계분기(FY) 스트링에서 달력 연도(Calendar Year) 매칭 연산 고도화
    # 예: 'Q1 FY24' -> 2023년 하반기~2024년 초에 걸쳐 있으므로 하드웨어 인프라 주기 고려해 매핑
    def to_calendar_year(row):
        q_str = str(row['NVIDIA 회계분기'])
        fy_val = int(q_str.split('FY')[-1])
        return 2000 + fy_val - 1

    df_nvda_raw['Calendar_Year'] = df_nvda_raw.apply(to_calendar_year, axis=1)
    
    # 연도별로 그룹화하여 데이터센터 총 매출액 연산 (백만 달러 -> 십억 달러 단위 변경)
    df_nvda_annual = df_nvda_raw.groupby('Calendar_Year')['데이터센터 매출 (백만 달러)'].sum().reset_index()
    df_nvda_annual['NVDA_데이터센터_매출_십억달러'] = df_nvda_annual['데이터센터 매출 (백만 달러)'] / 1000

    # ---- (3) 데이터 병합 (2019-2024 통합분석용) ----
    df_merged = pd.merge(df_nvda_annual, df_ms_clean, on='Calendar_Year')
    
    return df_ms_clean, df_nvda_raw, df_merged

# 데이터 파싱 시작
try:
    df_ms, df_nvda_raw, df_combined = load_and_preprocess_data()
except Exception as e:
    st.error(f"⚠️ 리포지토리 내의 CSV/공시 엑셀 파일을 로드하는 중에 오류가 발생했습니다. 파일명을 다시 한번 확인해 주세요. 오류내용: {e}")
    st.stop()


# 3. 사이드바 - 페이지 네비게이션 컨트롤러
st.sidebar.title("🍀 대시보드 메뉴")
page = st.sidebar.selectbox(
    "이동할 분석 페이지를 선택하세요:",
    ["🏠 프로젝트 소개 및 팀 정보", "📊 [Page 1] MSFT 탄소 배출 분석", "📈 [Page 2] NVDA 매출-탄소배출 상관분석"]
)

# 사이드바 하단 팀 정보 위젯 고정 노출
st.sidebar.markdown("---")
st.sidebar.markdown("""
**🎯 프로젝트 수행 팀원**
- **20706 김은택**: 데이터 분석 구조 및 백엔드 로직 연산 총괄
- **20415 신재륜**: UI 아키텍처 구현 및 인터랙티브 시각화 최적화
""")


# ==========================================
# 🏠 [메인 탭] 프로젝트 소개 및 팀 정보
# ==========================================
if page == "🏠 프로젝트 소개 및 팀 정보":
    st.title("🌿 빅테크 AI 성장과 지속가능성 종합 분석 시스템")
    st.subheader("마이크로소프트 탄소 발자국과 엔비디아 매출 데이터의 연계 융합 분석")
    
    st.markdown("""
    <div style="background-color:#f1f3f6; padding:22px; border-radius:12px; margin-bottom: 25px; border-left: 5px solid #2E7D32;">
        <h4 style="margin-top:0; color:#2E7D32;">💡 분석 시스템 개발 개요</h4>
        <p style="font-size: 15px; color:#333; line-height:1.6;">
            챗GPT 출시 이후 가속화된 <b>생성형 AI 패러다임</b>은 초거대 데이터 센터 인프라의 폭발적인 확장을 요구하고 있습니다. 
            이에 따라 빅테크 기업들이 선언했던 '2030 탄소 중립(Carbon Negative)' 선언에 비상등이 켜졌습니다. <br>
            본 시스템은 <b>AI 가속기(GPU) 하드웨어 시장을 독점하는 NVIDIA의 매출</b> 지표와 
            <b>글로벌 거대 클라우드 인프라를 운영하는 Microsoft의 실제 환경 공시 데이터</b>를 상호 매칭하여, 
            가속화되는 인공지능 혁신 속에 가려진 환경적 부담을 통계적·시각적으로 분석하고자 설계되었습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.info("### 📂 활용 데이터셋 안내\n"
                "1. **`tracenable-ghg-emissions-2019-2024-microsoft-20260617.xlsx`**\n"
                "   - 마이크로소프트의 공식 지속가능성 보고서 기반 온실가스 데이터 파싱 (Scope 1, 2, 3)\n"
                "2. **`nvidia.csv`**\n"
                "   - 엔비디아의 분기별 실적 보고서(SEC Filings) 내 데이터센터 부문 핵심 매출액 정보")
                
    with col_t2:
        st.success("### 👥 연구 수행 팀원 및 역할\n"
                   "- **20706 김은택**:\n"
                   "  - 데이터 전처리 파이프라인 수립 및 회계연도 타임라인 매칭 로직 개발\n"
                   "- **20415 신재륜**:\n"
                   "  - Streamlit 대시보드 컴포넌트 프론트엔드 최적화 및 Plotly 다중 차트 구현")

    st.markdown("---")
    st.markdown("👈 왼쪽 사이드바의 **페이지 선택 메뉴**를 통해 분석 컴포넌트를 탐색할 수 있습니다.")


# ==========================================
# 📊 [Page 1] MSFT 탄소 배출 분석
# ==========================================
elif page == "📊 [Page 1] MSFT 탄소 배출 분석":
    st.title("📊 [Page 1] 마이크로소프트(MSFT) 온실가스 배출 심층 분석")
    st.markdown("마이크로소프트의 공시 데이터를 기반으로 연도별 직접·간접 탄소 배출 추이를 추적합니다.")
    
    # 최신 연도 기준 KPI 메트릭 계산
    latest_row = df_ms.iloc[-1]
    prev_row = df_ms.iloc[0]
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(
            label="2024년 총 배출량 (시장 기반 장부 기준)", 
            value=f"{latest_row['Total_Carbon_Market']:,} mtCO2e",
            delta=f"2019년 대비 {((latest_row['Total_Carbon_Market']/prev_row['Total_Carbon_Market'])-1)*100:.1f}% 증가",
            delta_color="inverse"
        )
    with kpi2:
        st.metric(
            label="2024년 실제 전력 그리드 부하 (위치 기반 Scope 2)", 
            value=f"{latest_row['Scope 2 (위치 기반-실제 전력망']:,} mtCO2e",
            delta=f"2019년 대비 {((latest_row['Scope 2 (위치 기반-실제 전력망)']/prev_row['Scope 2 (위치 기반-실제 전력망)'])-1)*100:.1f}% 증가",
            delta_color="inverse"
        )
    with kpi3:
        st.metric(
            label="2024년 공급망 전체 간접 배출 (Scope 3)", 
            value=f"{latest_row['Scope 3 (공급망/가치사슬)'].iloc[-1]:,} mtCO2e" if isinstance(latest_row['Scope 3 (공급망/가치사슬)'], pd.Series) else f"{latest_row['Scope 3 (공급망/가치사슬)']:,} mtCO2e"
        )

    # 시각화 1: 세부 스코프 누적 막대 그래프
    st.subheader("1. 연도별 탄소 배출 구성비 추이 (Scope 1, 2, 3)")
    df_melted = df_ms.melt(id_vars=['Calendar_Year'], value_vars=['Scope 1 (직접 배출)', 'Scope 2 (시장 기반-계약 상쇄)', 'Scope 3 (공급망/가치사슬)'],
                             var_name='배출 유형(Scope)', value_name='배출량 (mtCO2e)')
    
    fig_bar = px.bar(
        df_melted, x='Calendar_Year', y='배출량 (mtCO2e)', color='배출 유형(Scope)',
        title="마이크로소프트 연도별 온실가스(GHG) 총합 그래프",
        barmode='stack',
        labels={'Calendar_Year': '연도'},
        color_discrete_sequence=['#42A5F5', '#66BB6A', '#FFA726']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # 시각화 2: 전력 매칭 격차 트렌드
    st.subheader("2. 전력 소비의 역설: 위치 기반 vs 시장 기반 격차")
    st.markdown("""
    - **위치 기반(Location-based)**: 데이터 센터가 구축된 지역 전력 그리드의 실제 화석연료 발전 비율을 반영한 **물리적 배출량**입니다.
    - **시장 기반(Market-based)**: 신재생에너지 공급인증서(REC) 구매 및 녹색 요금제 계약을 통해 서류상으로 상쇄 처리한 **장부상 배출량**입니다.
    """)
    
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=df_ms['Calendar_Year'], y=df_ms['Scope 2 (위치 기반-실제 전력망)'], name='위치 기반 (실제 그리드 탄소 유출)', line=dict(color='#E53935', width=4)))
    fig_line.add_trace(go.Scatter(x=df_ms['Calendar_Year'], y=df_ms['Scope 2 (시장 기반-계약 상쇄)'], name='시장 기반 (장부 계약상 상쇄 배출)', line=dict(color='#1E88E5', width=4, dash='dash')))
    fig_line.update_layout(title='인프라 폭증에 따른 전력 탄소 디커플링 현상', xaxis_title='연도', yaxis_title='배출량 (mtCO2e)')
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("📋 Microsoft 온실가스 전처리 데이터 요약")
    st.dataframe(df_ms.style.format(comma=True), use_container_width=True)


# ==========================================
# 📈 [Page 2] NVDA 매출-탄소배출 상관분석
# ==========================================
elif page == "📈 [Page 2] NVDA 매출-탄소배출 상관분석":
    st.title("📈 [Page 2] NVIDIA 매출 성장과 MSFT 탄소 발자국 상관관계 분석")
    st.markdown("하드웨어 공급 인프라의 성장 곡선이 대형 하이퍼스케일러의 전력 환경 지표와 어떤 흐름으로 맞물리는지 분석합니다.")

    # 세부 탭 분할 구성 (NVIDIA 단독 분기 매출 + 결합 이중축 분석)
    sub_tab1, sub_tab2 = st.tabs(["🎮 NVIDIA 분기별 매출 분석", "📊 하드웨어 매출-탄소배출 융합 분석"])
    
    with sub_tab1:
        st.subheader("NVIDIA 회계분기별 데이터센터 매출 추이")
        fig_nvda_quarter = px.line(
            df_nvda_raw, x='NVIDIA 회계분기', y='데이터센터 매출 (백만 달러)',
            title="엔비디아 분기별 데이터센터 부문 매출 폭발 구간 시각화",
            markers=True, color_discrete_sequence=['#76B900']
        )
        st.plotly_chart(fig_nvda_quarter, use_container_width=True)
        st.caption("※ 2022년 말(FY23~FY24 구간) ChatGPT 등장 이후 급격하게 꺾여 올라가는 수직성장 패턴 확인 가능.")
        
    with sub_tab2:
        st.subheader("AI 공급(NVIDIA 매출) vs 인프라 실제 가동 부하(MSFT 전력배출)")
        
        # 이중 축(Dual-axis) 차트 생성
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 바 차트: 엔비디아 연간 데이터센터 매출
        fig_dual.add_trace(
            go.Bar(
                x=df_combined['Calendar_Year'], y=df_combined['NVDA_DC_Revenue_Billion'],
                name="NVIDIA 데이터센터 매출액 (십억달러)", marker_color='#76B900', opacity=0.8
            ), secondary_y=False
        )
        
        # 라인 차트: MSFT 전력 배출량 (Location-based)
        fig_dual.add_trace(
            go.Scatter(
                x=df_combined['Calendar_Year'], y=df_combined['MSFT_Scope2_Location'],
                name="MSFT Scope 2 (위치기반 실제배출, mtCO2e)", line=dict(color='#00A4EF', width=4)
            ), secondary_y=True
        )
        
        fig_dual.update_layout(
            title_text="<b>NVIDIA 인프라 공급 실적과 MSFT 전력 소모 온실가스의 시계열 동기화 추세</b>",
            xaxis_title="연도 (Calendar Year)",
            legend=dict(x=0.01, y=0.99)
        )
        
        fig_dual.update_yaxes(title_text="<b>NVIDIA 데이터센터 연 매출액 ($ Billion)</b>", secondary_y=False)
        fig_dual.update_yaxes(title_text="<b>MSFT 위치기반 배출량 (mtCO2e)</b>", secondary_y=True)
        
        st.plotly_chart(fig_dual, use_container_width=True)
        
        # 피어슨 상관계수 통계 연산 및 인사이트 리포트 위젯
        corr_coef = df_combined['NVDA_DC_Revenue_Billion'].corr(df_combined['MSFT_Scope2_Location'])
        
        st.markdown("---")
        st.subheader("💡 정량적 분석 인사이트 요약")
        
        c_box1, c_box2 = st.columns([1, 2])
        with c_box1:
            st.markdown(f"""
            <div style="background-color:#fff3cd; padding:25px; border-radius:12px; text-align:center; border: 1px solid #ffeeba;">
                <b style="color:#856404; font-size:14px;">두 핵심 지표 간 통계적 상관계수</b>
                <h2 style="color:#856404; margin:10px 0; font-size:46px;">{corr_coef:.3f}</h2>
                <p style="margin:0; font-size:12px; color:#777;">Pearson Correlation Coefficient</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_box2:
            st.markdown(f"""
            1. **강한 양의 선형 상관관계**: 상관계수가 **{corr_coef:.3f}**라는 수치는 두 통계 변수가 거의 완벽히 비례하여 움직이고 있음을 입증합니다.
            2. **인프라 폭발의 동기화 현상**: 엔비디아의 하드웨어 공급 가속화 시점(2022~2024년)과 마이크로소프트의 실제 발전 그리드 소모량(Scope 2 Location-based)의 폭증 시점이 명확하게 맞물려 떨어집니다.
            3. **지속가능성 선언의 장벽**: 서류상 상쇄(Market-based) 계약을 적극적으로 진행하더라도, 실제 인프라 확장으로 가해지는 물리적인 전력 사용 리스크는 고성능 하드웨어 수요 성장 곡선에 직결되어 증가함을 시사합니다.
            """)

        st.subheader("📋 연도별 융합 지표 결합 매칭 데이터프레임")
        st.dataframe(
            df_combined.style.format({
                'Calendar_Year': '{:4d}년',
                '데이터센터 매출 (백만 달러)': '{:,} $M',
                'NVDA_DC_Revenue_Billion': '{:.2f} $B',
                'MSFT_Scope2_Location': '{:,} mtCO2e',
                'MSFT_Scope2_Market-based': '{:,} mtCO2e',
                'MSFT_Scope3': '{:,} mtCO2e'
            }), use_container_width=True
        )
