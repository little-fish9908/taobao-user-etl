import pandas as pd
from sqlalchemy import create_engine

dwd = pd.read_csv('../output/dwd_layer.csv')
dws = pd.read_csv('../output/dws_user_stats.csv')

# 创建 MySQL 连接引擎
engine = create_engine('mysql+pymysql://root:123456@localhost:3306/test')
# 写入数据到 MySQL
dwd.to_sql('dwd_orders', con=engine, index=False, if_exists='replace')
dws.to_sql('dws_users', con=engine, index=False, if_exists='replace')
print("数据已写入 MySQL test 库")

# 用 SQL 分析
# 构建用户转化漏斗
funnel = pd.read_sql("""
    SELECT 
        COUNT(DISTINCT user_id) as total_users,
        SUM(CASE WHEN browse_count > 0 THEN 1 ELSE 0 END) as browse_users,
        SUM(CASE WHEN cart_count > 0 THEN 1 ELSE 0 END) as cart_users,
        SUM(CASE WHEN buy_count > 0 THEN 1 ELSE 0 END) as buy_users
    FROM dws_users
""", engine)
print("\n【用户转化漏斗】")
print(funnel)

# 按用户活跃度分层
active = pd.read_sql("""
    SELECT 
        CASE 
            WHEN active_days <= 5 THEN '低活跃（1-5天）'
            WHEN active_days <= 15 THEN '中活跃（6-15天）'
            ELSE '高活跃（>15天）'
        END as active_group,
        COUNT(user_id) as user_count,
        AVG(buy_count) as avg_buy_count
    FROM dws_users
    GROUP BY active_group
    ORDER BY avg_buy_count DESC
""", engine)
print("\n【按活跃度分组的购买行为】")
print(active)

# 数据一致性验证
validation = pd.read_sql("""
    SELECT 
        (SELECT COUNT(DISTINCT user_id) FROM dwd_orders) as dwd_user_count,
        (SELECT COUNT(user_id) FROM dws_users) as dws_user_count
""", engine)
print("\n【数据一致性验证】")
print(f"DWD用户数：{validation['dwd_user_count'].values[0]}")
print(f"DWS用户数：{validation['dws_user_count'].values[0]}")

engine.dispose()
print("\nMySQL 分析完成")