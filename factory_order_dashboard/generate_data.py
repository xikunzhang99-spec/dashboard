import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

"""
生成工厂订单生产运营模拟数据。
运行方式：
python generate_data.py
"""

os.makedirs("data", exist_ok=True)

np.random.seed(42)
random.seed(42)

customers = ["华东制造", "远航科技", "金陵机电", "恒通设备", "北方工业", "苏州精工", "海川装备"]
products = ["电机外壳", "传动轴", "控制面板", "铝合金支架", "精密齿轮", "液压阀体"]
workshops = ["一号车间", "二号车间", "三号车间", "装配车间", "精加工车间"]
defect_reasons = ["尺寸偏差", "表面划伤", "装配不良", "材料缺陷", "焊接问题", "孔位偏差"]

today = datetime.today()

orders = []
productions = []
qualities = []

for i in range(1, 121):
    order_id = f"ORD{i:04d}"
    customer = random.choice(customers)
    product = random.choice(products)
    order_qty = random.randint(500, 6000)
    order_date = today - timedelta(days=random.randint(1, 90))
    delivery_date = order_date + timedelta(days=random.randint(10, 45))
    unit_price = random.randint(50, 260)
    amount = order_qty * unit_price

    total_actual = random.randint(int(order_qty * 0.25), int(order_qty * 1.08))

    if total_actual >= order_qty:
        status = "已完成"
    elif delivery_date < today:
        status = "延期"
    else:
        status = random.choice(["未开始", "生产中", "生产中", "生产中"])

    orders.append([
        order_id, customer, product, order_qty,
        order_date.strftime("%Y-%m-%d"),
        delivery_date.strftime("%Y-%m-%d"),
        status, amount
    ])

    production_days = random.randint(3, 15)
    remaining_actual = total_actual

    for d in range(production_days):
        production_date = order_date + timedelta(days=d)
        planned_qty = max(1, int(order_qty / production_days))
        actual_qty = max(0, int(np.random.normal(planned_qty, planned_qty * 0.25)))

        if remaining_actual <= 0:
            actual_qty = 0
        else:
            actual_qty = min(actual_qty, remaining_actual)
            remaining_actual -= actual_qty

        productions.append([
            order_id,
            random.choice(workshops),
            production_date.strftime("%Y-%m-%d"),
            planned_qty,
            actual_qty,
            round(random.uniform(6, 12), 1),
            f"EQ{random.randint(1, 18):02d}"
        ])

    check_qty = min(total_actual, random.randint(200, order_qty))
    fail_qty = random.randint(0, max(1, int(check_qty * 0.10)))
    pass_qty = check_qty - fail_qty

    qualities.append([
        order_id,
        (order_date + timedelta(days=random.randint(3, 18))).strftime("%Y-%m-%d"),
        check_qty,
        pass_qty,
        fail_qty,
        random.choice(defect_reasons)
    ])

order_df = pd.DataFrame(orders, columns=[
    "order_id", "customer", "product", "order_qty",
    "order_date", "delivery_date", "status", "amount"
])

production_df = pd.DataFrame(productions, columns=[
    "order_id", "workshop", "production_date",
    "planned_qty", "actual_qty", "work_hours", "equipment_id"
])

quality_df = pd.DataFrame(qualities, columns=[
    "order_id", "check_date", "check_qty",
    "pass_qty", "fail_qty", "defect_reason"
])

order_df.to_csv("data/order_info.csv", index=False, encoding="utf-8-sig")
production_df.to_csv("data/production.csv", index=False, encoding="utf-8-sig")
quality_df.to_csv("data/quality.csv", index=False, encoding="utf-8-sig")

print("模拟数据生成完成！")
print("已生成：data/order_info.csv, data/production.csv, data/quality.csv")