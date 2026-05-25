"""
淘宝用户行为数据仓库 - MySQL 分析脚本
功能：将清洗后的数据写入 MySQL，执行 SQL 分析，输出结果并保存
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

# 配置部分
DATA_DIR = '../output'
DB_NAME = 'test'
DWD_TABLE = 'dwd_orders'
DWS_TABLE = 'dws_users'

# 数据库连接信息
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_PORT = os.getenv('MYSQL_PORT', '3306')


# 1. 读取清洗后的数据
print("淘宝用户行为数据仓库 - MySQL 分析")

try:
    dwd = pd.read_csv(f'{DATA_DIR}/dwd_layer.csv')
    dws = pd.read_csv(f'{DATA_DIR}/dws_user_stats.csv')
    print(f"数据加载成功：DWD层 {len(dwd)} 行，DWS层 {len(dws)} 行")
except Exception as e:
    print(f"数据加载失败：{e}")
    exit(1)

# 2. 连接 MySQL 并写入数据
try:
    # 创建连接引擎
    engine = create_engine(
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    # 测试连接
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"MySQL 连接成功：{DB_HOST}:{DB_PORT}/{DB_NAME}")

    # 写入数据
    dwd.to_sql(DWD_TABLE, con=engine, index=False, if_exists='replace')
    dws.to_sql(DWS_TABLE, con=engine, index=False, if_exists='replace')
    print(f"数据已写入 MySQL：{DWD_TABLE}（{len(dwd)}行），{DWS_TABLE}（{len(dws)}行）")

    # 检查 MySQL 中的字段
    with engine.connect() as conn:
        result = conn.execute(text(f"DESCRIBE {DWD_TABLE}"))
        print("\n【dwd_orders 表结构】")
        for row in result:
            print(row)

except Exception as e:
    print(f"MySQL 连接或写入失败：{e}")
    exit(1)

# 3. SQL 分析1：用户转化漏斗
print("\n")
print("SQL 分析1：用户转化漏斗")

sql_funnel = """
SELECT 
    COUNT(DISTINCT user_id) as total_users,
    SUM(CASE WHEN browse_count > 0 THEN 1 ELSE 0 END) as browse_users,
    SUM(CASE WHEN cart_count > 0 THEN 1 ELSE 0 END) as cart_users,
    SUM(CASE WHEN buy_count > 0 THEN 1 ELSE 0 END) as buy_users
FROM dws_users
"""

try:
    funnel = pd.read_sql(sql_funnel, engine)
    print(funnel)
    funnel.to_csv(f'{DATA_DIR}/funnel_analysis.csv', index=False)
    print("漏斗分析结果已保存至：../output/funnel_analysis.csv")
except Exception as e:
    print(f"SQL执行失败：{e}")

# 4. SQL 分析2：按用户活跃度分层
print("\n")
print("SQL 分析2：按用户活跃度分层的购买行为")

sql_active = """
SELECT 
    CASE 
        WHEN active_days <= 5 THEN '低活跃（1-5天）'
        WHEN active_days <= 15 THEN '中活跃（6-15天）'
        ELSE '高活跃（>15天）'
    END as active_group,
    COUNT(user_id) as user_count,
    ROUND(AVG(buy_count), 2) as avg_buy_count
FROM dws_users
GROUP BY active_group
ORDER BY avg_buy_count DESC
"""

try:
    active = pd.read_sql(sql_active, engine)
    print(active)
    active.to_csv(f'{DATA_DIR}/active_analysis.csv', index=False)
    print("活跃度分析结果已保存至：../output/active_analysis.csv")
except Exception as e:
    print(f"SQL执行失败：{e}")

# 5. SQL 分析3：数据一致性校验
print("\n")
print("SQL 分析3：数据一致性校验")

sql_validate = """
SELECT 
    (SELECT COUNT(DISTINCT user_id) FROM dwd_orders) as dwd_user_count,
    (SELECT COUNT(user_id) FROM dws_users) as dws_user_count
"""

try:
    validation = pd.read_sql(sql_validate, engine)
    dwd_cnt = validation['dwd_user_count'].values[0]
    dws_cnt = validation['dws_user_count'].values[0]
    print(f"DWD层用户数：{dwd_cnt}")
    print(f"DWS层用户数：{dws_cnt}")

    if dwd_cnt == dws_cnt:
        print("数据一致性校验通过：DWD与DWS用户数一致")
    else:
        print(f"数据不一致：DWD层{dwd_cnt}人，DWS层{dws_cnt}人")
except Exception as e:
    print(f"SQL执行失败：{e}")

# 6. SQL 分析4：周末 vs 工作日购买对比（新增）
print("\n")
print("SQL 分析4：周末 vs 工作日购买行为对比")
print("数据预处理：添加 is_buy 字段")
try:
    with engine.connect() as conn:
        # 添加 is_buy 字段
        conn.execute(text("ALTER TABLE dwd_orders ADD COLUMN is_buy INT DEFAULT 0;"))
        # 根据 behavior_type 更新 is_buy 的值
        conn.execute(text("UPDATE dwd_orders SET is_buy = 1 WHERE behavior_type = 4;"))
        conn.commit()
        print("is_buy 字段添加并更新成功")
except Exception as e:
    print(f"字段可能已存在或更新失败: {e}")

sql_weekend = """
SELECT 
    CASE 
        WHEN weekday IN (5,6) THEN '周末'
        ELSE '工作日'
    END as day_type,
    COUNT(DISTINCT user_id) as active_users,
    SUM(is_buy) as total_buy,
    ROUND(AVG(is_buy), 4) as avg_purchase_rate
FROM dwd_orders
GROUP BY day_type
"""

try:
    weekend = pd.read_sql(sql_weekend, engine)
    print(weekend)
    weekend.to_csv(f'{DATA_DIR}/weekend_analysis.csv', index=False)
    print("周末/工作日分析结果已保存至：../output/weekend_analysis.csv")
except Exception as e:
    print(f"周末分析跳过（dwd_orders表可能缺少 weekday 或 is_buy 字段）：{e}")

# 7. 关闭连接
engine.dispose()
print("MySQL 分析全部完成，连接已关闭")
