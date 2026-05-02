import pandas as pd

df = pd.read_csv('../data/tianchi_mobile_recommend_train_user.csv')

print(f"数据集形状: {df.shape}")
# 输出一个元组

print("\n前5行数据：")
print(df.head())  # head()默认值是5

print("\n列名列表：")
print(df.columns.tolist())
# ['user_id', 'item_id', 'behavior_type', 'user_geohash'（用户位置编码）, 'item_category'（商品类目ID）, 'time']

print("\n各列数据类型：")
print(df.dtypes)

print("\n各列缺失值统计：")
print(df.isnull().sum())

print("\n数值列统计描述：")
print(df.describe())
# behavior_type 只有 1、2、3、4，没有脏数据（比如5、6），说明这一列干净