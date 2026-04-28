# 工厂订单生产运营数据分析大屏系统

## 一、项目简介

本项目是一个基于 Python 的工厂订单生产运营数据分析大屏系统，主要用于展示工厂订单、生产、质检和交付过程中的关键指标。

系统适合用于：

- Python 数据分析项目
- 课程设计
- 毕业设计雏形
- 数据可视化作品集
- 企业生产管理类系统原型

## 二、核心功能

本系统第一版实现以下功能：

1. 订单总览  
2. 订单金额统计  
3. 生产进度分析  
4. 车间生产完成率分析  
5. 产品良品率分析  
6. 不良原因占比分析  
7. 延期订单风险预警  
8. 重点订单生产进度排行  
9. 按产品、客户、订单状态和日期筛选数据  

## 三、项目结构

```text
factory_order_dashboard/
│
├── app.py                  # Streamlit 大屏主程序
├── generate_data.py         # 模拟数据生成脚本
├── requirements.txt         # 项目依赖
├── README.md                # 项目说明
└── data/
    ├── order_info.csv       # 订单数据
    ├── production.csv       # 生产数据
    └── quality.csv          # 质检数据
```

## 四、运行环境

建议使用 Python 3.9 及以上版本。

安装依赖：

```bash
pip install -r requirements.txt
```

## 五、运行步骤

第一步，生成模拟数据：

```bash
python generate_data.py
```

第二步，启动大屏系统：

```bash
streamlit run app.py
```

运行后，浏览器会自动打开系统页面。

## 六、数据表说明

### 1. 订单表 order_info.csv

| 字段名 | 含义 |
|---|---|
| order_id | 订单编号 |
| customer | 客户名称 |
| product | 产品名称 |
| order_qty | 订单数量 |
| order_date | 下单日期 |
| delivery_date | 交付日期 |
| status | 订单状态 |
| amount | 订单金额 |

### 2. 生产表 production.csv

| 字段名 | 含义 |
|---|---|
| order_id | 订单编号 |
| workshop | 生产车间 |
| production_date | 生产日期 |
| planned_qty | 计划产量 |
| actual_qty | 实际产量 |
| work_hours | 工时 |
| equipment_id | 设备编号 |

### 3. 质检表 quality.csv

| 字段名 | 含义 |
|---|---|
| order_id | 订单编号 |
| check_date | 质检日期 |
| check_qty | 检测数量 |
| pass_qty | 合格数量 |
| fail_qty | 不合格数量 |
| defect_reason | 不良原因 |

## 七、可扩展方向

后续可以继续增加：

1. MySQL 数据库接入  
2. 设备利用率分析  
3. 产能预测模型  
4. 订单延期风险评分  
5. Flask + ECharts 前后端分离版本  
6. 用户登录与权限管理  
7. 自动生成生产日报  
8. 实时数据接口接入