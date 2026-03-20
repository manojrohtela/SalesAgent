import sys
import os

# Fix Python Path resolution for Streamlit Community Cloud
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import io
import json
import time
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import streamlit.components.v1 as components


BACKEND_URL = os.environ.get("BI_AGENT_BACKEND_URL", "http://localhost:8000")
DEMO_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "demo_dataset.csv")


st.set_page_config(
    page_title="AI Business Intelligence Agent",
    layout="wide",
)

st.markdown(
    """
<style>
  :root{
    --bg: #0f172a;
    --panel: rgba(255,255,255,0.04);
    --panel2: rgba(255,255,255,0.06);
    --text: rgba(255,255,255,0.92);
    --muted: rgba(255,255,255,0.65);
    --border: rgba(255,255,255,0.10);
    --accent: #6366f1;
    --success: #22c55e;
    --warning: #f59e0b;
  }

  /* App background */
  .stApp { background: var(--bg); }
  header, [data-testid="stToolbar"] { visibility: hidden; height: 0px; }

  /* Typography tweaks */
  html, body, [class*="css"]  { color: var(--text); }
  .small-muted { color: var(--muted); font-size: 0.95rem; }

  /* Metric cards */
  .metric-grid{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-top: 10px;
    margin-bottom: 12px;
  }
  @media (max-width: 1100px){
    .metric-grid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  @media (max-width: 620px){
    .metric-grid{ grid-template-columns: 1fr; }
  }
  .metric-card{
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px 14px 12px 14px;
    background: linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(34,197,94,0.10) 55%, rgba(245,158,11,0.12) 100%);
    box-shadow: 0 14px 40px rgba(0,0,0,0.30);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    position: relative;
    overflow: hidden;
  }
  .metric-card:hover{
    transform: translateY(-3px);
    box-shadow: 0 18px 55px rgba(0,0,0,0.38);
    border-color: rgba(99,102,241,0.45);
  }
  .metric-label{
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.70);
    margin-bottom: 8px;
  }
  .metric-value{
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1.1;
  }
  .metric-sub{
    margin-top: 6px;
    color: rgba(255,255,255,0.70);
    font-size: 0.92rem;
  }

  /* Entrance Animations */
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .metric-card {
    animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
  }
  div[data-testid="column"]:nth-child(1) .metric-card { animation-delay: 0.05s; }
  div[data-testid="column"]:nth-child(2) .metric-card { animation-delay: 0.15s; }
  div[data-testid="column"]:nth-child(3) .metric-card { animation-delay: 0.25s; }
  div[data-testid="column"]:nth-child(4) .metric-card { animation-delay: 0.35s; }

  /* Plotly Chart Entrance Animations */
  div[data-testid="stPlotlyChart"] {
    opacity: 0;
    animation: fadeInUp 0.85s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }
  div[data-testid="column"]:nth-child(1) div[data-testid="stPlotlyChart"] { animation-delay: 0.3s; }
  div[data-testid="column"]:nth-child(2) div[data-testid="stPlotlyChart"] { animation-delay: 0.5s; }
  div[data-testid="column"]:nth-child(3) div[data-testid="stPlotlyChart"] { animation-delay: 0.7s; }

  /* Panels */
  .panel{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.28);
  }
  .panel-title{
    font-size: 0.95rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.70);
    margin-bottom: 10px;
  }

  /* Chat */
  .chat-title{
    font-size: 1.05rem;
    font-weight: 700;
    margin-bottom: 6px;
  }
  .chat-sub{
    color: rgba(255,255,255,0.65);
    font-size: 0.92rem;
    margin-bottom: 10px;
  }
  .bubble{
    padding: 10px 12px;
    border-radius: 14px;
    margin: 8px 0;
    max-width: 92%;
    border: 1px solid rgba(255,255,255,0.10);
    line-height: 1.35;
    font-size: 0.95rem;
    word-wrap: break-word;
  }
  .bubble-ai{
    background: rgba(255,255,255,0.06);
    color: rgba(255,255,255,0.92);
  }
  .bubble-user{
    margin-left: auto;
    background: rgba(99,102,241,0.22);
    border-color: rgba(99,102,241,0.35);
  }
  .typing{
    display: inline-flex;
    gap: 5px;
    align-items: center;
    padding: 10px 12px;
    border-radius: 14px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    width: fit-content;
  }
  .dot{
    width: 7px;
    height: 7px;
    background: rgba(255,255,255,0.70);
    border-radius: 50%;
    animation: bounce 1.1s infinite ease-in-out;
  }
  .dot:nth-child(2){ animation-delay: 0.15s; }
  .dot:nth-child(3){ animation-delay: 0.3s; }
  @keyframes bounce{
    0%, 80%, 100% { transform: translateY(0); opacity: 0.6; }
    40% { transform: translateY(-5px); opacity: 1; }
  }

  /* Streamlit widget tweaks */
  [data-testid="stSidebar"]{ background: rgba(255,255,255,0.03); border-right: 1px solid rgba(255,255,255,0.08); }
  .stTextInput input{
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.92) !important;
  }
  .stButton button{
    border-radius: 12px !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    background: rgba(99,102,241,0.18) !important;
    color: rgba(255,255,255,0.92) !important;
    transition: transform .15s ease, background .15s ease;
  }
  .stButton button:hover{ transform: translateY(-1px); background: rgba(99,102,241,0.26) !important; }
</style>
""",
    unsafe_allow_html=True,
)


