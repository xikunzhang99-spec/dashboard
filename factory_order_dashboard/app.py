import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="工厂订单生产运营数据分析大屏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# 页面样式
# =====================
st.markdown(
    """
    <style>
    .main {
        background-color: #f5f7fb;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }
    .dashboard-title {
        font-size: 34px;
        font-weight: 800;
        text-align: center;
        color: #1f2937;
        margin-bottom: 6px;
    }
    .dashboard-subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 22px;
    }
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 18px 20px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="dashboard-title">工厂订单生产运营数据分析大屏</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">订单交付 · 生产进度 · 质量分析 · 风险预警</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    from pathlib import Path

    # 获取当前 app.py 所在目录
    BASE_DIR = Path(__file__).resolve().parent

    # data 文件夹路径
    DATA_DIR = BASE_DIR / "data"

     # 读取数据（兼容本地 + 云端）
    order_df = pd.read_csv(DATA_DIR / "order_info.csv")
    production_df = pd.read_csv(DATA_DIR / "production.csv")
    quality_df = pd.read_csv(DATA_DIR / "quality.csv")

    order_df["order_date"] = pd.to_datetime(order_df["order_date"])
    order_df["delivery_date"] = pd.to_datetime(order_df["delivery_date"])
    production_df["production_date"] = pd.to_datetime(production_df["production_date"])
    quality_df["check_date"] = pd.to_datetime(quality_df["check_date"])

    return order_df, production_df, quality_df

order_df, production_df, quality_df = load_data()

# =====================
# 侧边栏筛选
# =====================
st.sidebar.header("筛选条件")

product_list = ["全部"] + sorted(order_df["product"].unique().tolist())
selected_product = st.sidebar.selectbox("产品类型", product_list)

status_list = ["全部"] + sorted(order_df["status"].unique().tolist())
selected_status = st.sidebar.selectbox("订单状态", status_list)

customer_list = ["全部"] + sorted(order_df["customer"].unique().tolist())
selected_customer = st.sidebar.selectbox("客户名称", customer_list)

min_date = order_df["order_date"].min().date()
max_date = order_df["order_date"].max().date()
date_range = st.sidebar.date_input(
    "下单日期范围",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_orders = order_df.copy()

if selected_product != "全部":
    filtered_orders = filtered_orders[filtered_orders["product"] == selected_product]

if selected_status != "全部":
    filtered_orders = filtered_orders[filtered_orders["status"] == selected_status]

if selected_customer != "全部":
    filtered_orders = filtered_orders[filtered_orders["customer"] == selected_customer]

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_orders = filtered_orders[
        (filtered_orders["order_date"] >= start_date) &
        (filtered_orders["order_date"] <= end_date)
    ]

valid_order_ids = filtered_orders["order_id"].tolist()
filtered_production = production_df[production_df["order_id"].isin(valid_order_ids)]
filtered_quality = quality_df[quality_df["order_id"].isin(valid_order_ids)]

# =====================
# 汇总数据
# =====================
production_sum = (
    filtered_production.groupby("order_id")[["planned_qty", "actual_qty", "work_hours"]]
    .sum()
    .reset_index()
)

order_progress = pd.merge(filtered_orders, production_sum, on="order_id", how="left")
order_progress[["planned_qty", "actual_qty", "work_hours"]] = order_progress[["planned_qty", "actual_qty", "work_hours"]].fillna(0)
order_progress["完成进度"] = (order_progress["actual_qty"] / order_progress["order_qty"] * 100).clip(upper=100)
order_progress["剩余数量"] = (order_progress["order_qty"] - order_progress["actual_qty"]).clip(lower=0)

quality_sum = (
    filtered_quality.groupby("order_id")[["check_qty", "pass_qty", "fail_qty"]]
    .sum()
    .reset_index()
)

quality_order = pd.merge(filtered_orders[["order_id", "product", "customer"]], quality_sum, on="order_id", how="left")
quality_order[["check_qty", "pass_qty", "fail_qty"]] = quality_order[["check_qty", "pass_qty", "fail_qty"]].fillna(0)

# =====================
# 核心指标卡片
# =====================
total_orders = len(filtered_orders)
total_amount = filtered_orders["amount"].sum()
processing_orders = len(filtered_orders[filtered_orders["status"] == "生产中"])
delayed_orders = len(filtered_orders[filtered_orders["status"] == "延期"])

overall_progress = order_progress["actual_qty"].sum() / order_progress["order_qty"].sum() * 100 if order_progress["order_qty"].sum() else 0
overall_pass_rate = quality_order["pass_qty"].sum() / quality_order["check_qty"].sum() * 100 if quality_order["check_qty"].sum() else 0

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("订单总数", f"{total_orders}")
col2.metric("订单总金额", f"{total_amount / 10000:.2f} 万元")
col3.metric("生产中订单", f"{processing_orders}")
col4.metric("延期订单", f"{delayed_orders}")
col5.metric("整体完成率", f"{overall_progress:.1f}%")
col6.metric("整体良品率", f"{overall_pass_rate:.1f}%")

st.divider()

# =====================
# 第一行图表
# =====================
left, right = st.columns([1.15, 1])

with left:
    st.subheader("订单数量与实际产量趋势")

    order_trend = (
        filtered_orders.groupby("order_date")
        .size()
        .reset_index(name="订单数量")
    )

    production_trend = (
        filtered_production.groupby("production_date")["actual_qty"]
        .sum()
        .reset_index()
        .rename(columns={"production_date": "日期", "actual_qty": "实际产量"})
    )

    order_trend = order_trend.rename(columns={"order_date": "日期"})

    fig_order = px.line(
        order_trend,
        x="日期",
        y="订单数量",
        markers=True,
        title="每日新增订单数量"
    )
    st.plotly_chart(fig_order, use_container_width=True)

with right:
    st.subheader("订单状态分布")
    status_df = filtered_orders["status"].value_counts().reset_index()
    status_df.columns = ["订单状态", "数量"]

    fig_status = px.pie(
        status_df,
        names="订单状态",
        values="数量",
        hole=0.45,
        title="订单状态占比"
    )
    st.plotly_chart(fig_status, use_container_width=True)

# =====================
# 第二行图表
# =====================
left, right = st.columns(2)

with left:
    st.subheader("各车间生产完成率")

    workshop_df = (
        filtered_production.groupby("workshop")[["planned_qty", "actual_qty"]]
        .sum()
        .reset_index()
    )

    if not workshop_df.empty:
        workshop_df["完成率"] = workshop_df["actual_qty"] / workshop_df["planned_qty"] * 100
        workshop_df = workshop_df.sort_values("完成率", ascending=False)

        fig_workshop = px.bar(
            workshop_df,
            x="workshop",
            y="完成率",
            text="完成率",
            title="各车间计划产量与实际产量完成情况"
        )
        fig_workshop.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_workshop, use_container_width=True)
    else:
        st.info("暂无车间生产数据")

with right:
    st.subheader("各产品良品率")

    product_quality = (
        pd.merge(filtered_quality, filtered_orders[["order_id", "product"]], on="order_id", how="left")
        .groupby("product")[["check_qty", "pass_qty"]]
        .sum()
        .reset_index()
    )

    if not product_quality.empty:
        product_quality["良品率"] = product_quality["pass_qty"] / product_quality["check_qty"] * 100
        product_quality = product_quality.sort_values("良品率", ascending=False)

        fig_quality = px.bar(
            product_quality,
            x="product",
            y="良品率",
            text="良品率",
            title="各产品质检良品率"
        )
        fig_quality.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        st.plotly_chart(fig_quality, use_container_width=True)
    else:
        st.info("暂无质检数据")

# =====================
# 第三行图表
# =====================
left, right = st.columns(2)

with left:
    st.subheader("延期订单风险预警")

    today = pd.to_datetime(datetime.today().date())
    warning_df = order_progress[
        ((order_progress["delivery_date"] < today) & (order_progress["完成进度"] < 100)) |
        ((order_progress["delivery_date"] <= today + pd.Timedelta(days=3)) & (order_progress["完成进度"] < 80))
    ].copy()

    warning_df["距离交付天数"] = (warning_df["delivery_date"] - today).dt.days
    warning_df["完成进度"] = warning_df["完成进度"].round(2)

    warning_df = warning_df[[
        "order_id", "customer", "product", "order_qty",
        "actual_qty", "剩余数量", "delivery_date",
        "距离交付天数", "完成进度", "status"
    ]].sort_values(["距离交付天数", "完成进度"])

    st.dataframe(warning_df, use_container_width=True, height=360)

with right:
    st.subheader("不良原因占比")

    defect_df = (
        filtered_quality.groupby("defect_reason")["fail_qty"]
        .sum()
        .reset_index()
        .sort_values("fail_qty", ascending=False)
    )

    if not defect_df.empty:
        fig_defect = px.pie(
            defect_df,
            names="defect_reason",
            values="fail_qty",
            title="不合格数量按不良原因分布"
        )
        st.plotly_chart(fig_defect, use_container_width=True)
    else:
        st.info("暂无不良原因数据")

# =====================
# 第四行：重点订单进度排行
# =====================
st.subheader("重点订单生产进度排行")

rank_df = order_progress[[
    "order_id", "customer", "product", "order_qty",
    "actual_qty", "剩余数量", "完成进度", "delivery_date", "status"
]].copy()

rank_df["完成进度"] = rank_df["完成进度"].round(2)
rank_df = rank_df.sort_values("完成进度", ascending=True)

st.dataframe(rank_df, use_container_width=True, height=360)
