import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 페이지 기본 설정
st.set_page_config(page_title="NVIDIA Revenue vs MSFT Emissions", layout="wide")

st.title("엔비디아 매출과 마이크로소프트 탄소 배출량 상관관계 분석")
st.write("2019년부터 2024년까지 엔비디아의 데이터센터 매출과 마이크로소프트의 총 탄소 배출량 간의 상관관계를 분석하는 대시보드입니다. **(현재 파일 대신 임의의 가상 데이터를 사용하고 있습니다.)**")

# 임의의 데이터 생성 함수
@st.cache_data
def load_dummy_data():
    years = [2019, 2020, 2021, 2022, 2023, 2024]
    
    # 1. 임의의 NVIDIA 연간 데이터센터 매출 (단위: 백만 달러, 최근 급성장하는 추세 반영)
    nvidia_revenue = [2983, 6696, 10613, 15005, 47525, 104000]
    nvidia_yearly = pd.DataFrame({
        'Year': years,
        '데이터센터 매출 (백만 달러)': nvidia_revenue
    })
    
    # 2. 임의의 Microsoft 연간 총 탄소 배출량 (단위: mtCO2e, 점진적으로 증가하는 추세 반영)
    msft_emissions = [117956, 120500, 125000, 131200, 139000, 146500]
    msft_yearly = pd.DataFrame({
        'Year': years,
        'Total Emissions (mtCO2e)': msft_emissions
    })
    
    # 3. 데이터 병합
    merged_df = pd.merge(nvidia_yearly, msft_yearly, on='Year', how='inner')
    return nvidia_yearly, msft_yearly, merged_df

# 데이터 로드
nvidia_yearly, msft_yearly, merged_df = load_dummy_data()

st.subheader("데이터 미리보기 (가상 데이터)")
col1, col2 = st.columns(2)
with col1:
    st.write("NVIDIA 데이터센터 연간 매출 (백만 달러)")
    st.dataframe(nvidia_yearly.set_index('Year'))
with col2:
    st.write("Microsoft 연간 총 탄소 배출량 (mtCO2e)")
    st.dataframe(msft_yearly.set_index('Year'))

st.subheader("병합된 데이터 (2019-2024)")
st.dataframe(merged_df.set_index('Year'))

st.subheader("매출과 탄소 배출량 추이 비교")
fig, ax1 = plt.subplots(figsize=(10, 5))

# NVIDIA 매출 그래프 (왼쪽 Y축)
color = 'tab:blue'
ax1.set_xlabel('Year')
ax1.set_ylabel('NVIDIA Data Center Revenue ($M)', color=color)
ax1.plot(merged_df['Year'], merged_df['데이터센터 매출 (백만 달러)'], marker='o', color=color, label='NVIDIA Revenue')
ax1.tick_params(axis='y', labelcolor=color)

# Microsoft 탄소 배출량 그래프 (오른쪽 Y축)
ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('MSFT Carbon Emissions (mtCO2e)', color=color)  
ax2.plot(merged_df['Year'], merged_df['Total Emissions (mtCO2e)'], marker='s', color=color, label='MSFT Emissions')
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  
st.pyplot(fig)

st.subheader("상관관계 분석")
correlation = merged_df['데이터센터 매출 (백만 달러)'].corr(merged_df['Total Emissions (mtCO2e)'])
st.write(f"**피어슨 상관계수 (Pearson Correlation Coefficient): {correlation:.4f}**")

st.write("""
* 상관계수가 1에 가까울수록 강한 양의 상관관계(매출이 오를 때 배출량도 오름)를 의미합니다.
* 상관계수가 -1에 가까울수록 강한 음의 상관관계(매출이 오를 때 배출량은 감소함)를 의미합니다.
""")

fig2, ax_scatter = plt.subplots(figsize=(8, 6))
sns.regplot(data=merged_df, x='데이터센터 매출 (백만 달러)', y='Total Emissions (mtCO2e)', ax=ax_scatter)
ax_scatter.set_title("NVIDIA 매출 vs MSFT 탄소 배출량 산점도 및 회귀선")
st.pyplot(fig2)