def _load_df_from_upload_or_demo(uploaded: Optional[st.runtime.uploaded_file_manager.UploadedFile]) -> pd.DataFrame:
    """Load CSV with flexible column support - date column is optional."""
    if uploaded is not None:
        df = pd.read_csv(io.StringIO(uploaded.getvalue().decode("utf-8")))
    else:
        df = pd.read_csv(DEMO_CSV_PATH)
    
    # Try to parse date column if it exists
    if "date" in df.columns:
        try:
            df["date"] = pd.to_datetime(df["date"])
        except Exception:
            pass  # If date parsing fails, leave as is
    
    return df


def _compute_kpis(df: pd.DataFrame) -> Dict[str, str]:
    """Compute KPIs with fully flexible column support."""
    kpis = {}
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    
    metric_col = numeric_cols[0] if numeric_cols else "Records"
    cat1_col = categorical_cols[0] if categorical_cols else "Category 1"
    cat2_col = categorical_cols[1] if len(categorical_cols) > 1 else cat1_col

    kpis["metric_name"] = metric_col.title()
    kpis["cat1_name"] = cat1_col.title()
    kpis["cat2_name"] = cat2_col.title() if len(categorical_cols) > 1 else cat1_col.title()
    kpis["cat2_label"] = cat2_col.title() if len(categorical_cols) > 1 else "Segment"

    # Total metric
    if numeric_cols:
        total_val = float(df[metric_col].sum())
        prefix = "$" if "rev" in metric_col.lower() or "sales" in metric_col.lower() or "spend" in metric_col.lower() else ""
        kpis["total_metric"] = f"{prefix}{total_val:,.0f}"
        kpis["total_metric_raw"] = str(total_val)
        kpis["metric_prefix"] = prefix
    else:
        kpis["total_metric"] = str(len(df))
        kpis["total_metric_raw"] = str(len(df))
        kpis["metric_prefix"] = ""
    
    # Top cat1
    if categorical_cols and numeric_cols:
        by_cat1 = df.groupby(cat1_col)[metric_col].sum().sort_values(ascending=False)
        kpis["top_cat1"] = str(by_cat1.index[0])
    else:
        kpis["top_cat1"] = "N/A"
    
    # Strongest/Weakest cat2
    if categorical_cols and numeric_cols:
        by_cat2 = df.groupby(cat2_col)[metric_col].sum().sort_values(ascending=False)
        kpis["strongest_cat2"] = str(by_cat2.index[0])
        kpis["weakest_cat2"] = str(by_cat2.index[-1])
    else:
        kpis["strongest_cat2"] = "N/A"
        kpis["weakest_cat2"] = "N/A"
    
    return kpis


