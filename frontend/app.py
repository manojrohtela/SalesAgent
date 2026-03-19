import io
import json
import os
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
    with col1:
        st.markdown("<div class='panel'><div class='panel-title'>Trend Analysis</div></div>", unsafe_allow_html=True)
        if fig_trend is not None:
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this chart")
    with col2:
        st.markdown("<div class='panel'><div class='panel-title'>Performance Breakdown</div></div>", unsafe_allow_html=True)
        if fig_product is not None:
            st.plotly_chart(fig_product, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this chart")
    with col3:
        st.markdown(f"<div class='panel'><div class='panel-title'>{kpis.get('cat2_label', 'Segment')} Comparison</div></div>", unsafe_allow_html=True)
        if fig_region is not None:
            st.plotly_chart(fig_region, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this chart")

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

    # Apply Custom CSS for Floating Chat Box
    st.markdown("""
    <style>
    /* Base Chat Container */
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"] {
        position: fixed !important;
        bottom: 35px !important;
        right: 35px !important;
        z-index: 999999 !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* COLLAPSED STATE (Floating Button) */
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])) {
        width: 65px !important;
        height: 65px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        box-shadow: 0 10px 40px rgba(99,102,241, 0.45) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])):hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 50px rgba(99,102,241, 0.6) !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])) > details > summary {
        height: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        border-radius: 50% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])) > details > summary p {
        font-size: 0 !important; /* hide the text */
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])) > details > summary svg {
        display: none !important; /* hide default chevron */
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:not(:has(details[open])) > details > summary::before {
        content: '💬' !important;
        font-size: 28px !important;
        color: white !important;
        position: absolute !important;
    }

    /* OPEN STATE (Chat Window) */
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) {
        width: 450px !important;
        height: min(720px, 85vh) !important;
        max-width: 90vw !important;
        border-radius: 20px !important;
        background-color: #0f172a !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        display: flex !important;
        flex-direction: column !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) > details {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        border: none !important;
        margin: 0 !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) > details > summary {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        padding: 18px 24px !important;
        border-radius: 20px 20px 0 0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        border: none !important;
        margin-bottom: 0 !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) > details > summary p {
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        color: white !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) > details > summary svg {
        display: none !important; /* hide default chevron */
    }
    /* Simple close 'X' */
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpander"]:has(details[open]) > details > summary::after {
        content: '✖' !important;
        color: rgba(255,255,255,0.8) !important;
        font-size: 18px !important;
        position: absolute !important;
        right: 24px !important;
    }
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpanderDetails"] {
        padding: 16px !important;
        background-color: #1e293b !important;
        flex-grow: 1 !important;
        overflow-y: auto !important;
        border-radius: 0 0 20px 20px !important;
    }
    /* Additional fix for internal margins */
    div.element-container:has(#chat-expander-anchor) + div.element-container div[data-testid="stExpanderDetails"] > div > div {
        gap: 0 !important; /* Tighter chat elements */
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating Chat Window via Native Expander
    st.markdown("<div id='chat-expander-anchor'></div>", unsafe_allow_html=True)
    with st.expander("💬 Ask AI Analyst", expanded=False):
        st.markdown("<div style='font-size: 1.3rem; font-weight: 800; margin-bottom: 5px; color: white;'>AI Analyst ✨</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 15px;'>Ask business queries or request custom charts.</div>", unsafe_allow_html=True)
        
        chat_container = st.container(height=480)
        with chat_container:
            if len(st.session_state.messages) == 0:
                st.info("I'm ready! Some things you can ask me:\n\n- How to boost our weakest segments?\n- What's the general trend?\n- Create a pie chart for my categories.")
                
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"], unsafe_allow_html=True)
                    
            if st.session_state.is_typing:
                with st.chat_message("assistant"):
                    st.markdown("🤔 *Analyzing data...*")
                    
        # Text input handling inside Popover (st.chat_input may snap to bottom of screen natively, so we use form)
        with st.form("chat_form", clear_on_submit=True, border=False):
            col_input, col_btn = st.columns([4, 1], gap="small")
            with col_input:
                q = st.text_input("Ask a question...", label_visibility="collapsed", placeholder="Type your request here...")
            with col_btn:
                submit = st.form_submit_button("Send", use_container_width=True)
                
            if submit and q and q.strip():
                st.session_state.messages.append({"role": "user", "content": q.strip()})
                st.session_state.is_typing = True
                st.rerun()

        # Processing response in typing mode
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
                
                # Check if chart got created dynamically, inform user in chat to check main screen
                dynamic_chart_note = ""
                if resp.get("charts", {}).get("dynamic_chart"):
                    dynamic_chart_note = "\n\n*(I also generated a dynamic chart for you! Check the main dashboard.)*"
                
                report = (resp.get("structured_report") or "").strip()
                display_text = report + dynamic_chart_note
                st.session_state.messages.append({"role": "assistant", "content": display_text.replace("\n", "<br/>")})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Couldn't reach the backend: {str(e)}"})
            finally:
                st.session_state.is_typing = False
                st.rerun()
