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
    """Compute KPIs with flexible column support."""
    kpis = {}
    
    # Total revenue (look for numeric columns if revenue doesn't exist)
    if "revenue" in df.columns and pd.api.types.is_numeric_dtype(df["revenue"]):
        total_revenue = float(df["revenue"].sum())
        kpis["total_revenue"] = f"${total_revenue:,.0f}"
    else:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            total_val = float(df[numeric_cols[0]].sum())
            kpis["total_revenue"] = f"${total_val:,.0f}"
        else:
            kpis["total_revenue"] = "N/A"
    
    # Top product
    if "product" in df.columns and "revenue" in df.columns:
        by_product = df.groupby("product")["revenue"].sum().sort_values(ascending=False)
        kpis["top_product"] = str(by_product.index[0])
    else:
        kpis["top_product"] = "N/A"
    
    # Strongest region
    if "region" in df.columns and "revenue" in df.columns:
        by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
        kpis["strongest_region"] = str(by_region.index[0])
        kpis["weakest_region"] = str(by_region.index[-1])
    else:
        kpis["strongest_region"] = "N/A"
        kpis["weakest_region"] = "N/A"
    
    return kpis


def _trend_direction(df: pd.DataFrame) -> str:
    """Determine trend direction with flexible column support."""
    try:
        if "date" not in df.columns:
            return "N/A"
        
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if not numeric_cols:
            return "N/A"
        
        daily = df.groupby(df["date"].dt.date)[numeric_cols[0]].sum().reset_index(name="value")
        if len(daily) < 10:
            return "mixed"
        
        x = range(len(daily))
        # simple slope proxy: compare last 20% vs first 20%
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
        f"Top product: **{kpis['top_product']}**",
        f"Strongest region: **{kpis['strongest_region']}**",
        f"Weakest region: **{kpis['weakest_region']}**",
        f"Revenue trend: **{trend}**",
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
    <div class="metric-label">Total Revenue</div>
    <div class="metric-value" data-target="{kpis.get('total_revenue', 'N/A').replace('$', '').replace(',', '')}" data-prefix="$" id="kpi_total_revenue">$0</div>
    <div class="metric-sub">All regions • All products</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Top Product</div>
    <div class="metric-value">{kpis['top_product']}</div>
    <div class="metric-sub">Highest revenue driver</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Strongest Region</div>
    <div class="metric-value">{kpis['strongest_region']}</div>
    <div class="metric-sub">Best regional performance</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Weakest Region</div>
    <div class="metric-value">{kpis['weakest_region']}</div>
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

    main_col, chat_col = st.columns([3.2, 1.3], gap="large")
    with main_col:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("<div class='panel'><div class='panel-title'>Data Visualization 1</div></div>", unsafe_allow_html=True)
            if fig_trend is not None:
                st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this chart")
        with right:
            st.markdown("<div class='panel'><div class='panel-title'>Data Visualization 2</div></div>", unsafe_allow_html=True)
            if fig_product is not None:
                st.plotly_chart(fig_product, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No data available for this chart")

        st.markdown("<div class='panel'><div class='panel-title'>Data Visualization 3</div></div>", unsafe_allow_html=True)
        if fig_region is not None:
            st.plotly_chart(fig_region, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No data available for this chart")

        # Display dynamic chart if one was generated by AI query
        if analysis is not None and analysis.get("charts", {}).get("dynamic_chart"):
            try:
                dynamic_chart_data = analysis["charts"]["dynamic_chart"]
                
                # Check if it's a dict with "data" and "type" keys
                if isinstance(dynamic_chart_data, dict) and "data" in dynamic_chart_data:
                    chart_json = dynamic_chart_data["data"]
                elif isinstance(dynamic_chart_data, str):
                    # If it's already a JSON string, use it directly
                    chart_json = dynamic_chart_data
                else:
                    chart_json = None
                
                if chart_json:
                    # Parse the JSON and display
                    if isinstance(chart_json, str):
                        chart_json = json.loads(chart_json)
                    
                    st.markdown("<div class='panel'><div class='panel-title'>AI-Generated Chart</div></div>", unsafe_allow_html=True)
                    st.plotly_chart(chart_json, use_container_width=True, config={"displayModeBar": False})
            except Exception as e:
                st.warning(f"Could not render dynamic chart: {str(e)}")

        st.markdown("<div class='panel'><div class='panel-title'>Key Insights</div></div>", unsafe_allow_html=True)
        for b in bullets:
            st.markdown(f"- {b}")

        if analysis is not None:
            with st.expander("Full AI Analysis", expanded=False):
                st.markdown(analysis.get("structured_report", ""))
                if analysis.get("follow_up_questions"):
                    st.markdown("**Proactive follow-ups**")
                    for q in analysis.get("follow_up_questions", []):
                        st.markdown(f"- {q}")
        else:
            st.info("Run analysis to generate the AI report.")

    with chat_col:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='chat-title'>AI Analyst</div>", unsafe_allow_html=True)
        st.markdown("<div class='chat-sub'>Ask about the dataset. I'll answer concisely and reference what's in the charts.</div>", unsafe_allow_html=True)

        chat_area = st.container()
        with chat_area:
            for m in st.session_state.messages:
                cls = "bubble-user" if m["role"] == "user" else "bubble-ai"
                st.markdown(f"<div class='bubble {cls}'>{m['content']}</div>", unsafe_allow_html=True)

            if st.session_state.is_typing:
                st.markdown(
                    "<div class='typing'><div class='dot'></div><div class='dot'></div><div class='dot'></div></div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        q = st.chat_input(
            placeholder="Ask business questions about your data • Examples: Which product should we promote? Which region needs marketing? How can we increase sales?",
            key="chat_input",
        )

        if q and q.strip():
            st.session_state.messages.append({"role": "user", "content": q.strip()})
            st.session_state.is_typing = True
            st.rerun()

        # If we're in typing mode, fetch the assistant response in the next run.
        if st.session_state.is_typing:
            last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
            uploaded_bytes = uploaded.getvalue() if uploaded is not None else None
        # If we're in typing mode, fetch the assistant response in the next run.
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
                # For Q&A, use full response. For reports, truncate to first 12 lines.
                report = (resp.get("structured_report") or "").strip()
                if last_user.strip():
                    # User asked a specific question - use full answer
                    display_text = report
                else:
                    # No question - truncate full report for display
                    display_text = "\n".join(report.splitlines()[:12]).strip()
                st.session_state.messages.append({"role": "assistant", "content": display_text.replace("\n", "<br/>")})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"Couldn't reach the backend: {e}"})
            finally:
                st.session_state.is_typing = False
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

