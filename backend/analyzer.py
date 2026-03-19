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

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def analyze_dataset(df: pd.DataFrame, charts_dir: str) -> AnalysisResult:
    """
    Core pandas/matplotlib analysis pipeline, generalized for any CSV.
    """
    _ensure_dir(charts_dir)
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Try to find a date column
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    if not date_cols:
        for col in cat_cols:
            if "date" in col.lower() or "time" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_cols = [col]
                    cat_cols.remove(col)
                    break
                except:
                    pass

    metric = num_cols[0] if num_cols else "Count"
    if not num_cols:
        df["Count"] = 1
        metric = "Count"

    # Quick Summary
    n_rows, n_cols = df.shape
    dataset_summary = f"Rows: {n_rows}, Columns: {n_cols}\n"
    if date_cols and not pd.isna(df[date_cols[0]].min()):
        dataset_summary += f"Date range: {df[date_cols[0]].min().date()} to {df[date_cols[0]].max().date()}\n"
    dataset_summary += f"Total {metric}: {df[metric].sum():,.0f}"

    # Top & Bottom Categories logic
    key_insights = []
    stats = {}
    
    if cat_cols:
        cat1 = cat_cols[0]
        by_cat1 = df.groupby(cat1)[metric].sum().sort_values(ascending=False)
        stats["cat1_name"] = str(cat1)
        stats["top_cat1"] = str(by_cat1.index[0])
        stats["weakest_cat1"] = str(by_cat1.index[-1])
        stats["top_product"] = str(by_cat1.index[0]) # For legacy
        stats["weakest_product"] = str(by_cat1.index[-1]) # For legacy
        key_insights.append(f"Top {cat1}: {stats['top_cat1']} ({by_cat1.max():,.0f})")
        key_insights.append(f"Weakest {cat1}: {stats['weakest_cat1']} ({by_cat1.min():,.0f})")
        
        if len(cat_cols) > 1:
            cat2 = cat_cols[1]
            by_cat2 = df.groupby(cat2)[metric].sum().sort_values(ascending=False)
            stats["cat2_label"] = str(cat2)
            stats["strongest_cat2"] = str(by_cat2.index[0])
            stats["weakest_cat2"] = str(by_cat2.index[-1])
            stats["strongest_region"] = str(by_cat2.index[0]) # For legacy
            stats["weakest_region"] = str(by_cat2.index[-1]) # For legacy
            key_insights.append(f"Top {cat2}: {stats['strongest_cat2']} ({by_cat2.max():,.0f})")
            key_insights.append(f"Weakest {cat2}: {stats['weakest_cat2']} ({by_cat2.min():,.0f})")
        else:
            stats.update({"strongest_cat2": "N/A", "weakest_cat2": "N/A", "cat2_label": "Segment"})
    else:
        stats.update({"top_cat1": "N/A", "weakest_cat1": "N/A", "cat1_name": "Category"})
        stats.update({"strongest_cat2": "N/A", "weakest_cat2": "N/A", "cat2_label": "Segment"})

    # Trends if dates exist
    if date_cols:
        daily = df.groupby(date_cols[0])[metric].sum().reset_index().sort_values(date_cols[0])
        if len(daily) > 2:
            x = np.arange(len(daily))
            slope = np.polyfit(x, daily[metric].values, 1)[0]
            if slope > 0:
                key_insights.append(f"{metric.title()} is trending upward over time.")
            elif slope < 0:
                key_insights.append(f"{metric.title()} is trending downward over time.")
            else:
                key_insights.append(f"{metric.title()} is relatively stable.")

    # Generate Dummy/Standard charts for backend compatibility
    charts = {}
    visual_analysis = ["Dynamic visualizations based on the dataset structure."]
    # The frontend ignores these pngs anyway, but we return an empty dict or lightweight png to satisfy typing if strictly needed.
    # To be safe and save compute, we skip png generation since frontend uses Plotly.
    
    business_recommendations = [
        f"Investigate top performing segments in the data to understand the drivers behind {metric}.",
        "Reallocate resources from bottom performing segments to maximize return on investment.",
        "Use these insights to build targeted campaigns for specific segments."
    ]

    action_plan = [
        "Review this data with the core business team.",
        "Generate a detailed report for the top segment.",
        "Implement A/B testing on underperforming segments."
    ]

    return AnalysisResult(
        dataset_summary=dataset_summary,
        key_insights=key_insights,
        visual_analysis=visual_analysis,
        business_recommendations=business_recommendations,
        action_plan=action_plan,
        charts=charts,
        stats_snapshot=stats
    )
