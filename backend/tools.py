import os
from typing import Any, Dict, List, Optional, Protocol, Tuple
import logging
import re
import numpy as np
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class _LLM(Protocol):
    pass


def get_llm(
    model: Optional[str] = None,
    provider: Optional[str] = None,
) -> _LLM:
    """
    Construct a chat model via LangChain.

    Default behavior:
    - If GROQ_API_KEY is set: use Groq
    - Else: use OpenAI (OPENAI_API_KEY)
    """
    provider_env = (provider or os.environ.get("BI_AGENT_LLM_PROVIDER") or "").strip().lower()
    has_groq = bool(os.environ.get("GROQ_API_KEY"))

    if provider_env in {"groq"} or (provider_env == "" and has_groq):
        return ChatGroq(model=model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"), temperature=0.3)

    return ChatOpenAI(model=model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.3)


def _get_dataframe_schema(df: pd.DataFrame) -> str:
    """Get the schema of the dataframe as a string."""
    schema_lines = []
    schema_lines.append(f"Columns: {list(df.columns)}")
    schema_lines.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    schema_lines.append("Data types:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        schema_lines.append(f"  - {col}: {dtype}")
    
    # Sample unique values for categorical columns
    schema_lines.append("\nSample values:")
    for col in df.columns:
        if df[col].dtype == 'object' or df[col].nunique() < 20:
            unique_vals = df[col].unique()[:10]
            schema_lines.append(f"  - {col}: {list(unique_vals)}")
    
    return "\n".join(schema_lines)


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Auto-detect column types: numeric, categorical, datetime, or other.
    Helps handle flexible CSV datasets.
    """
    column_types = {}
    for col in df.columns:
        dtype = df[col].dtype
        if pd.api.types.is_datetime64_any_dtype(dtype):
            column_types[col] = "datetime"
        elif pd.api.types.is_numeric_dtype(dtype):
            column_types[col] = "numeric"
        elif pd.api.types.is_object_dtype(dtype) or pd.api.types.is_categorical_dtype(dtype):
            # Check if it looks numeric
            try:
                pd.to_numeric(df[col].dropna(), errors='coerce').notna().sum() / len(df[col].dropna()) > 0.8
                column_types[col] = "numeric"
            except:
                column_types[col] = "categorical"
        else:
            column_types[col] = "other"
    return column_types


def find_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Find all numeric columns in dataframe."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def find_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Find all categorical columns in dataframe."""
    return df.select_dtypes(include=['object']).columns.tolist()


def find_datetime_columns(df: pd.DataFrame) -> List[str]:
    """Find all datetime columns in dataframe."""
    return df.select_dtypes(include=['datetime64']).columns.tolist()


def generate_dynamic_chart(df: pd.DataFrame, question: str, chart_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Generate a Plotly chart dynamically based on user request.
    Returns dict with chart object (serializable) or None if unable to generate.
    
    Detects chart type from question and generates appropriate visualization.
    """
    try:
        q_lower = question.lower()
        numeric_cols = find_numeric_columns(df)
        categorical_cols = find_categorical_columns(df)
        datetime_cols = find_datetime_columns(df)
        
        if not numeric_cols:
            logger.warning("No numeric columns found for chart generation")
            return None
        
        # Infer chart type from question if not provided
        if not chart_type:
            if "pie" in q_lower:
                chart_type = "pie"
            elif "bar" in q_lower:
                chart_type = "bar"
            elif "trend" in q_lower or "line" in q_lower or "over time" in q_lower:
                chart_type = "line"
            elif "scatter" in q_lower:
                chart_type = "scatter"
            elif "box" in q_lower or "distribution" in q_lower:
                chart_type = "box"
            else:
                # Default: bar chart for categorical + numeric
                chart_type = "bar"
        
        # Generate appropriate chart
        chart_obj = None
        
        if chart_type == "pie" and categorical_cols and numeric_cols:
            # Pie chart: categorical dimension with numeric value
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            if "revenue" in q_lower or "sales" in q_lower:
                num_col = next((c for c in numeric_cols if "revenue" in c.lower()), numeric_cols[0])
            grouped = df.groupby(cat_col)[num_col].sum()
            chart_obj = {
                "type": "pie",
                "data": px.pie(
                    values=grouped.values,
                    names=grouped.index,
                    title=f"{num_col.title()} by {cat_col.title()}"
                ).to_json()
            }
        
        elif chart_type == "bar" and categorical_cols and numeric_cols:
            # Bar chart
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            if "revenue" in q_lower or "sales" in q_lower:
                num_col = next((c for c in numeric_cols if "revenue" in c.lower()), numeric_cols[0])
            grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
            chart_obj = {
                "type": "bar",
                "data": px.bar(
                    x=grouped.index,
                    y=grouped.values,
                    title=f"{num_col.title()} by {cat_col.title()}",
                    labels={"x": cat_col.title(), "y": num_col.title()}
                ).to_json()
            }
        
        elif chart_type == "line" and (datetime_cols or categorical_cols) and numeric_cols:
            # Line chart (trend)
            num_col = numeric_cols[0]
            if "revenue" in q_lower or "sales" in q_lower:
                num_col = next((c for c in numeric_cols if "revenue" in c.lower()), numeric_cols[0])
            
            if datetime_cols:
                time_col = datetime_cols[0]
                df_sorted = df.sort_values(time_col)
                chart_obj = {
                    "type": "line",
                    "data": px.line(
                        df_sorted,
                        x=time_col,
                        y=num_col,
                        title=f"{num_col.title()} Trend"
                    ).to_json()
                }
            else:
                # Use categorical as x-axis
                cat_col = categorical_cols[0] if categorical_cols else df.columns[0]
                chart_obj = {
                    "type": "line",
                    "data": px.line(
                        df,
                        x=cat_col,
                        y=num_col,
                        title=f"{num_col.title()} Trend"
                    ).to_json()
                }
        
        elif chart_type == "scatter" and len(numeric_cols) >= 2:
            # Scatter plot
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            color_col = categorical_cols[0] if categorical_cols else None
            chart_obj = {
                "type": "scatter",
                "data": px.scatter(
                    df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col.title()} vs {x_col.title()}"
                ).to_json()
            }
        
        elif chart_type == "box" and numeric_cols and categorical_cols:
            # Box plot (distribution)
            num_col = numeric_cols[0]
            cat_col = categorical_cols[0]
            chart_obj = {
                "type": "box",
                "data": px.box(
                    df,
                    x=cat_col,
                    y=num_col,
                    title=f"Distribution of {num_col.title()} by {cat_col.title()}"
                ).to_json()
            }
        
        if chart_obj:
            logger.info(f"Generated {chart_type} chart for question: {question}")
            return chart_obj
        else:
            logger.warning(f"Could not generate {chart_type} chart for: {question}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return None


def generate_pandas_query(df: pd.DataFrame, question: str) -> Optional[str]:
    """
    Use LLM to generate a pandas query that answers the question.
    Returns only the pandas expression code.
    
    Handles flexible CSV datasets by auto-detecting column types.
    """
    schema = _get_dataframe_schema(df)
    column_types = detect_column_types(df)
    
    # Add column type information to schema
    column_type_info = "\nColumn Classifications:\n"
    for col, col_type in column_types.items():
        column_type_info += f"  - {col}: {col_type}\n"
    
    full_schema = schema + column_type_info
    
    template = """You are a Python data analyst expert.

Your task is to write a pandas expression that answers the user's question about a dataset.

DataFrame information:
{schema}

User question: {question}

INSTRUCTIONS:
1. Generate ONLY a valid pandas expression
2. The dataframe is named "df"
3. Return ONLY the pandas code, nothing else
4. Do NOT include explanation or markdown formatting
5. Do NOT wrap in code blocks
6. Make sure the expression is executable Python code
7. Handle date comparisons if needed
8. For categorical filtering, use exact string matches
9. For numeric operations, use appropriate aggregation functions

Examples:
- For "total revenue": df["revenue"].sum()
- For "revenue by region": df.groupby("region")["revenue"].sum()
- For "top 3 products": df.groupby("product")["revenue"].sum().nlargest(3)
- For "average spend in Europe": df[df["region"]=="Europe"]["marketing_spend"].mean()
- For "revenue in December 2025": df[(df["date"].dt.month==12)&(df["date"].dt.year==2025)]["revenue"].sum()

Generate the pandas expression now:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    chain = prompt | llm
    
    try:
        msg = chain.invoke({
            "schema": full_schema,
            "question": question,
        })
        code = getattr(msg, "content", str(msg)).strip()
        logger.info(f"Generated pandas query for '{question}': {code}")
        return code
    except Exception as e:
        logger.error(f"Failed to generate pandas query: {e}")
        return None


def execute_pandas_query(df: pd.DataFrame, code: str) -> Tuple[bool, Any, str]:
    """
    Safely execute a pandas query and return the result.
    Returns (success: bool, result: Any, error_message: str)
    """
    try:
        # Create a safe namespace with only df
        namespace = {"df": df, "pd": pd}
        
        # Execute the query
        result = eval(code, {"__builtins__": {}}, namespace)
        
        logger.info(f"Query execution successful. Result type: {type(result).__name__}")
        return True, result, ""
    except Exception as e:
        error_msg = f"Query execution failed: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def _format_query_result(result: Any, question: str) -> str:
    """
    Convert a pandas query result into a human-readable response.
    """
    # Handle single numeric values
    if isinstance(result, (int, float, np.integer, np.floating)):
        # Try to infer what was asked about
        q_lower = question.lower()
        
        # Format currency
        if "revenue" in q_lower or "sales" in q_lower or "spend" in q_lower:
            formatted = f"${result:,.0f}"
        else:
            formatted = f"{result:,.2f}".rstrip('0').rstrip('.')
        
        # Generate response based on question keywords
        if "total" in q_lower:
            return f"Total: {formatted}"
        elif "average" in q_lower or "avg" in q_lower or "mean" in q_lower:
            return f"Average: {formatted}"
        elif "count" in q_lower or "number" in q_lower:
            return f"Count: {int(result)}"
        else:
            return f"Result: {formatted}"
    
    # Handle Series (grouped results)
    elif isinstance(result, pd.Series):
        lines = []
        for idx, val in result.items():
            if isinstance(val, (int, float, np.integer, np.floating)):
                if "revenue" in question.lower() or "sales" in question.lower():
                    formatted = f"${val:,.0f}"
                else:
                    formatted = f"{val:,.2f}".rstrip('0').rstrip('.')
                lines.append(f"{idx}: {formatted}")
            else:
                lines.append(f"{idx}: {val}")
        return ", ".join(lines)
    
    # Handle DataFrame
    elif isinstance(result, pd.DataFrame):
        if len(result) == 0:
            return "No data found."
        
        # Format as readable table
        lines = []
        for idx, row in result.iterrows():
            row_str = " | ".join([f"{col}: {val}" for col, val in row.items()])
            lines.append(row_str)
        return "\n".join(lines[:10])  # Limit to first 10 rows
    
    # Handle list or array
    elif isinstance(result, (list, tuple)):
        if len(result) == 0:
            return "No results."
        formatted_items = []
        for item in result[:10]:  # Limit to 10 items
            if isinstance(item, (int, float)):
                formatted_items.append(f"{item:,.2f}".rstrip('0').rstrip('.'))
            else:
                formatted_items.append(str(item))
        return ", ".join(formatted_items)
    
    # Default
    else:
        return str(result)


def _answer_data_question(df: pd.DataFrame, question: str, stats: Dict[str, Any]) -> Optional[str]:
    """
    Answer a data question by generating and executing a pandas query dynamically.
    Uses LLM to generate the pandas code instead of hardcoded rules.
    """
    # Ensure date column is datetime if it exists
    if 'date' in df.columns:
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    logger.info(f"Processing data question: '{question}'")
    
    # Generate pandas query using LLM
    pandas_code = generate_pandas_query(df, question)
    
    if not pandas_code:
        logger.warning(f"Failed to generate pandas query for: {question}")
        return None
    
    # Execute the query
    success, result, error_msg = execute_pandas_query(df, pandas_code)
    
    if not success:
        logger.error(f"Query execution failed: {error_msg}")
        return None
    
    # Format the result into a readable response
    response = _format_query_result(result, question)
    logger.info(f"Final response: {response}")
    
    return response


def build_insight_chain():
    """
    Construct a chain that takes structured stats plus an optional user question
    and returns a business-friendly, well-structured analysis.
    """
    template = """
You are a senior business intelligence analyst.

CRITICAL INSTRUCTION: If a user question is provided and is NOT empty, you MUST answer ONLY that question directly and concisely in 1-3 sentences using the stats provided. Do NOT provide any report structure. Do NOT include DATASET SUMMARY, KEY INSIGHTS, or any other sections. Just answer the question.

If NO user question is provided (empty string), then write a concise but insightful report with these exact section headings:

DATASET SUMMARY
<2-4 sentences summarizing the dataset, volume, and overall performance.>

KEY INSIGHTS
<Bulleted list of the most important insights about products, regions, trends, and anomalies.>

VISUAL ANALYSIS
<Bulleted list explaining what a revenue trend chart, product performance chart, and region comparison chart reveal.>

BUSINESS RECOMMENDATIONS
<Bulleted list of specific, actionable recommendations to improve revenue or efficiency.>

ACTION PLAN
<Numbered list of next actions over the next 30 days.>

---

Dataset summary:
{dataset_summary}

Stats snapshot:
{stats_snapshot}

User question (may be empty): {user_question}

Remember: If user_question is not empty, answer ONLY the question in 1-3 sentences. No report structure.
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    return prompt | llm


def _classify_question(question: str) -> str:
    """Classify the question into DATA, BUSINESS_ANALYSIS, GENERAL, or CHART."""
    q_lower = question.lower()
    
    # Check for chart requests FIRST
    chart_keywords = ['chart', 'plot', 'graph', 'visualize', 'show this in', 'pie chart', 'bar chart', 'line chart', 'scatter', 'display']
    if any(keyword in q_lower for keyword in chart_keywords):
        return "CHART"
    
    # Keywords indicating business analysis - check BEFORE data keywords
    # (because "increase sales" should be BUSINESS_ANALYSIS, not DATA)
    analysis_keywords = [
        'should we', 'should i', 'recommend', 'promote', 'strategy', 'investment', 'priority',
        'which product should', 'where should', 'how to increase', 'needs attention',
        'optimize', 'boost revenue', 'boost sales', 'grow sales', 'grow the',
        'what should', 'why should', 'how can we', 'advice', 'best way',
        'improve sales', 'improve revenue', 'increase sales', 'increase revenue',
        'expand to', 'focus on', 'consider', 'think about'
    ]
    has_analysis_keywords = any(keyword in q_lower for keyword in analysis_keywords)
    
    if has_analysis_keywords:
        return "BUSINESS_ANALYSIS"
    
    # Data columns that indicate direct data queries - check AFTER analysis keywords
    data_keywords = {
        'date', 'product', 'region', 'revenue', 'units_sold', 'marketing_spend',
        'total', 'average', 'sum', 'count', 'max', 'min', 'highest', 'lowest',
        'how many', 'what is the', 'show me', 'list', 'top', 'bottom',
        'units', 'spend'
    }
    references_columns = any(col in q_lower for col in data_keywords)
    
    # If references data columns/keywords, likely DATA
    if references_columns:
        return "DATA"
    
    # Otherwise, GENERAL
    return "GENERAL"


def build_business_analysis_chain():
    """Chain for business analysis questions requiring recommendations."""
    template = """
You are a senior business intelligence analyst providing strategic recommendations.

Based on the following dataset insights, answer the user's business question with specific, actionable recommendations.

Dataset Insights:
{insights}

User Question: {user_question}

IMPORTANT: Answer the specific question asked. Provide structured response with:

Answer
<Direct answer to the question based on data insights>

Key Reasoning  
<Bullet points explaining the analysis and data supporting your answer>

Recommendation
<Specific, actionable business recommendations based on the data>

Keep the response concise, focused on the data, and business-value driven.
Be direct and answer what the user asked.
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    return prompt | llm


def build_general_business_chain():
    """Chain for general business questions (including hybrid data+strategy questions)."""
    template = """
You are a versatile business intelligence analyst and strategic advisor.

You have access to dataset insights and can provide both data-driven answers and strategic business advice.

Dataset Insights (use if relevant):
{insights}

User Question: {user_question}

IMPORTANT: 
- If the question asks about the data, analyze the insights provided and answer directly
- If the question is strategic/business advice, provide professional guidance
- Always be specific and use the data when applicable
- If you cannot answer based on the data, say so explicitly

Provide a structured response with:

Answer
<Direct answer to the question>

Analysis/Reasoning
<Bullet points with data evidence or business logic>

Recommendations (if applicable)
<Specific, actionable next steps>

Keep the response professional, direct, and actionable.
"""
    prompt = ChatPromptTemplate.from_template(template)
    llm = get_llm()
    return prompt | llm


def _get_key_insights(df: pd.DataFrame, stats: Dict[str, Any]) -> str:
    """
    Extract comprehensive key insights from dataframe and stats for business analysis.
    Works with flexible CSV datasets.
    """
    insights = []
    
    # Pre-computed stats
    if 'top_product' in stats:
        insights.append(f"Top product: {stats['top_product']}")
    if 'weakest_product' in stats:
        insights.append(f"Weakest product: {stats['weakest_product']}")
    if 'strongest_region' in stats:
        insights.append(f"Strongest region: {stats['strongest_region']}")
    if 'weakest_region' in stats:
        insights.append(f"Weakest region: {stats['weakest_region']}")
    
    if df is not None and len(df) > 0:
        # Auto-detect numeric columns for flexible CSV support
        numeric_cols = find_numeric_columns(df)
        categorical_cols = find_categorical_columns(df)
        
        # Get revenue or first numeric column
        metric_col = next((c for c in numeric_cols if 'revenue' in c.lower()), numeric_cols[0] if numeric_cols else None)
        
        if metric_col and categorical_cols:
            # Revenue/metric by first categorical dimension
            primary_cat = categorical_cols[0]
            try:
                cat_breakdown = df.groupby(primary_cat)[metric_col].sum().sort_values(ascending=False)
                insights.append(f"{metric_col.title()} by {primary_cat.title()}: {', '.join([f'{c}: ${v:,.0f}' if metric_col.lower() in ['revenue', 'sales', 'spend'] else f'{c}: {v:,.0f}' for c, v in cat_breakdown.head(5).items()])}")
            except:
                pass
        
        # If there's a second categorical column
        if len(categorical_cols) > 1 and metric_col:
            secondary_cat = categorical_cols[1]
            try:
                cat_breakdown_2 = df.groupby(secondary_cat)[metric_col].sum().sort_values(ascending=False)
                insights.append(f"{metric_col.title()} by {secondary_cat.title()}: {', '.join([f'{c}: ${v:,.0f}' if metric_col.lower() in ['revenue', 'sales', 'spend'] else f'{c}: {v:,.0f}' for c, v in cat_breakdown_2.head(5).items()])}")
            except:
                pass
        
        # Total metric
        if metric_col:
            try:
                total_metric = df[metric_col].sum()
                insights.append(f"Total {metric_col.lower()}: ${total_metric:,.0f}" if metric_col.lower() in ['revenue', 'sales', 'spend'] else f"Total {metric_col.lower()}: {total_metric:,.0f}")
            except:
                pass
        
        # Row count and date range
        insights.append(f"Dataset size: {len(df)} records")
        datetime_cols = find_datetime_columns(df)
        if datetime_cols:
            try:
                date_col = datetime_cols[0]
                min_date = df[date_col].min()
                max_date = df[date_col].max()
                insights.append(f"Date range: {min_date.date()} to {max_date.date()}")
            except:
                pass
    
    return "\n".join(insights)


def generate_structured_ai_response(
    df: Optional[pd.DataFrame] = None,
    dataset_summary: str = "",
    stats_snapshot: Dict[str, Any] = None,
    user_question: Optional[str] = "",
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Intelligent business analyst that handles data queries, business analysis, general business questions, and chart generation.
    Returns (text_response, chart_object_or_none)
    
    Features:
    - Chart generation for "show this in chart" requests
    - Dynamic pandas queries for data questions
    - Business analysis with recommendations
    - General business advice
    - Comprehensive fallback mechanisms for safety
    """
    if stats_snapshot is None:
        stats_snapshot = {}
    
    question = (user_question or "").strip()
    
    # Classify the question
    question_type = _classify_question(question) if question else "NONE"
    
    # Get key insights for context
    key_insights = _get_key_insights(df, stats_snapshot)
    
    # Handle chart requests
    if question_type == "CHART":
        try:
            if df is not None:
                chart_obj = generate_dynamic_chart(df, question)
                if chart_obj:
                    response_text = f"I've created a chart for your query: {question}"
                    logger.info(f"Chart generated for question: {question}")
                    return response_text, chart_obj
        except Exception as e:
            logger.warning(f"Chart generation failed (will fallback): {e}")
        
        # Fallback if chart generation fails - return data analysis instead
        if df is not None:
            try:
                data_answer = _answer_data_question(df, question, stats_snapshot)
                if data_answer:
                    return f"Chart generation encountered an issue. Here's the data instead:\n{data_answer}", None
            except:
                pass
        
        return "I couldn't generate a chart for that request. Try asking for a pie chart, bar chart, or line chart with specific data.", None
    
    # No question - return full report
    if not question:
        try:
            report = _generate_full_report(dataset_summary, stats_snapshot)
            return report, None
        except Exception as e:
            logger.warning(f"Full report generation failed: {e}")
            return "Unable to generate full report. Please ask specific questions about the data.", None
    
    if question_type == "DATA":
        # Direct data queries
        if df is not None:
            try:
                data_answer = _answer_data_question(df, question, stats_snapshot)
                if data_answer:
                    return data_answer, None
            except Exception as e:
                logger.warning(f"Data question failed: {e}")
        
        # Fallback: try business analysis on the same question
        try:
            chain = build_general_business_chain()
            msg = chain.invoke({
                "insights": key_insights,
                "user_question": question,
            })
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                return f"[Data analysis fallback] {content.strip()}", None
        except Exception as e:
            logger.warning(f"Data fallback also failed: {e}")
        
        return f"I couldn't directly query the data. Based on available insights:\n{key_insights}", None
    

    elif question_type == "BUSINESS_ANALYSIS":
        # Business analysis requiring recommendations
        try:
            chain = build_business_analysis_chain()
            msg = chain.invoke({
                "insights": key_insights,
                "user_question": question,
            })
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                return content.strip(), None
        except Exception as e:
            logger.warning(f"Business analysis LLM failed: {e}")
        
        # Fallback: return summary insights with question context
        fallback_response = f"Based on the data analysis:\n\n{key_insights}\n\nFor more specific recommendations on '{question}', please rephrase your question more clearly."
        return fallback_response, None
    
    else:  # GENERAL
        # General business questions - with comprehensive error handling
        try:
            chain = build_general_business_chain()
            msg = chain.invoke({
                "insights": key_insights,
                "user_question": question,
            })
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                return content.strip(), None
        except Exception as e:
            logger.warning(f"General business LLM failed: {e}")
        
        # Multi-level fallback for general questions
        try:
            # Try as business analysis
            chain = build_business_analysis_chain()
            msg = chain.invoke({
                "insights": key_insights,
                "user_question": question,
            })
            content = getattr(msg, "content", None)
            if isinstance(content, str):
                return content.strip(), None
        except:
            pass
        
        # Final fallback: use insights
        return f"General query: {question}\n\nAvailable insights:\n{key_insights}", None


def generate_structured_ai_response_legacy(
    df: Optional[pd.DataFrame] = None,
    dataset_summary: str = "",
    stats_snapshot: Dict[str, Any] = None,
    user_question: Optional[str] = "",
) -> str:
    """
    Legacy wrapper for backward compatibility.
    Returns only the text response (ignores chart data).
    """
    text_response, _ = generate_structured_ai_response(
        df=df,
        dataset_summary=dataset_summary,
        stats_snapshot=stats_snapshot,
        user_question=user_question,
    )
    return text_response


def _generate_full_report(dataset_summary: str, stats_snapshot: Dict[str, Any]) -> str:
    """Generate the full business intelligence report when no specific question is asked."""
    stats_str_parts: List[str] = []
    for k, v in stats_snapshot.items():
        stats_str_parts.append(f"{k}: {v}")
    stats_str = "\n".join(stats_str_parts)

    try:
        chain = build_insight_chain()
        msg = chain.invoke({
            "dataset_summary": dataset_summary,
            "stats_snapshot": stats_str,
            "user_question": "",
        })
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content.strip()
    except Exception as e:
        logger.warning(f"Full report LLM failed: {e}")
    
    # Fallback deterministic report
    top_product = stats_snapshot.get("top_product", "N/A")
    weakest_product = stats_snapshot.get("weakest_product", "N/A")
    strongest_region = stats_snapshot.get("strongest_region", "N/A")
    weakest_region = stats_snapshot.get("weakest_region", "N/A")
    trend_summary = stats_snapshot.get("trend_summary", "")
    anomaly_summary = stats_snapshot.get("anomaly_summary", "")

    return "\n".join([
        "DATASET SUMMARY",
        dataset_summary,
        "",
        "KEY INSIGHTS",
        f"- Top product: {top_product}",
        f"- Weakest product: {weakest_product}",
        f"- Strongest region: {strongest_region}",
        f"- Weakest region: {weakest_region}",
        f"- Trend: {trend_summary}".strip(),
        f"- Anomalies: {anomaly_summary}".strip(),
        "",
        "VISUAL ANALYSIS",
        "- Revenue trend chart: highlights overall direction and volatility over time.",
        "- Product performance chart: shows which products drive most revenue.",
        "- Region comparison chart: reveals regional strengths and weak spots.",
        "",
        "BUSINESS RECOMMENDATIONS",
        "- Reallocate budget toward high-performing product/region combinations while testing messaging in weaker regions.",
        "- Create targeted campaigns for the weakest region and validate pricing/positioning assumptions.",
        "- Increase weekend-focused promotions if weekend uplift is present.",
        "",
        "ACTION PLAN",
        "1. Review region + product performance; shift 10–15% spend to highest ROI areas.",
        "2. Launch 2–3 A/B tests on offers and channels in the weakest region.",
        "3. Monitor weekly trends and anomalies; operationalize learnings into a monthly playbook.",
    ]).strip()

