## AI Business Intelligence Agent

End-to-end demo-ready AI BI agent that can:

- **Ingest CSV datasets** (or auto-generate a realistic demo dataset)
- **Analyze performance** across products and regions with pandas
- **Generate charts** (matplotlib) for trends, products, and regions
- **Answer natural language questions** via LangChain + Groq (or OpenAI fallback)
- **Produce a structured business report** with clear sections:
  - DATASET SUMMARY
  - KEY INSIGHTS
  - VISUAL ANALYSIS
  - BUSINESS RECOMMENDATIONS
  - ACTION PLAN

Frontend is built with **Streamlit** and backend with **FastAPI**.

---

## Project Structure

- `backend/`
  - `dataset_generator.py` – synthetic demo dataset generator with business rules
  - `analyzer.py` – pandas-based analysis + matplotlib charts
  - `tools.py` – LangChain + Groq helpers to create structured narratives (OpenAI fallback)
  - `agent.py` – FastAPI app exposing the analysis API
- `frontend/`
  - `app.py` – Streamlit UI (upload, auto-analysis, chat-style questions, charts)
- `data/`
  - `demo_dataset.csv` – sample generated dataset (full demo dataset can be regenerated)
- `requirements.txt` – Python dependencies

---

## Features

- **CSV upload**
  - Upload a CSV with columns: `date, product, region, revenue, units_sold, marketing_spend`.

- **Automatic demo dataset**
  - If no file is uploaded, the backend automatically generates a **synthetic 500-row dataset** with:
    - Products: Phone, Laptop, Tablet, Headphones, Smartwatch
    - Regions: India, US, Europe, Middle East, Asia
    - Revenue between 1,000 and 50,000
    - Marketing spend that positively influences revenue
    - Phones generally selling more
    - Europe slightly weaker revenue
    - Weekend sales slightly higher

- **Data analysis**
  - Top performing products and weakest regions
  - Revenue trends over time
  - Anomaly detection on daily revenue

- **Visualizations**
  - Revenue trend chart
  - Product performance chart
  - Region comparison chart

- **AI insights & Q&A**
  - Natural language questions like:
    - “What insights can you find?”
    - “Which product performs best?”
    - “Which region has declining revenue?”
    - “What recommendations would increase revenue?”
  - AI response is always structured into the 5 required sections.

- **Autonomous & proactive**
  - As soon as a dataset is uploaded or generated, the agent:
    - Runs analysis automatically
    - Produces insights
    - Suggests follow-up questions:
      - “Would you like revenue prediction?”
      - “Would you like a marketing strategy report?”
      - “Would you like a downloadable report?”

---

## Prerequisites

- Python 3.9+
- Groq API key (recommended) or OpenAI API key (fallback)

Set your key as an environment variable (Groq):

```bash
export GROQ_API_KEY="gsk_..."
```

Optional model selection:

```bash
export GROQ_MODEL="llama3-70b-8192"
```

Fallback (OpenAI):

```bash
export OPENAI_API_KEY="sk-..."
```

Optionally, configure the backend URL for the Streamlit app (defaults to `http://localhost:8000`):

```bash
export BI_AGENT_BACKEND_URL="https://your-backend-url.onrender.com"
```

---

## Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

---

## Running Locally

### 1. Start the FastAPI backend

From the project root:

```bash
uvicorn backend.agent:app --host 0.0.0.0 --port 8000 --reload
```

The backend exposes:

- `GET /health` – health check
- `POST /analyze` – main AI BI endpoint

### 2. Start the Streamlit frontend

In a second terminal, from the project root:

```bash
streamlit run frontend/app.py
```

Open the URL shown by Streamlit (usually `http://localhost:8501`).

---

## Using the App

1. **Open the Streamlit UI.**
2. On the sidebar:
   - (Optional) **Upload a CSV** matching the expected schema.
   - If you skip upload, the app uses the **auto-generated demo dataset**.
3. Click **Run Analysis** (or rely on auto-run on first load).
4. Explore:
   - **Structured AI Analysis** with the five required sections.
   - **Follow-up questions** suggested by the agent.
   - **Charts** showing trends, products, and regions.
5. Ask natural language questions in the **Ask a Question** panel.

---

## Regenerating the Demo Dataset

To regenerate a fresh 500-row demo dataset:

```bash
python -m backend.dataset_generator
```

This will overwrite `data/demo_dataset.csv` with a new synthetic dataset that respects all business rules.

---

## Deploying on Render

You’ll typically deploy the **FastAPI backend** on Render and run the **Streamlit frontend** either locally or in a separate service.

### 1. Backend (FastAPI) on Render

1. Push this project to GitHub.
2. On Render, create a new **Web Service**:
   - Connect your GitHub repo.
   - Choose the main branch.
3. Set the **Build Command**:

   ```bash
   pip install -r requirements.txt
   ```

4. Set the **Start Command**:

   ```bash
   uvicorn backend.agent:app --host 0.0.0.0 --port 10000
   ```

5. Set environment variables in Render:
   - `GROQ_API_KEY` – your Groq key (recommended), or `OPENAI_API_KEY` for fallback.
6. Deploy. Render will give you a URL like `https://your-app.onrender.com`.

### 2. Frontend (Streamlit)

For a simple demo flow, run Streamlit locally and point it to the Render backend:

1. On your local machine:

   ```bash
   export BI_AGENT_BACKEND_URL="https://your-app.onrender.com"
   streamlit run frontend/app.py
   ```

2. Open the local Streamlit URL and the app will call the backend hosted on Render.

You can also containerize and deploy Streamlit as a separate Render service using a similar pattern (install requirements + `streamlit run frontend/app.py`), but for many client demos, keeping Streamlit local and the API remote is sufficient.

---

## Notes for Client Demos

- The app automatically falls back to a **realistic synthetic dataset** if no CSV is uploaded, so you always have something compelling to show.
- The **structured AI response** is stable and easy to talk through:
  - DATASET SUMMARY
  - KEY INSIGHTS
  - VISUAL ANALYSIS
  - BUSINESS RECOMMENDATIONS
  - ACTION PLAN
- The **follow-up questions** give you an easy segue into deeper capabilities (prediction, marketing strategy, reporting) in future iterations.