def _trend_direction(df: pd.DataFrame) -> str:
    """Determine trend direction with flexible column support."""
    try:
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
        if not datetime_cols:
            return "N/A"
        date_col = datetime_cols[0]
        
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_cols:
            return "N/A"
        metric_col = numeric_cols[0]
        
        daily = df.groupby(df[date_col].dt.date)[metric_col].sum().reset_index(name="value")
        if len(daily) < 10:
            return "mixed"
        
        x = range(len(daily))
        k = max(3, int(len(daily) * 0.2))
        start_avg = daily["value"].head(k).mean()
        end_avg = daily["value"].tail(k).mean()
        if end_avg > start_avg * 1.05:
            return "increasing"
        if end_avg < start_avg * 0.95:
            return "declining"
        return "stable"
    except Exception:
        return "N/A"


def _insight_bullets(df: pd.DataFrame, kpis: Dict[str, str]) -> List[str]:
    trend = _trend_direction(df)
    return [
        f"Top {kpis['cat1_name']}: **{kpis['top_cat1']}**",
        f"Strongest {kpis.get('cat2_label', 'Segment')}: **{kpis['strongest_cat2']}**",
        f"Weakest {kpis.get('cat2_label', 'Segment')}: **{kpis['weakest_cat2']}**",
        f"{kpis['metric_name']} trend: **{trend}**",
    ]


def _plotly_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="rgba(255,255,255,0.88)"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    return fig


def _charts(df: pd.DataFrame) -> Tuple:
    """Generate charts with flexible column support."""
    figs = []
    
    # Try to create trend chart if we have a date column and numeric column
    try:
        if "date" in df.columns:
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                daily = df.groupby(df["date"].dt.date)[numeric_cols[0]].sum().reset_index()
                daily.columns = ["date", "value"]
                fig_trend = px.line(
                    daily,
                    x="date",
                    y="value",
                    title="Trend Over Time",
                    markers=True,
                    color_discrete_sequence=["#6366f1"],
                )
                fig_trend.update_traces(line=dict(width=3), hovertemplate="Date=%{x}<br>Value=%{y:,.0f}<extra></extra>")
                fig_trend = _plotly_theme(fig_trend)
                figs.append(fig_trend)
    except Exception:
        pass  # Skip if trend chart fails
    
    # Try to create product/category chart
    try:
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        
        if categorical_cols and numeric_cols:
            by_cat = df.groupby(categorical_cols[0])[numeric_cols[0]].sum().reset_index().sort_values(numeric_cols[0], ascending=False)
            fig_cat = px.bar(
                by_cat,
                x=categorical_cols[0],
                y=numeric_cols[0],
                title=f"{categorical_cols[0].title()} Performance",
                color=categorical_cols[0],
                color_discrete_sequence=["#6366f1", "#22c55e", "#f59e0b", "#38bdf8", "#a78bfa"],
            )
            fig_cat.update_traces(hovertemplate=f"{categorical_cols[0]}=%{{x}}<br>{numeric_cols[0]}=%{{y:,.0f}}<extra></extra>")
            fig_cat.update_layout(showlegend=False)
            fig_cat = _plotly_theme(fig_cat)
            figs.append(fig_cat)
    except Exception:
        pass  # Skip if category chart fails
    
    # If we have 2+ numeric columns, create a scatter or second bar
    try:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        
        if len(numeric_cols) >= 2 and categorical_cols:
            by_cat2 = df.groupby(categorical_cols[0])[numeric_cols[1]].sum().reset_index().sort_values(numeric_cols[1], ascending=False)
            fig_cat2 = px.bar(
                by_cat2,
                x=categorical_cols[0],
                y=numeric_cols[1],
                title=f"{categorical_cols[0].title()} - {numeric_cols[1].title()}",
                color=categorical_cols[0],
                color_discrete_sequence=["#22c55e", "#6366f1", "#f59e0b", "#fb7185", "#38bdf8"],
            )
            fig_cat2.update_traces(hovertemplate=f"{categorical_cols[0]}=%{{x}}<br>{numeric_cols[1]}=%{{y:,.0f}}<extra></extra>")
            fig_cat2.update_layout(showlegend=False)
            fig_cat2 = _plotly_theme(fig_cat2)
            figs.append(fig_cat2)
    except Exception:
        pass  # Skip if second chart fails

    # Fallback 1: Distribution of secondary categorical
    if len(figs) < 3 and len(categorical_cols) > 1:
        try:
            val_counts = df[categorical_cols[1]].value_counts().reset_index()
            val_counts.columns = [categorical_cols[1], 'Count']
            fig_f1 = px.bar(val_counts, x=categorical_cols[1], y='Count', title=f"{categorical_cols[1].title()} Distribution", color=categorical_cols[1], color_discrete_sequence=["#f59e0b", "#38bdf8", "#fb7185"])
            fig_f1.update_layout(showlegend=False)
            fig_f1 = _plotly_theme(fig_f1)
            figs.append(fig_f1)
        except Exception:
            pass

    # Fallback 2: Scatter correlation of numeric points
    if len(figs) < 3 and len(numeric_cols) > 1:
        try:
            fig_f2 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{numeric_cols[0].title()} vs {numeric_cols[1].title()}", color=categorical_cols[0] if categorical_cols else None, color_discrete_sequence=["#a78bfa", "#6366f1", "#f59e0b"])
            fig_f2 = _plotly_theme(fig_f2)
            figs.append(fig_f2)
        except Exception:
            pass

    # Fallback 3: Metric spread
    if len(figs) < 3 and len(numeric_cols) > 0:
        try:
            fig_f3 = px.box(df, y=numeric_cols[0], title=f"{numeric_cols[0].title()} Overview Spread", color_discrete_sequence=["#22c55e"])
            fig_f3 = _plotly_theme(fig_f3)
            figs.append(fig_f3)
        except Exception:
            pass
            
    # Return at least one figure or placeholder
    if len(figs) == 0:
        # Create a simple summary if no charts possible
        fig_placeholder = px.bar(
            x=["No categorical data"],
            y=[1],
            title="Data Summary",
            color_discrete_sequence=["#6366f1"]
        )
        fig_placeholder = _plotly_theme(fig_placeholder)
        figs.append(fig_placeholder)
    
    # Pad to return 3 figures for UI consistency
    while len(figs) < 3:
        figs.append(None)
    
    return tuple(figs[:3])


