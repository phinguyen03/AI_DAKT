import pandas as pd
import glob

# 1. Tìm tất cả các file bắt đầu bằng 'output' và có đuôi .csv
file_paths = glob.glob("output*.csv")

# 2. Đọc và gộp
df_list = [pd.read_csv(file) for file in file_paths]
df_combined = pd.concat(df_list, ignore_index=True)

# 4. Kiểm tra kết quả
print(df_combined.shape)
print(df_combined.head())

# 5. Lưu lại
df_combined.to_csv("output_all.csv", index=False)

