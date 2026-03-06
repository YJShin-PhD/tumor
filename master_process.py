import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
from scipy.stats import ttest_ind

def extract_number(value):
    """글자가 섞인 데이터에서 숫자만 추출 (예: 'Day 4' -> 4)"""
    if pd.isna(value): return value
    try:
        num_str = re.sub(r'[^0-9.]', '', str(value))
        return float(num_str) if num_str else None
    except:
        return None

def process_tumor_data(file_path):
    print(f"\n--- {file_path} 처리 시작 ---")
    
    # 1. 제목 줄(Header) 찾기 (0~4행 시도)
    target_cols = ['Group', 'Animal no.']
    df_raw = None
    for i in range(5): 
        temp_df = pd.read_excel(file_path, header=i)
        temp_df.columns = temp_df.columns.astype(str).str.strip()
        if all(col in temp_df.columns for col in target_cols):
            df_raw = temp_df
            print(f"  -> {i}번 줄에서 제목을 찾았습니다!")
            break
            
    if df_raw is None:
        print(f"  실패: 'Group'과 'Animal no.' 제목을 찾지 못했습니다.")
        return

    # 2. 데이터 변환 (Wide -> Long)
    df_long = df_raw.melt(id_vars=['Group', 'Animal no.'], 
                          var_name='Day', 
                          value_name='Tumor_Volume')
    
    # 3. 데이터 정제 (숫자만 추출 및 빈칸 제거)
    df_long['Day'] = df_long['Day'].apply(extract_number)
    df_long['Tumor_Volume'] = df_long['Tumor_Volume'].apply(extract_number)
    df_long = df_long.dropna(subset=['Day', 'Tumor_Volume'])

    if df_long.empty:
        print("  실패: 분석할 수 있는 숫자 데이터가 없습니다.")
        return

    # 4. 성장률(Growth Rate) 계산
    df_long = df_long.sort_values(['Animal no.', 'Day'])
    df_long['Growth_Rate(%)'] = df_long.groupby('Animal no.')['Tumor_Volume'].pct_change() * 100

    # 5. 통계 분석 (마지막 날 기준 G1 vs G2 T-test)
    last_day = df_long['Day'].max()
    g1_final = df_long[(df_long['Group'] == 'G1') & (df_long['Day'] == last_day)]['Tumor_Volume']
    g2_final = df_long[(df_long['Group'] == 'G2') & (df_long['Day'] == last_day)]['Tumor_Volume']
    
    stat_msg = ""
    if len(g1_final) > 1 and len(g2_final) > 1:
        t_stat, p_val = ttest_ind(g1_final, g2_final, nan_policy='omit')
        stat_msg = f"Last Day({int(last_day)}) G1 vs G2 p-value: {p_val:.4f}"
    else:
        stat_msg = f"Last Day({int(last_day)}) - Statistics N/A (low n)"

    # 6. 결과 저장 (엑셀)
    output_excel = file_path.replace('.xlsx', '_analyzed.xlsx')
    df_long.to_excel(output_excel, index=False)
    print(f"  데이터 저장 완료: {output_excel}")

    # 7. 그래프 생성 및 화면 표시
    try:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_long, x='Day', y='Tumor_Volume', hue='Group', 
                     marker='o', err_style='bars', errorbar='se', err_kws={'capsize': 3})
        
        plt.title(f'Tumor Growth Curve\n{stat_msg}')
        plt.xlabel('Days after administration')
        plt.ylabel('Tumor Volume (mm³)')
        plt.grid(True, alpha=0.3)
        
        # 실제 측정일만 X축 눈금으로 표시
        measured_days = sorted(df_long['Day'].unique().astype(int))
        plt.xticks(measured_days)
        
        # 이미지 저장
        output_plot = file_path.replace('.xlsx', '_plot.png')
        plt.savefig(output_plot, dpi=300, bbox_inches='tight')
        print(f"  그래프 저장 완료: {output_plot}")
        
        # 화면에 그래프 띄우기
        plt.show() 
        
    except Exception as e:
        print(f"  그래프 생성 실패: {e}")
    finally:
        plt.close()

# --- 자동화: 폴더 내 모든 엑셀 파일 대상 ---
if __name__ == "__main__":
    current_files = [f for f in os.listdir('.') if f.endswith('.xlsx') 
                     and not f.startswith('~$') 
                     and '_analyzed' not in f]

    if not current_files:
        print("분석할 엑셀 파일(.xlsx)이 폴더에 없습니다.")
    else:
        for file in current_files:
            process_tumor_data(file)
        print("\n모든 작업이 끝났습니다!")