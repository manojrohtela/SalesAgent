import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


plt.switch_backend("Agg")


@dataclass
class AnalysisResult:
    dataset_summary: str
    key_insights: List[str]
    visual_analysis: List[str]
    business_recommendations: List[str]
    action_plan: List[str]
    charts: Dict[str, str]
    stats_snapshot: Dict[str, str]


def _describe_dataset(df: pd.DataFrame) -> str:
    n_rows, n_cols = df.shape
    start_date = pd.to_datetime(df["date"]).min().date()
    end_date = pd.to_datetime(df["date"]).max().date()
    total_revenue = df["revenue"].sum()
    total_units = df["units_sold"].sum()
    avg_marketing = df["marketing_spend"].mean()
    return (
        f"Rows: {n_rows}, Columns: {n_cols}\n"
        f"Date range: {start_date} to {end_date}\n"
        f"Total revenue: ${total_revenue:,.0f}\n"
        f"Total units sold: {total_units:,.0f}\n"
        f"Average marketing spend per record: ${avg_marketing:,.0f}"
    )


def _top_and_bottom(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    return by_product, by_region


def _detect_trends(df: pd.DataFrame) -> List[str]:
    df_daily = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )
    revenues = df_daily["revenue"].values
    if len(revenues) < 2:
        return ["Not enough data to infer trends."]

    x = np.arange(len(revenues))
    coeffs = np.polyfit(x, revenues, 1)
    slope = coeffs[0]
    trend_desc = []
    if slope > 0:
        trend_desc.append("Overall revenue is trending upward over time.")
    elif slope < 0:
        trend_desc.append("Overall revenue is trending downward over time.")
    else:
        trend_desc.append("Overall revenue is relatively flat over time.")

    weekend_mask = pd.to_datetime(df["date"]).dt.weekday >= 5
    weekend_rev = df.loc[weekend_mask, "revenue"].mean()
    weekday_rev = df.loc[~weekend_mask, "revenue"].mean()
    if weekend_rev > weekday_rev * 1.05:
        trend_desc.append("Weekend revenue is slightly higher than weekday revenue.")

    return trend_desc


def _detect_anomalies(df: pd.DataFrame) -> List[str]:
    messages: List[str] = []
    df_daily = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
        .sort_values("date")
    )
    revenues = df_daily["revenue"]
    mean_rev = revenues.mean()
    std_rev = revenues.std(ddof=0)
    if std_rev == 0 or len(revenues) < 5:
        return ["No strong anomalies detected in daily revenue."]

    z_scores = (revenues - mean_rev) / std_rev
    high_anoms = df_daily.loc[z_scores > 2.5]
    low_anoms = df_daily.loc[z_scores < -2.5]

    for _, row in high_anoms.iterrows():
        messages.append(
            f"Unusually high revenue of ${row['revenue']:,.0f} on {row['date'].date()}."
        )
    for _, row in low_anoms.iterrows():
        messages.append(
            f"Unusually low revenue of ${row['revenue']:,.0f} on {row['date'].date()}."
        )

    if not messages:
        messages.append("No strong revenue anomalies detected.")
    return messages


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def create_charts(df: pd.DataFrame, charts_dir: str) -> Dict[str, str]:
    _ensure_dir(charts_dir)
    df["date"] = pd.to_datetime(df["date"])

    # Revenue trend chart
    daily = df.groupby("date")["revenue"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(daily["date"], daily["revenue"], marker="o", linewidth=1)
    ax.set_title("Revenue Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue")
    ax.grid(True, alpha=0.3)
    trend_path = os.path.join(charts_dir, "revenue_trend.png")
    fig.tight_layout()
    fig.savefig(trend_path)
    plt.close(fig)

    # Product performance chart
    by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    by_product.plot(kind="bar", ax=ax, color="#1f77b4")
    ax.set_title("Revenue by Product")
    ax.set_xlabel("Product")
    ax.set_ylabel("Revenue")
    ax.grid(axis="y", alpha=0.3)
    prod_path = os.path.join(charts_dir, "product_performance.png")
    fig.tight_layout()
    fig.savefig(prod_path)
    plt.close(fig)

    # Region comparison chart
    by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    by_region.plot(kind="bar", ax=ax, color="#ff7f0e")
    ax.set_title("Revenue by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue")
    ax.grid(axis="y", alpha=0.3)
    region_path = os.path.join(charts_dir, "region_comparison.png")
    fig.tight_layout()
    fig.savefig(region_path)
    plt.close(fig)

    visual_analysis = [
        "Revenue trend over time showing overall movement and volatility.",
        "Product-level revenue comparison highlighting top and lagging products.",
        "Regional revenue comparison making weaker regions easy to spot.",
    ]

    return {
        "revenue_trend": trend_path,
        "product_performance": prod_path,
        "region_comparison": region_path,
    }, visual_analysis


def analyze_dataset(df: pd.DataFrame, charts_dir: str) -> AnalysisResult:
    """
    Core pandas/matplotlib analysis pipeline.
    """
    dataset_summary = _describe_dataset(df)
    by_product, by_region = _top_and_bottom(df)
    trends = _detect_trends(df)
    anomalies = _detect_anomalies(df)

    top_product = by_product.idxmax()
    weakest_product = by_product.idxmin()
    strongest_region = by_region.idxmax()
    weakest_region = by_region.idxmin()

    key_insights = [
        f"Top performing product by revenue: {top_product} (${by_product.max():,.0f}).",
        f"Weakest product by revenue: {weakest_product} (${by_product.min():,.0f}).",
        f"Strongest region by revenue: {strongest_region} (${by_region.max():,.0f}).",
        f"Weakest region by revenue: {weakest_region} (${by_region.min():,.0f}).",
    ]
    key_insights.extend(trends)
    key_insights.extend(anomalies)

    charts, visual_analysis = create_charts(df, charts_dir)

    business_recommendations = [
        "Increase marketing investment in top performing products and replicate successful campaigns in weaker regions.",
        f"Investigate the drivers behind weak performance in {weakest_region} and adjust pricing, positioning, or local partnerships.",
        "Double down on weekend-focused campaigns to capitalize on stronger weekend performance.",
        "Run controlled experiments (A/B tests) on creative, channels, and offers to improve marketing efficiency.",
    ]

    action_plan = [
        "In the next 7 days, review channel-level performance for each region and reallocate 10–15% of spend from underperforming channels.",
        "Within 2 weeks, design and launch a weekend-focused promotion for top products in strong regions.",
        "Within 30 days, create a playbook of best-performing campaigns and roll them out to weaker regions.",
        "Set up a monthly performance review cadence using this BI agent to track the impact of changes.",
    ]

    stats_snapshot = {
        "top_product": top_product,
        "weakest_product": weakest_product,
        "strongest_region": strongest_region,
        "weakest_region": weakest_region,
        "trend_summary": " ".join(trends),
        "anomaly_summary": " ".join(anomalies),
    }

    return AnalysisResult(
        dataset_summary=dataset_summary,
        key_insights=key_insights,
        visual_analysis=visual_analysis,
        business_recommendations=business_recommendations,
        action_plan=action_plan,
        charts=charts,
        stats_snapshot=stats_snapshot,
    )

