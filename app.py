import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import re

# 웹 페이지 설정
st.set_page_config(page_title="Tumor Analysis Dashboard", layout="wide")
st.title("📊 Tumor Growth Analysis Dashboard")
st.markdown("엑셀 파일을 업로드하면 자동으로 **성장률 계산, 통계 분석, 그래프**를 생성합니다.")

# 숫자 추출 함수
def extract_number(value):
    if pd.isna(value): return value
    try:
        # 숫자와 소수점만 남기고 제거
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else None
    except:
        return None

# 파일 업로드 기능
uploaded_file = st.file_uploader("분석할 엑셀 파일을 선택하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    # 데이터 로드 (헤더 자동 탐색)
    target_cols = ['Group', 'Animal no.']
    df_raw = None
    
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
        
        # 전처리: 숫자형 변환 및 결측치 제거
        df_long['Day'] = df_long['Day'].apply(extract_number)
        df_long['Tumor_Volume'] = df_long['Tumor_Volume'].apply(extract_number)
        df_long = df_long.dropna(subset=['Day', 'Tumor_Volume'])
        
        # 정렬
        df_long = df_long.sort_values(['Group', 'Animal no.', 'Day'])

        # 통계 분석 (마지막 측정일 기준 G1 vs G2)
        last_day = df_long['Day'].max()
        g1_data = df_long[(df_long['Group'] == 'G1') & (df_long['Day'] == last_day)]['Tumor_Volume']
        g2_data = df_long[(df_long['Group'] == 'G2') & (df_long['Day'] == last_day)]['Tumor_Volume']
        
        p_val = None
        if len(g1_data) > 1 and len(g2_data) > 1:
            _, p_val = ttest_ind(g1_data, g2_data, nan_policy='omit')

        # 화면 구성 (2컬럼)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📈 종양 성장 곡선")
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # 에러 발생 지점 수정 완료: err_kws 사용
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
            
            stat_title = f"Tumor Growth Curve (Last Day p-value: {p_val:.4f})" if p_val is not None else "Tumor Growth Curve"
            plt.title(stat_title)
            plt.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

        with col2:
            st.subheader("📊 데이터 요약 (마지막 측정일)")
            summary = df_long[df_long['Day'] == last_day].groupby('Group')['Tumor_Volume'].agg(['mean', 'std', 'count']).reset_index()
            st.table(summary)
            
            if p_val is not None:
                st.info(f"💡 **T-test 결과:** 그룹 간 차이의 유의확률(p-value)은 **{p_val:.4f}** 입니다.")

        # 데이터 다운로드
        st.divider()
        st.subheader("📥 분석 결과 저장")
        csv = df_long.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="분석 완료된 데이터(CSV) 다운로드",
            data=csv,
            file_name=f"tumor_analysis_result_{int(last_day)}days.csv",
            mime="text/csv"
        )
    else:
        st.error("❌ 엑셀 파일에서 'Group'과 'Animal no.' 열을 찾을 수 없습니다. 파일 양식을 확인해 주세요.")
