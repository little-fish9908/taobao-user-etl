"""
目标：删除无用列、转换时间格式、检查异常值
"""
import pandas as pd

df = pd.read_csv('../data/tianchi_mobile_recommend_train_user.csv')

print(f"\n列数: {df.shape[1]}")
print(f"列名: {df.columns.tolist()}")

# 删除 user_geohash 列（大量缺失值）
df = df.drop('user_geohash', axis=1)
# axis=0，按行操作；axis=1，按列操作
print(f"\n删除 user_geohash 后，列数: {df.shape[1]}")


# 把 time 列转成日期时间格式
df['time'] = pd.to_datetime(df['time'], errors='coerce')
# errors='coerce' ：转换失败则变成 NaT（空时间）
# 检查有多少行转换失败（变成了 NaT）
null_time_count = df['time'].isnull().sum()
print(f"\ntime 转换失败（变成空时间）的行数: {null_time_count}")
if null_time_count > 0:
    print(f"有 {null_time_count} 行时间转换失败，这部分数据无法用于时间分析")
# 转换失败的数量少就删除这部分数据，多就查找失败原因，进行补救，比如先统一格式


# 检查 behavior_type 是否有异常值（应该只有 1,2,3,4）
print("\nbehavior_type 的取值分布：")
print(df['behavior_type'].value_counts().sort_index())
# 找出不是 1,2,3,4 的值
invalid_behaviors = df[~df['behavior_type'].isin([1, 2, 3, 4])]
if len(invalid_behaviors) > 0:
    print(f"\n发现异常行为类型: {invalid_behaviors['behavior_type'].unique()}")
else:
    print("\nbehavior_type 无异常值）")


# 确认清洗结果
print("清洗后数据概览：")
print(f"行数: {len(df)}")
print(f"列数: {df.shape[1]}")
print(f"\n前三行数据：")
print(df.head(3))

# 保存清洗后的数据
df.to_csv('../output/cleaned_data.csv', index=False)