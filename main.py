import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="NVIDIA 매출 vs Microsoft 탄소 배출량 상관관계 분석",
    page_icon="📊",
    layout="wide",
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

MS_METRIC_LABELS = {
    "scope1_tco2e": "Scope 1 (직접 배출)",
    "scope2_market_based_tco2e": "Scope 2 - Market-based (간접 배출)",
    "scope2_location_based_tco2e": "Scope 2 - Location-based (간접 배출)",
    "scope3_tco2e": "Scope 3 (기타 간접 배출)",
    "total_tco2e": "총 배출량 (Scope1+2(Market)+3)",
}


# ----------------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    nvidia_q = pd.read_csv(os.path.join(DATA_DIR, "nvidia_revenue.csv"))
    ms_annual = pd.read_csv(os.path.join(DATA_DIR, "microsoft_emissions.csv"))

    # NVIDIA 분기 데이터 -> 회계연도(FY) 합산
    nvidia_annual = (
        nvidia_q.groupby("fiscal_year", as_index=False)["revenue_million_usd"]
        .sum()
        .rename(columns={"fiscal_year": "year", "revenue_million_usd": "nvidia_datacenter_revenue_musd"})
    )

    merged = pd.merge(nvidia_annual, ms_annual, on="year", how="inner").sort_values("year")
    return nvidia_q, nvidia_annual, ms_annual, merged


nvidia_q, nvidia_annual, ms_annual, merged = load_data()

# ----------------------------------------------------------------------------
# 사이드바
# ----------------------------------------------------------------------------
st.sidebar.header("⚙️ 분석 설정")

ms_metric = st.sidebar.selectbox(
    "Microsoft 탄소 배출 지표 선택",
    options=list(MS_METRIC_LABELS.keys()),
    format_func=lambda x: MS_METRIC_LABELS[x],
    index=4,
)

corr_method = st.sidebar.radio(
    "상관계수 종류",
    options=["pearson", "spearman"],
    format_func=lambda x: "피어슨 (선형 상관)" if x == "pearson" else "스피어만 (순위 상관)",
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "⚠️ 분석 기간은 2019~2024년(6개 연도)으로, 표본 크기가 매우 작습니다. "
    "상관계수는 참고용이며 인과관계를 의미하지 않습니다."
)
st.sidebar.caption(
    "ℹ️ NVIDIA 매출은 회계연도(FY, 회계연도 마감 1월) 기준이고 "
    "Microsoft 배출량은 보고연도 기준이라 정확한 캘린더 연도와는 약간의 시차가 있을 수 있습니다."
)

# ----------------------------------------------------------------------------
# 타이틀 & 인트로
# ----------------------------------------------------------------------------
st.title("📊 NVIDIA 데이터센터 매출 × Microsoft 탄소 배출량 상관관계 분석")
st.markdown(
    """
AI 붐을 이끄는 **NVIDIA의 데이터센터 매출**과, 그 AI 인프라를 대규모로 운용하는
**Microsoft의 온실가스(GHG) 배출량**이 함께 움직이는지를 2019년~2024년 데이터로 살펴봅니다.
"""
)

# ----------------------------------------------------------------------------
# 핵심 지표 카드
# ----------------------------------------------------------------------------
x = merged["nvidia_datacenter_revenue_musd"].values
y = merged[ms_metric].values

if corr_method == "pearson":
    corr, p_value = stats.pearsonr(x, y)
else:
    corr, p_value = stats.spearmanr(x, y)

col1, col2, col3 = st.columns(3)
col1.metric("상관계수 (r)", f"{corr:.3f}")
col2.metric("p-value", f"{p_value:.3f}")
col3.metric("R² (설명력)", f"{corr**2:.3f}")

if p_value < 0.05:
    significance_text = "통계적으로 유의미한 상관관계가 관찰됩니다 (p < 0.05)."
else:
    significance_text = "통계적으로 유의미하다고 보기는 어렵습니다 (p ≥ 0.05). 표본이 6개뿐이라 해석에 주의가 필요합니다."

if corr > 0.7:
    strength_text = "강한 양의 상관관계"
