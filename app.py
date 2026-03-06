import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import re

# 제목 및 설명
st.set_page_config(page_title="Tumor Analysis Dashboard")
st.title("📊 Tumor Growth Analysis Dashboard")
st.markdown("엑셀 파일을 업로드하면 자동으로 **성장률 계산, 통계 분석, 그래프**를 생성합니다.")

# 파일 업로드 기능
uploaded_file = st.file_uploader("분석할 엑셀 파일을 선택하세요 (.xlsx)", type=["xlsx"])

def extract_number(value):
    if pd.isna(value): return value
    try:
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else None
    except: return None

if uploaded_file:
    # 데이터 로드 (헤더 찾기 로직 포함)
    target_cols = ['Group', 'Animal no.']
    df_raw = None
    for i in range(5):
        temp_df = pd.read_excel(uploaded_file, header=i)
        temp_df.columns = temp_df.columns.astype(str).str.strip()
        if all(col in temp_df.columns for col in target_cols):
            df_raw = temp_df
            st.success(f"✅ 데이터 구조 확인 완료 (헤더: {i}번 행)")
            break

    if df_raw is not None:
        # 데이터 변환 및 정제
        df_long = df_raw.melt(id_vars=['Group', 'Animal no.'], var_name='Day', value_name='Tumor_Volume')
        df_long['Day'] = df_long['Day'].apply(extract_number)
        df_long['Tumor_Volume'] = df_long['Tumor_Volume'].apply(extract_number)
        df_long = df_long.dropna(subset=['Day', 'Tumor_Volume'])

        # 결과 데이터 프레임 보여주기
        st.subheader("📋 분석 데이터 미리보기")
        st.write(df_long.head())

        # 통계 및 그래프 생성
        last_day = df_long['Day'].max()
        g1 = df_long[(df_long['Group'] == 'G1') & (df_long['Day'] == last_day)]['Tumor_Volume']
        g2 = df_long[(df_long['Group'] == 'G2') & (df_long['Day'] == last_day)]['Tumor_Volume']
        
        p_val = ttest_ind(g1, g2, nan_policy='omit').pvalue if len(g1)>1 and len(g2)>1 else None
        stat_msg = f"p-value: {p_val:.4f}" if p_val is not None else "Statistics N/A"

        # 그래프 출력
        st.subheader("📈 종양 성장 곡선")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df_long, x='Day', y='Tumor_Volume', hue='Group', marker='o', errorbar='se', err_kws={'capsize': 3}, ax=ax)
        plt.title(f"Tumor Growth Curve ({stat_msg})")
        st.pyplot(fig)

        # 결과 다운로드 버튼
        st.subheader("📥 결과 다운로드")
        csv = df_long.to_csv(index=False).encode('utf-8')
        st.download_button("분석 결과(CSV) 다운로드", data=csv, file_name="analysis_result.csv", mime="text/csv")