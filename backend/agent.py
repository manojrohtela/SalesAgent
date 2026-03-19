import os
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from .analyzer import AnalysisResult, analyze_dataset
from .dataset_generator import generate_demo_dataset, load_or_generate_demo_dataset
from .tools import generate_structured_ai_response


app = FastAPI(title="AI Business Intelligence Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHARTS_DIR = os.path.join(os.path.dirname(__file__), "charts")
DEMO_CSV_PATH = os.path.join(DATA_DIR, "demo_dataset.csv")


class AnalysisResponse(BaseModel):
    structured_report: str
    charts: dict
    follow_up_questions: list


def _ensure_demo_dataset() -> pd.DataFrame:
    return load_or_generate_demo_dataset(DEMO_CSV_PATH)


def _read_uploaded_csv(uploaded_file: UploadFile) -> pd.DataFrame:
    """Read uploaded CSV with flexible column support - date parsing is optional."""
    content = uploaded_file.file.read()
    from io import StringIO

    s = StringIO(content.decode("utf-8"))
    df = pd.read_csv(s)
    
    # Normalize column names to make the application general
    df.columns = df.columns.astype(str).str.lower().str.strip()
    
    col_mapping = {
        'date': ['date', 'timestamp', 'day', 'time'],
        'revenue': ['revenue', 'sales', 'amount', 'total', 'price', 'value'],
        'units_sold': ['units_sold', 'units', 'quantity', 'qty', 'count'],
        'marketing_spend': ['marketing_spend', 'spend', 'cost', 'marketing', 'advertising'],
        'product': ['product', 'item', 'category', 'sku', 'name'],
        'region': ['region', 'country', 'city', 'location', 'state', 'market', 'territory'],
    }
    
    new_cols = {}
    for standard_col, aliases in col_mapping.items():
        for alias in aliases:
            matched = [c for c in df.columns if alias in c]
            if matched:
                new_cols[matched[0]] = standard_col
                break
                
    df = df.rename(columns=new_cols)
    
    # Fill in missing columns to prevent KeyError in analyzer
    if 'date' not in df.columns:
        df['date'] = pd.to_datetime('today')
    if 'revenue' not in df.columns:
        df['revenue'] = 0.0
    if 'units_sold' not in df.columns:
        df['units_sold'] = 0
    if 'marketing_spend' not in df.columns:
        df['marketing_spend'] = 0.0
    if 'product' not in df.columns:
        df['product'] = 'Unknown'
    if 'region' not in df.columns:
        df['region'] = 'Unknown'

    # Try to parse date column
    try:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    except Exception:
        pass  # If date parsing fails, leave as is
    
    return df

def _run_full_analysis(df: pd.DataFrame, user_question: Optional[str] = "") -> AnalysisResponse:
    result: AnalysisResult = analyze_dataset(df, charts_dir=CHARTS_DIR)
    
    # Get response with potential chart data
    structured_report, chart_obj = generate_structured_ai_response(
        df=df,
        dataset_summary=result.dataset_summary,
        stats_snapshot=result.stats_snapshot,
        user_question=user_question or "",
    )
    
    # If a dynamic chart was generated, add it to the charts
    charts = dict(result.charts)  # Copy existing charts
    if chart_obj:
        charts["dynamic_chart"] = chart_obj
    
    follow_up_questions = [
        "Would you like revenue prediction?",
        "Would you like a marketing strategy report?",
        "Would you like a downloadable report?",
    ]
    return AnalysisResponse(
        structured_report=structured_report,
        charts=charts,
        follow_up_questions=follow_up_questions,
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    use_demo: bool = True,
    question: Optional[str] = "",
    file: Optional[UploadFile] = File(default=None),
):
    """
    Main endpoint for autonomous analysis and Q&A.

    - If a CSV is uploaded, it is used.
    - Otherwise, a realistic demo dataset is generated or loaded.
    - The agent always returns a structured report, charts, and proactive follow-up questions.
    """
    if file is not None:
        df = _read_uploaded_csv(file)
    elif use_demo:
        df = _ensure_demo_dataset()
    else:
        df = generate_demo_dataset(save_path=DEMO_CSV_PATH)

    return _run_full_analysis(df, user_question=question or "")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.agent:app", host="0.0.0.0", port=8000, reload=True)