elif corr > 0.3:
    strength_text = "중간 정도의 양의 상관관계"
elif corr > -0.3:
    strength_text = "거의 상관관계 없음"
elif corr > -0.7:
    strength_text = "중간 정도의 음의 상관관계"
else:
    strength_text = "강한 음의 상관관계"

st.info(f"**해석:** {strength_text}로 나타납니다. {significance_text}")

st.markdown("---")

# ----------------------------------------------------------------------------
# 탭 구성
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 시계열 비교", "🔍 산점도 & 회귀선", "🧮 전체 지표 상관관계", "📋 원본 데이터"])

# --- 탭 1: 시계열 비교 (이중 축) ---
with tab1:
    st.subheader("연도별 추이 비교 (이중 축)")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=merged["year"],
            y=merged["nvidia_datacenter_revenue_musd"],
            name="NVIDIA 데이터센터 매출 (백만 달러)",
            marker_color="#76B900",
            yaxis="y1",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=merged["year"],
            y=merged[ms_metric],
            name=f"Microsoft {MS_METRIC_LABELS[ms_metric]} (tCO2e)",
            mode="lines+markers",
            line=dict(color="#00A4EF", width=3),
            marker=dict(size=9),
            yaxis="y2",
        )
    )
    fig.update_layout(
        xaxis=dict(title="연도", dtick=1),
        yaxis=dict(title="NVIDIA 매출 (백만 달러)", side="left"),
        yaxis2=dict(title="Microsoft 배출량 (tCO2e)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=500,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 탭 2: 산점도 & 회귀선 ---
with tab2:
    st.subheader("산점도 & 선형 회귀선")

    slope, intercept, r_value, p_value_lr, std_err = stats.linregress(x, y)
    line_x = np.linspace(x.min(), x.max(), 100)
    line_y = slope * line_x + intercept

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers+text",
            text=merged["year"].astype(str),
            textposition="top center",
            marker=dict(size=12, color="#76B900"),
            name="연도별 데이터",
        )
    )
    fig2.add_trace(
        go.Scatter(
            x=line_x,
            y=line_y,
            mode="lines",
            line=dict(color="#00A4EF", dash="dash"),
            name=f"회귀선 (y = {slope:.2f}x + {intercept:,.0f})",
        )
    )
    fig2.update_layout(
        xaxis_title="NVIDIA 데이터센터 매출 (백만 달러)",
        yaxis_title=f"Microsoft {MS_METRIC_LABELS[ms_metric]} (tCO2e)",
        height=500,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.caption(f"결정계수 R² = {r_value**2:.3f}")

# --- 탭 3: 전체 지표 상관관계 히트맵 ---
with tab3:
    st.subheader("NVIDIA 매출 vs Microsoft 배출 지표 전체 상관관계")

    corr_cols = ["nvidia_datacenter_revenue_musd"] + list(MS_METRIC_LABELS.keys())
    corr_matrix = merged[corr_cols].corr(method=corr_method)

    labels = ["NVIDIA 매출"] + [MS_METRIC_LABELS[c] for c in MS_METRIC_LABELS]

    fig3 = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=labels,
            y=labels,
            colorscale="RdBu",
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
        )
    )
    fig3.update_layout(height=550)
    st.plotly_chart(fig3, use_container_width=True)

# --- 탭 4: 원본 데이터 ---
with tab4:
    st.subheader("병합된 연간 데이터 (2019~2024)")
    st.dataframe(merged, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**NVIDIA 분기별 데이터센터 매출**")
        st.dataframe(nvidia_q, use_container_width=True)
    with col_b:
        st.markdown("**Microsoft 연간 온실가스 배출량**")
        st.dataframe(ms_annual, use_container_width=True)

    st.download_button(
        "병합 데이터 CSV 다운로드",
        merged.to_csv(index=False).encode("utf-8-sig"),
        file_name="nvidia_microsoft_merged.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption(
    "데이터 출처: NVIDIA 데이터센터 매출(분기 실적 발표 자료), "
    "Microsoft 온실가스 배출량(Tracenable GHG Emissions 데이터, 2019~2024)."
)