def _advanced_charts(df: pd.DataFrame) -> Tuple:
    """Generate advanced statistical charts: Correlation Heatmap, Moving Averages, and Forecasts."""
    import numpy as np
    figs = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
    
    if not date_cols:
        for c in df.columns:
            if "date" in c.lower() or "time" in c.lower():
                try: df[c] = pd.to_datetime(df[c]); date_cols = [c]; break
                except: pass

    metric = next((c for c in num_cols if 'revenue' in c.lower() or 'sales' in c.lower()), num_cols[0] if num_cols else None)
    
    # 1. Trend & Moving Average
    if date_cols and metric:
        try:
            daily = df.groupby(date_cols[0])[metric].sum().reset_index().sort_values(date_cols[0])
            if len(daily) > 7:
                daily['7-Day MA'] = daily[metric].rolling(window=7, min_periods=1).mean()
                
                fig_ma = px.line(daily, x=date_cols[0], y=[metric, '7-Day MA'], title=f"{metric.title()} with 7-Day Moving Avg")
                fig_ma.update_traces(line=dict(width=3))
                fig_ma = _plotly_theme(fig_ma)
                figs.append(fig_ma)
                
                # 2. Linear Forecast
                x = np.arange(len(daily))
                y = daily[metric].values
                slope, intercept = np.polyfit(x, y, 1)
                daily['Forecast'] = (slope * x) + intercept
                
                fig_fc = px.scatter(daily, x=date_cols[0], y=metric, title=f"Linear Forecast: {metric.title()}", opacity=0.5)
                fig_fc.add_scatter(x=daily[date_cols[0]], y=daily['Forecast'], mode='lines', name='Trendline')
                fig_fc = _plotly_theme(fig_fc)
                fig_fc.update_layout(showlegend=False)
                figs.append(fig_fc)
        except Exception:
            pass

    # 3. Correlation Heatmap
    if len(num_cols) > 1:
        try:
            corr = df[num_cols].corr()
            fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="Purpor", title="Numeric Correlation Matrix")
            fig_corr = _plotly_theme(fig_corr)
            figs.append(fig_corr)
        except Exception:
            pass

    # Fallback 1: Distribution Histogram
    if metric and len(figs) < 3:
        try:
            fig_hist = px.histogram(df, x=metric, marginal="box", title=f"Statistical Distribution: {metric.title()}", color_discrete_sequence=["#38bdf8"])
            fig_hist = _plotly_theme(fig_hist)
            figs.append(fig_hist)
        except Exception:
            pass
            
    # Fallback 2: Variance Box Plot by Top Category
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if metric and cat_cols and len(figs) < 3:
        try:
            fig_box = px.box(df, x=cat_cols[0], y=metric, title=f"Variance Analysis by {cat_cols[0].title()}", color=cat_cols[0], color_discrete_sequence=["#a78bfa", "#f59e0b", "#38bdf8", "#fb7185"])
            fig_box.update_layout(showlegend=False)
            fig_box = _plotly_theme(fig_box)
            figs.append(fig_box)
        except Exception:
            pass
            
    # Fallback 3: Proportional Donut Chart
    if metric and cat_cols and len(cat_cols) > 1 and len(figs) < 3:
        try:
            by_cat2 = df.groupby(cat_cols[1])[metric].sum().reset_index()
            fig_pie = px.pie(by_cat2, names=cat_cols[1], values=metric, hole=0.4, title=f"Proportional Contribution by {cat_cols[1].title()}")
            fig_pie = _plotly_theme(fig_pie)
            figs.append(fig_pie)
        except Exception:
            pass
            
    # Pad to 3
    while len(figs) < 3:
        figs.append(None)
        
    return tuple(figs[:3])


