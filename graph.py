import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 데이터 불러오기
df = pd.read_excel('result.xlsx')

# 2. 'Day' 컬럼을 숫자로 변환
df['Day'] = pd.to_numeric(df['Day'])

# 3. 그래프 그리기
plt.figure(figsize=(12, 7))

# 여기서 err_kws={'capsize': 3} 처럼 꾸러미 안에 넣어서 전달하면 구 버전에서도 잘 작동합니다.
sns.lineplot(
    data=df, 
    x='Day', 
    y='Tumor_Volume', 
    hue='Group', 
    marker='o', 
    err_style='bars',
    errorbar='se',
    err_kws={'capsize': 3}  # 에러 방지를 위해 꾸러미(dict) 형태로 전달합니다.
)

# 4. X축 설정 (실제 측정일만 표시)
measured_days = sorted(df['Day'].unique())
plt.xticks(measured_days) 

# 5. 그래프 꾸미기
plt.title('Tumor Growth Curve with Error Bars (SE)', fontsize=15)
plt.xlabel('Days after administration', fontsize=12)
plt.ylabel('Tumor Volume (mm³)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

# 6. 저장 및 출력
plt.savefig('tumor_graph_final.png', dpi=300)
print("성공! 에러 바가 포함된 그래프가 저장되었습니다.")
plt.show()