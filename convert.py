import pandas as pd

# 1. 엑셀 파일 읽기 (header=1 이라고 써야 두 번째 줄을 제목으로 읽어요!)
# 파일 이름이 다르면 'tv_data.xlsx' 부분을 수정하세요.
df = pd.read_excel('tv_data.xlsx', header=2)

# 2. 제대로 읽었는지 확인하기 위해 제목을 출력해봅니다.
print("이제 찾은 제목들:", df.columns.tolist())

# 3. 데이터 변환 (가로를 세로로!)
# 이번에는 제목을 정확히 찾았으니 에러가 안 날 거예요.
df_long = df.melt(id_vars=['Group', 'Animal no.'], 
                  var_name='Day', 
                  value_name='Tumor_Volume')

# 4. 빈칸(N/A) 데이터 지우기
df_long = df_long.dropna(subset=['Tumor_Volume'])

# 5. 결과 저장
df_long.to_excel('result.xlsx', index=False)

print("---")
print("성공! 이제 'result.xlsx' 파일을 확인해 보세요.")