def call_backend_analyze(
    question: Optional[str] = "",
    uploaded_file: Optional[bytes] = None,
    use_demo: bool = True,
):
    try:
        # NATIVELY RUN THE ENGINE IN-MEMORY (Bypasses Vercel/FastAPI entirely!)
        # Perfect for deploying as a 100% monolithic app on Streamlit Community Cloud
        import io
        import pandas as pd
        from backend.agent import _run_full_analysis, _ensure_demo_dataset, generate_demo_dataset

        if uploaded_file is not None:
            df = pd.read_csv(io.BytesIO(uploaded_file))
        elif use_demo:
            df = _ensure_demo_dataset()
        else:
            df = generate_demo_dataset()
            
        print("Running native LLM agent analysis...")
        response = _run_full_analysis(df, user_question=question or "")
        return {
            "structured_report": response.structured_report,
            "charts": response.charts,
            "follow_up_questions": response.follow_up_questions
        }
    except Exception as e:
        print(f"Fallback to API proxy failed: {e}")
        # Legacy fallback if running purely as frontend
        import requests
        params = {"use_demo": str(use_demo).lower(), "question": question or ""}
        files = None
        if uploaded_file is not None:
            files = {"file": ("dataset.csv", uploaded_file, "text/csv")}

        resp = requests.post(f"{BACKEND_URL}/analyze", params=params, files=files, timeout=60)
        resp.raise_for_status()
        return resp.json()


with st.sidebar:
    st.header("Dataset")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    st.caption(
        "If you don't upload a file, a realistic demo dataset will be generated automatically."
    )

    auto_run = st.checkbox("Auto-run analysis on load", value=True)
    run_button = st.button("Run Analysis", use_container_width=True)

if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

should_run = False
has_data = uploaded is not None
if auto_run and st.session_state.analysis is None and has_data:
    should_run = True
if run_button:
    should_run = True

