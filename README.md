# 淘宝用户行为数据仓库与 ETL 项目

## 项目简介
基于阿里天池公开数据集（100万+用户行为记录），完成数据清洗、数仓分层（ODS → DWD → DWS）及 MySQL 数据分析，构建用户转化漏斗与活跃度画像。

**技术栈**：Python（Pandas） + SQL + MySQL + SQLAlchemy

---

## 一、观察数据（数据探查）

1. 数据总量约 **1200 万行，6 列**
2. 观察前 5 行数据，无明显异常
3. 列名列表：`['user_id', 'item_id', 'behavior_type', 'user_geohash', 'item_category', 'time']`
4. 数据类型：`user_id`, `item_id`, `behavior_type`, `item_category` 为 `int64`；`user_geohash`, `time` 为 `object`
5. 缺失值统计：`user_geohash` 列缺失值达 **68%**，决定删除该列
6. 数值列统计描述：`behavior_type` 列最值在 `[1, 4]`，说明该列数据干净，无脏数据

---

## 二、清洗数据

1. 删除 `user_geohash` 列
2. 将 `time` 列转成日期时间格式，转换失败的行数为 **0**
3. 检查 `behavior_type` 是否有异常值：分布为 `1:1155万, 2:24万, 3:34万, 4:12万`，**无异常值**
4. 确认清洗结果后保存为 `cleaned_data.csv`

---

## 三、数据分层

### 1. ODS 层（原始数据层）
读取清洗后的数据，将 `time` 列转为日期时间格式

### 2. DWD 层（明细数据层）
新增字段：`date`（日期）、`hour`（小时）、`weekday`（星期几）

### 3. DWS 层（用户行为汇总层）
- 创建辅助列（`is_browse`, `is_fav`, `is_cart`, `is_buy`）
- 按用户分组汇总：行为次数、活跃天数
- 计算转化率：浏览→购买、加购→购买、日均行为

---

## 四、MySQL 分析

1. 创建连接引擎，写入数据到 MySQL
2. 构建用户转化漏斗（浏览 → 加购 → 购买）
3. 按用户活跃度（低 / 中 / 高）分层，分析购买行为差异
4. 验证数据一致性，关闭连接

---

## 五、如何运行本项目

1. 下载阿里天池数据集，放入 `data/` 目录
2. 安装依赖：`pip install -r requirements.txt`
3. 依次运行 scripts 目录下的脚本
4. 确保 MySQL 服务已启动，并修改连接信息

---

## 六、项目总结

| 能力维度 | 本项目体现 |
|----------|--------------|
| Python ETL | 数据清洗、时间解析、特征加工、分层构建 |
| 数仓建模 | ODS → DWD → DWS 三层分离 |
| 指标体系 | 转化漏斗、活跃度画像、转化率指标 |
| SQL 能力 | 条件聚合、窗口函数、数据一致性校验 |
| 工程能力 | 代码模块化、可重跑、MySQL 落地 |
| 业务洞察 | 发现“加购不是必经路径”、“高活跃用户贡献更高购买” |

---

## 七、代码仓库结构

```text
├── data/
│   └── tianchi_mobile_recommend_train_user.csv
├── scripts/
│   ├── 01_data_overview.py
│   ├── 02_data_cleaning.py
│   ├── 03_data_layering.py
│   └── 04_sql_analysis.py
├── output/
│   ├── cleaned_data.csv
│   ├── dwd_layer.csv
│   └── dws_user_stats.csv
├── README.md
└── requirements.txt
```

---

## 八、作者

张凯馨 | 数据开发工程师 | 2026.04