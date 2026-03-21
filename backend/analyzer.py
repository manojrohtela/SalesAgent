import os
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

@dataclass
class AnalysisResult:
    dataset_summary: str
    key_insights: List[str]
    visual_analysis: List[str]
    business_recommendations: List[str]
    action_plan: List[str]
    charts: Dict[str, Any]
    stats_snapshot: Dict[str, Any]

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
    stats["metric_name"] = str(metric)
    stats["total_metric"] = float(df[metric].sum())
    stats["average_metric"] = float(df[metric].mean())
    stats["row_count"] = int(n_rows)
    stats["column_count"] = int(n_cols)

    if date_cols and not pd.isna(df[date_cols[0]].min()):
        stats["date_range_start"] = str(df[date_cols[0]].min().date())
        stats["date_range_end"] = str(df[date_cols[0]].max().date())
    
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
            stats.update({
                "strongest_cat2": stats["top_cat1"],
                "weakest_cat2": stats["weakest_cat1"],
                "cat2_label": str(cat1),
                "strongest_region": stats["top_cat1"],
                "weakest_region": stats["weakest_cat1"],
            })
    else:
        stats.update({"top_cat1": "Overall", "weakest_cat1": "Overall", "cat1_name": "Category"})
        stats.update({
            "strongest_cat2": "Overall",
            "weakest_cat2": "Overall",
            "cat2_label": "Dataset",
            "strongest_region": "Overall",
            "weakest_region": "Overall",
        })

    # Distribution Analysis & Outliers
    mean_val = df[metric].mean()
    std_val = df[metric].std()
    outliers = df[metric][(df[metric] > mean_val + 2 * std_val) | (df[metric] < mean_val - 2 * std_val)]
    insight_dist = f"{metric.title()} averages {mean_val:,.0f} with a standard deviation of {std_val:,.0f}."
    if not outliers.empty:
        insight_dist += f" Detected {len(outliers)} significant outliers indicating high variability."
    key_insights.append(insight_dist)

    # Correlation Analysis
    if len(num_cols) > 1:
        corr_matrix = df[num_cols].corr()
        corr_unstacked = corr_matrix.abs().unstack()
        corr_unstacked = corr_unstacked[corr_unstacked < 1.0] # Remove self-correlation
        if not corr_unstacked.empty:
            max_corr_idx = corr_unstacked.idxmax()
            col_a, col_b = max_corr_idx
            val = corr_matrix.loc[col_a, col_b]
            
            desc = "strong positive" if val > 0.6 else "moderate positive" if val > 0.3 else "weak"
            if val < -0.3: desc = "moderate negative"
            if val < -0.6: desc = "strong negative"
            
            key_insights.append(f"{col_a.replace('_', ' ').title()} has a {desc} correlation ({val:.2f}) with {col_b.replace('_', ' ').title()}.")

    # Trends, Growth, & Forecasting if dates exist
    if date_cols:
        daily = df.groupby(date_cols[0])[metric].sum().reset_index().sort_values(date_cols[0])
        if len(daily) > 2:
            peak_row = daily.loc[daily[metric].idxmax()]
            trough_row = daily.loc[daily[metric].idxmin()]
            stats["peak_period_name"] = str(peak_row[date_cols[0]].date())
            stats["peak_period_value"] = float(peak_row[metric])
            stats["low_period_name"] = str(trough_row[date_cols[0]].date())
            stats["low_period_value"] = float(trough_row[metric])
            x = np.arange(len(daily))
            y = daily[metric].values
            
            # Growth Rate
            if y[0] != 0:
                growth_rate = ((y[-1] - y[0]) / abs(y[0])) * 100
                key_insights.append(f"Overall {metric.title()} grew by {growth_rate:.1f}% across the tracked period.")
                
            # Forecasting via Linear Regression
            slope, intercept = np.polyfit(x, y, 1)
            next_x = len(daily)
            forecast = (slope * next_x) + intercept
            key_insights.append(f"Next period's {metric.title()} is estimated at {forecast:,.0f} based on predictive linear trends.")

    # Generate React Recharts compatible JSON data
    charts = {}
    
    try:
        if date_cols:
            # daily trend
            daily_sum = df.groupby(date_cols[0])[metric].sum().reset_index().sort_values(date_cols[0])
            daily_sum[date_cols[0]] = daily_sum[date_cols[0]].dt.strftime('%b %d')
            charts["lineData"] = daily_sum.rename(columns={date_cols[0]: "name", metric: "value"}).to_dict(orient="records")
            
            # monthly area
            df_m = df.copy()
            df_m['month'] = df_m[date_cols[0]].dt.strftime('%b')
            monthly_sum = df_m.groupby('month')[metric].sum().reset_index()
            # Sort by actual month order
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            monthly_sum['m_val'] = pd.Categorical(monthly_sum['month'], categories=months, ordered=True)
            monthly_sum = monthly_sum.sort_values('m_val').drop('m_val', axis=1)
            charts["areaData"] = monthly_sum.rename(columns={"month": "name", metric: "value"}).to_dict(orient="records")
        else:
            charts["lineData"] = [{"name": "All", "value": int(df[metric].sum())}]
            charts["areaData"] = [{"name": "All", "value": int(df[metric].sum())}]

        if cat_cols:
            cat1 = cat_cols[0]
            by_cat1 = df.groupby(cat1)[metric].sum().sort_values(ascending=False).head(5).reset_index()
            charts["barData"] = by_cat1.rename(columns={cat1: "name", metric: "value"}).to_dict(orient="records")

            if len(cat_cols) > 1:
                cat2 = cat_cols[1]
                by_cat2 = df.groupby(cat2)[metric].sum().sort_values(ascending=False).head(4).reset_index()
                charts["pieData"] = by_cat2.rename(columns={cat2: "name", metric: "value"}).to_dict(orient="records")
            else:
                charts["pieData"] = by_cat1.rename(columns={cat1: "name", metric: "value"}).head(4).to_dict(orient="records")
        else:
            charts["barData"] = [{"name": "Overall", "value": int(df[metric].sum())}]
            charts["pieData"] = [{"name": "Overall", "value": int(df[metric].sum())}]
            
        # Convert values to native int/float to ensure JSON serialization compatibility
        for k in charts:
            for item in charts[k]:
                item['value'] = float(item['value']) if pd.notna(item['value']) else 0.0
                item['name'] = str(item['name'])

    except Exception as e:
        print(f"Error generating chart data: {e}")
        charts = {}
        
    visual_analysis = ["Dynamic visualizations based on the dataset structure."]
    
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
