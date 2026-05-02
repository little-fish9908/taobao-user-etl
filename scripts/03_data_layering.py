"""
目标：按数据仓库分层思想，加工数据
ODS层：原始数据（已经清洗好的）
DWD层：明细数据（补充时间维度）
DWS层：用户行为汇总（按用户聚合）
"""
import pandas as pd

# ODS层：清洗后的原始数据
df = pd.read_csv('../output/cleaned_data.csv', parse_dates=['time'])
# parse_dates：将time列转换成日期时间格式


# DWD层：明细数据（增加时间维度字段）

# 从时间字段中提取更多信息
df['date'] = df['time'].dt.date
df['hour'] = df['time'].dt.hour
df['weekday'] = df['time'].dt.weekday   # 周一 = 0，周日 = 6

print("【DWD层】已生成，新增字段：date, hour, weekday")
print(f"字段列表: {df.columns.tolist()}")

# 保存DWD层数据
df.to_csv('../output/dwd_layer.csv', index=False)
# Pandas 里的 DataFrame，默认有一列行号（从0开始），叫索引（index）
# index=False 的意思是：保存 CSV 文件时，不写入行索引列。
print("DWD层已保存: ../output/dwd_layer.csv")


# DWS层：用户行为汇总（按用户汇总）

# 对 behavior_type 进行统计,创建4个辅助列
# df['behavior_type'] == 1	判断每行是不是「浏览」，得到 True/False
# astype(int)	把 True -> 1，False -> 0
df['is_browse'] = (df['behavior_type'] == 1).astype(int)  # 浏览
df['is_fav'] = (df['behavior_type'] == 2).astype(int)     # 收藏
df['is_cart'] = (df['behavior_type'] == 3).astype(int)    # 加购
df['is_buy'] = (df['behavior_type'] == 4).astype(int)     # 购买

# 按用户分组汇总，aggregate（聚合），nunique（统计去重后还剩几个 Number of unique）
user_stats = df.groupby('user_id').agg(
    total_actions=('behavior_type', 'count'),  # 总行为次数
    browse_count=('is_browse', 'sum'),         # 浏览次数
    fav_count=('is_fav', 'sum'),               # 收藏次数
    cart_count=('is_cart', 'sum'),             # 加购次数
    buy_count=('is_buy', 'sum'),               # 购买次数
    active_days=('date', 'nunique')            # 活跃天数
).reset_index()
# group by 后，user_id 会变成索引（index），不是普通列。
# 有 .reset_index()，user_id 变回普通列，可以像普通数据一样用 df['user_id']

# 计算转化率特征（注意分母不能为0, +1防止报错）
# 浏览→购买转化率
user_stats['browse_to_buy_rate'] = user_stats['buy_count'] / (user_stats['browse_count'] + 1)
# 加购→购买转化率
user_stats['cart_to_buy_rate'] = user_stats['buy_count'] / (user_stats['cart_count'] + 1)
# 日均行为次数
user_stats['avg_daily_actions'] = user_stats['total_actions'] / user_stats['active_days']

print("\n【DWS层】用户汇总表已生成")
print(f"用户数: {len(user_stats)}")
print(f"字段列表: {user_stats.columns.tolist()}")

# 查看汇总结果（前5行）
print("\n用户汇总表示例（前5行）：")
print(user_stats.head())

# 保存DWS层数据
user_stats.to_csv('../output/dws_user_stats.csv', index=False)
print("\nDWS层已保存: ../output/dws_user_stats.csv")


# 各层数据量对比
print("\n数据量验证：")
print(f"原始数据（ODS层）行数: {len(df):,}")
print(f"DWD层行数: {len(df):,}")
print(f"DWS层用户数: {len(user_stats):,}")
print(f"购买用户数: {(user_stats['buy_count'] > 0).sum():,}")
print(f"购买用户占比: {(user_stats['buy_count'] > 0).mean():.2%}")