if should_run:
    with st.spinner(""):
        status = st.empty()
        status.markdown("<div class='small-muted'>Analyzing dataset...</div>", unsafe_allow_html=True)
        time.sleep(0.35)
        status.markdown("<div class='small-muted'>Generating insights...</div>", unsafe_allow_html=True)
        time.sleep(0.35)
        status.markdown("<div class='small-muted'>Building visualizations...</div>", unsafe_allow_html=True)
        time.sleep(0.35)

        uploaded_bytes = uploaded.getvalue() if uploaded is not None else None
        analysis = call_backend_analyze(
            question="",
            uploaded_file=uploaded_bytes,
            use_demo=uploaded is None,
        )
        st.session_state.analysis = analysis
        status.empty()

analysis = st.session_state.analysis

# Only load and display data if a file was uploaded or analysis was run
if has_data or analysis is not None:
    df = _load_df_from_upload_or_demo(uploaded)
    kpis = _compute_kpis(df)
    bullets = _insight_bullets(df, kpis)
    fig_trend, fig_product, fig_region = _charts(df)
    fig_ma, fig_fc, fig_corr = _advanced_charts(df)
    data_ready = True
else:
    data_ready = False

st.markdown(
    """
<div style="display:flex; align-items:flex-end; justify-content:space-between; gap: 18px;">
  <div>
    <div style="font-size:2.0rem; font-weight:800; letter-spacing:-0.02em;">AI Business Intelligence Agent</div>
    <div class="small-muted" style="margin-top:4px;">Analyze business performance and generate insights in seconds.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if not data_ready:
    st.info("📤 **Upload a CSV file to get started!** Once you upload your data, analysis and insights will appear here.")
else:
    st.markdown(
        f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">Total {kpis.get('metric_name', 'Metric')}</div>
    <div class="metric-value" data-target="{kpis.get('total_metric_raw', '0')}" data-prefix="{kpis.get('metric_prefix', '')}" id="kpi_total_revenue">{kpis.get('total_metric', '0')}</div>
    <div class="metric-sub">All regions • All categories</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Top {kpis.get('cat1_name', 'Category')}</div>
    <div class="metric-value">{kpis.get('top_cat1', 'N/A')}</div>
    <div class="metric-sub">Highest volume driver</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Strongest {kpis.get('cat2_label', 'Segment')}</div>
    <div class="metric-value">{kpis.get('strongest_cat2', 'N/A')}</div>
    <div class="metric-sub">Best performance</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Weakest {kpis.get('cat2_label', 'Segment')}</div>
    <div class="metric-value">{kpis.get('weakest_cat2', 'N/A')}</div>
    <div class="metric-sub">Primary growth opportunity</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Animated KPI counter (rendered safely via an HTML component to avoid f-string brace issues)
    components.html(
        f"""
<script>
(() => {{
  const el = window.parent.document.getElementById("kpi_total_revenue");
  if (!el) return;
  const target = parseFloat(el.getAttribute("data-target") || "0");
  const prefix = el.getAttribute("data-prefix") || "";
  const duration = 950;
  const start = performance.now();
  const fmt = (n) => prefix + Math.round(n).toLocaleString();
  const tick = (t) => {{
    const p = Math.min(1, (t - start) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    el.textContent = fmt(target * eased);
    if (p < 1) requestAnimationFrame(tick);
  }};
  requestAnimationFrame(tick);
}})();
</script>
""",
        height=0,
    )

    # Expand visualizations to full width using 3 equally spaced columns
    col1, col2, col3 = st.columns(3, gap="large")
    
    standard_figures = [fig_trend, fig_product, fig_region]
    standard_cols = [col1, col2, col3]
    
    for i, col in enumerate(standard_cols):
        with col:
            fig = standard_figures[i] if i < len(standard_figures) else None
            if fig is not None:
                title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else "Performance Breakdown"
                fig.update_layout(title=None)
                st.markdown(f"<div class='panel'><div class='panel-title'>{title}</div></div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown("<div class='panel'><div class='panel-title'>Performance Breakdown</div></div>", unsafe_allow_html=True)
                st.info("Insufficient column dimensions for this chart")

    st.markdown("<br><div style='font-size:1.4rem; font-weight:800; letter-spacing:-0.02em; margin-bottom: 2px;'>Advanced Predictive Analytics</div>", unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3, gap="large")
    
    advanced_figures = [fig_ma, fig_fc, fig_corr]
    advanced_cols = [col4, col5, col6]
    
    for i, col in enumerate(advanced_cols):
        with col:
            fig = advanced_figures[i] if i < len(advanced_figures) else None
            if fig is not None:
                title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else "Analytical Insight"
                fig.update_layout(title=None)
                st.markdown(f"<div class='panel'><div class='panel-title'>{title}</div></div>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.markdown("<div class='panel'><div class='panel-title'>Analytical Insight</div></div>", unsafe_allow_html=True)
                st.info("Insufficient dimensional data for further visualization")

    # Display dynamic chart if one was generated by AI query
    if analysis is not None and analysis.get("charts", {}).get("dynamic_chart"):
        try:
            dynamic_chart_data = analysis["charts"]["dynamic_chart"]
            if isinstance(dynamic_chart_data, dict) and "data" in dynamic_chart_data:
                chart_json = dynamic_chart_data["data"]
            elif isinstance(dynamic_chart_data, str):
                chart_json = dynamic_chart_data
            else:
                chart_json = None
            
            if chart_json:
                if isinstance(chart_json, str):
                    chart_json = json.loads(chart_json)
                st.markdown("<br><div class='panel'><div class='panel-title'>AI-Generated Custom Chart</div></div>", unsafe_allow_html=True)
                st.plotly_chart(chart_json, use_container_width=True, config={"displayModeBar": False})
        except Exception as e:
            st.warning(f"Could not render dynamic chart: {str(e)}")

    # Full report & Insights
    st.markdown("<br><div class='panel'><div class='panel-title'>Key Insights</div></div>", unsafe_allow_html=True)
    for b in bullets:
        st.markdown(f"- {b}")

    if analysis is not None:
        with st.expander("📝 View Full Strategic AI Analysis", expanded=False):
            st.markdown(analysis.get("structured_report", ""))
            if analysis.get("follow_up_questions"):
                st.markdown("**Proactive follow-ups**")
                for q in analysis.get("follow_up_questions", []):
                    st.markdown(f"- {q}")
    else:
        st.info("Run analysis to generate the strategic AI report.")

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # Apply Custom CSS for Modern Floating Action Button & Chat Panel using RAW HTML
    st.markdown("""
    <style>
    /* Raw HTML FAB Button */
    .floating-chat-button {
        position: fixed;
        bottom: 25px;
        right: 25px;
        width: 65px;
        height: 65px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        cursor: pointer;
        box-shadow: 0px 8px 25px rgba(99,102,241, 0.45);
        z-index: 999999;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        user-select: none;
    }
    .floating-chat-button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0px 12px 35px rgba(99,102,241, 0.6);
    }
    
    /* Dedicated Close Button inside Panel */
    .close-chat-btn {
        background: transparent;
        border: none;
        color: rgba(255,255,255,0.6);
        font-size: 1.2rem;
        cursor: pointer;
        float: right;
    }
    .close-chat-btn:hover {
        color: white;
    }

    /* Floating Chat Panel Container */
    div.element-container:has(#chat-panel-anchor) + div[data-testid="stVerticalBlock"] {
        position: fixed !important;
        bottom: 105px !important;
        right: 25px !important;
        width: 370px !important;
        height: 530px !important;
        max-width: 90vw !important;
        max-height: 80vh !important;
        background-color: #0f172a !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 45px rgba(0,0,0,0.5) !important;
        z-index: 999998 !important;
        padding: 20px !important;
        animation: chatFade 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        display: none; /* Javascript will toggle this to 'flex' */
        flex-direction: column !important;
        overflow: hidden !important;
    }
    
    @keyframes chatFade {
        from { opacity: 0; transform: translateY(20px) scale(0.96); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    </style>
    
    <!-- PURE HTML FLOATING ACTION BUTTON -->
    <div id="fab-btn" class="floating-chat-button" onclick="
        const panel = window.parent.document.querySelector('div.element-container:has(#chat-panel-anchor) + div[data-testid=\\'stVerticalBlock\\']');
        if(panel) {
            const isHidden = (panel.style.display === 'none' || panel.style.display === '');
            panel.style.display = isHidden ? 'flex' : 'none';
            this.innerHTML = isHidden ? '✖' : '💬';
            sessionStorage.setItem('st_chat_state', isHidden ? 'open' : 'closed');
        }
    ">💬</div>
    
    <!-- RESTORE STATE LISTENER FOR STREAMLIT RERUNS -->
    <script>
    setTimeout(() => {
        const state = sessionStorage.getItem('st_chat_state');
        const panel = window.parent.document.querySelector('div.element-container:has(#chat-panel-anchor) + div[data-testid=\\'stVerticalBlock\\']');
        const btn = window.parent.document.getElementById('fab-btn');
        if(state === 'open' && panel && btn) {
            panel.style.display = 'flex';
            btn.innerHTML = '✖';
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)

    # Force open state if assistant is processing a message
    if st.session_state.is_typing:
        st.markdown("<script>sessionStorage.setItem('st_chat_state', 'open');</script>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # Render Floating Chat Panel Base (Always rendered, hidden via CSS initially)
    # ---------------------------------------------------------
    st.markdown("<div id='chat-panel-anchor'></div>", unsafe_allow_html=True)
    with st.container():
        # Panel Header
        col_t, col_x = st.columns([5, 1])
        with col_t:
            st.markdown("<div style='font-size: 1.15rem; font-weight: 800; color: white;'>AI Analyst ✨</div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8; margin-bottom: 12px;'>Ask business queries or request custom charts.</div>", unsafe_allow_html=True)
        with col_x:
            st.markdown("""
                <button class="close-chat-btn" onclick="
                    const panel = window.parent.document.querySelector('div.element-container:has(#chat-panel-anchor) + div[data-testid=\\'stVerticalBlock\\']');
                    const btn = window.parent.document.getElementById('fab-btn');
                    if(panel) panel.style.display = 'none';
                    if(btn) btn.innerHTML = '💬';
                    sessionStorage.setItem('st_chat_state', 'closed');
                ">✖</button>
            """, unsafe_allow_html=True)
            
            # Scrollable Chat Area
            chat_container = st.container(height=350, border=False)
            with chat_container:
                if len(st.session_state.messages) == 0:
                    st.info("I'm ready! Some things you can ask me:\n\n- How to boost weakest segments?\n- Recommend a marketing strategy.\n- Show me a dynamic pie chart.")
                
                for m in st.session_state.messages:
                    with st.chat_message(m["role"]):
                        st.markdown(m["content"], unsafe_allow_html=True)
                        
                if st.session_state.is_typing:
                    with st.chat_message("assistant"):
                        st.markdown("🤔 *Analyzing data...*")
                        
            # Chat Input Form
            with st.form("chat_form", clear_on_submit=True, border=False):
                col_input, col_btn = st.columns([4, 1], gap="small")
                with col_input:
                    q = st.text_input("Ask...", label_visibility="collapsed", placeholder="Type your request here...")
                with col_btn:
                    submit = st.form_submit_button("Send", use_container_width=True)
                    
                if submit and q and q.strip():
                    st.session_state.messages.append({"role": "user", "content": q.strip()})
                    st.session_state.is_typing = True
                    st.rerun()

            # Processing LLM response (when typing is flagged)
            if st.session_state.is_typing:
                last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
                uploaded_bytes = uploaded.getvalue() if uploaded is not None else None
                try:
                    resp = call_backend_analyze(
                        question=last_user,
                        uploaded_file=uploaded_bytes,
                        use_demo=uploaded is None,
                    )
                    st.session_state.analysis = resp
                    
                    dynamic_chart_note = ""
                    if resp.get("charts", {}).get("dynamic_chart"):
                        dynamic_chart_note = "\n\n*(I also generated an interactive dynamic chart for you! Check the main dashboard background.)*"
                    
                    report = (resp.get("structured_report") or "").strip()
                    display_text = report + dynamic_chart_note
                    st.session_state.messages.append({"role": "assistant", "content": display_text.replace("\n", "<br/>")})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"AI Engine Connection Error: {str(e)}"})
                finally:
                    st.session_state.is_typing = False
                    st.rerun()
