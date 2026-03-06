import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import re

# 웹 페이지 설정 (기존 wide 모드 유지)
st.set_page_config(page_title="Tumor Analysis Dashboard", layout="wide")
st.title("📊 Tumor Growth Analysis Dashboard")
st.markdown("엑셀 파일을 업로드하면 자동으로 **성장률 계산, 통계 분석, 그래프**를 생성합니다.")

# 숫자 추출 함수
def extract_number(value):
    if pd.isna(value): return value
    try:
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else None
    except:
        return None

# 파일 업로드
uploaded_file = st.file_uploader("분석할 엑셀 파일을 선택하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    target_cols = ['Group', 'Animal no.']
    df_raw = None
    
    # 헤더 자동 탐색
    for i in range(5):
        try:
            temp_df = pd.read_excel(uploaded_file, header=i)
            temp_df.columns = temp_df.columns.astype(str).str.strip()
            if all(col in temp_df.columns for col in target_cols):
                df_raw = temp_df
                st.success(f"✅ 데이터 구조 확인 완료 (Header Row: {i})")
                break
        except:
            continue

    if df_raw is not None:
        # 데이터 변환 (Wide to Long)
        df_long = df_raw.melt(id_vars=['Group', 'Animal no.'], var_name='Day', value_name='Tumor_Volume')
        
        # 날짜 및 부피 숫자형 변환
        df_long['Day'] = df_long['Day'].apply(extract_number)
        df_long['Tumor_Volume'] = df_long['Tumor_Volume'].apply(extract_number)
        df_long = df_long.dropna(subset=['Day', 'Tumor_Volume'])
        
        # 날짜 정렬 (x축에 실제 측정 날짜 반영을 위함)
        df_long = df_long.sort_values(['Day', 'Group'])

        # 통계 분석 (마지막 측정일 기준)
        last_day = df_long['Day'].max()
        g1_data = df_long[(df_long['Group'] == 'G1') & (df_long['Day'] == last_day)]['Tumor_Volume']
        g2_data = df_long[(df_long['Group'] == 'G2') & (df_long['Day'] == last_day)]['Tumor_Volume']
        
        p_val = None
        if len(g1_data) > 1 and len(g2_data) > 1:
            _, p_val = ttest_ind(g1_data, g2_data, nan_policy='omit')

        # --- 레이아웃 수정: 그래프 아래로 표 이동 ---
        
        # 1. 그래프 영역
        st.subheader("📈 종양 성장 곡선")
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # x축을 실제 측정 날짜(Day) 수치로 표시
        sns.lineplot(
            data=df_long, 
            x='Day', 
            y='Tumor_Volume', 
            hue='Group', 
            marker='o', 
            errorbar='se', 
            err_style='bars',
            err_kws={'capsize': 3},
            ax=ax
        )
        
        stat_title = f"Tumor Growth Curve (p-value at Day {int(last_day)}: {p_val:.4f})" if p_val is not None else "Tumor Growth Curve"
        plt.title(stat_title, fontsize=14)
        plt.xlabel("Day (Actual measurement date)")
        plt.ylabel("Tumor Volume (mm³)")
        plt.grid(True, linestyle
