# NVIDIA Revenue vs Microsoft GHG Emissions Analyzer

## 프로젝트 소개
본 프로젝트는 **2019년부터 2024년까지 엔비디아(NVIDIA)의 데이터센터 매출량**과 **마이크로소프트(Microsoft)의 총 탄소 배출량** 간의 상관관계를 시각화하고 분석하는 Streamlit 웹 애플리케이션입니다. 
AI 산업의 발전으로 인한 데이터센터의 폭발적인 성장과 그에 따른 빅테크 기업의 환경적 영향(탄소 배출량) 변화 추이를 살펴보고 통계적 상관관계를 도출합니다.

## 개발자 역할 (팀원)
* **김은택**: 
  - 데이터 전처리 파이프라인 구축 (회계연도 변환 및 연도별 그룹핑)
  - 두 기업 데이터셋 병합 및 피어슨 상관계수(Pearson Correlation) 도출 알고리즘 작성
* **신재륜**: 
  - Streamlit 대시보드 레이아웃 및 UI/UX 설계
  - Matplotlib, Seaborn을 활용한 데이터 시각화 구현 (이중 Y축 꺾은선 그래프, 산점도 및 선형 회귀선)

## 설치 및 실행 방법

1. 필수 패키지 설치
```bash
pip install -r requirements.txt
