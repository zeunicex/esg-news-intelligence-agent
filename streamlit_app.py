"""Streamlit dashboard for the ESG News Intelligence Agent."""

from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from esg_news_agent.export import articles_to_csv
from esg_news_agent.pipeline import analyze_articles
from esg_news_agent.sources import fetch_newsapi, load_csv

st.set_page_config(page_title="ESG News Intelligence", layout="wide")
st.title("ESG News Intelligence")
st.caption(
    "News-based ESG media signals for research; "
    "not an ESG rating or investment advice."
)

with st.sidebar:
    company = st.text_input("Company", "Northstar Industries")
    source = st.selectbox("Source", ("Sample data", "Upload CSV", "NewsAPI"))
    from_date = st.date_input("From", date.today() - timedelta(days=7))
    to_date = st.date_input("To", date.today())
    threshold = st.slider(
        "Duplicate similarity threshold",
        0.70,
        1.00,
        0.90,
        0.01,
    )
    uploaded = (
        st.file_uploader("CSV file", type="csv")
        if source == "Upload CSV"
        else None
    )
    run = st.button("Run analysis", type="primary", use_container_width=True)

if run:
    try:
        if source == "Sample data":
            articles = load_csv(ROOT / "examples" / "sample_news.csv")
        elif source == "NewsAPI":
            articles = fetch_newsapi(company, from_date, to_date)
        elif uploaded is None:
            st.warning("Choose a CSV file first.")
            st.stop()
        else:
            with tempfile.NamedTemporaryFile(suffix=".csv") as temp_file:
                temp_file.write(uploaded.getvalue())
                temp_file.flush()
                articles = load_csv(temp_file.name)

        result = analyze_articles(articles, duplicate_threshold=threshold)
        st.session_state["result"] = result
    except Exception as exc:
        st.error(str(exc))

result = st.session_state.get("result")
if result:
    counts = result["counts"]
    columns = st.columns(4)
    columns[0].metric("Collected", counts["collected"])
    columns[1].metric("Duplicates removed", counts["duplicates_removed"])
    columns[2].metric("ESG relevant", counts["esg_relevant"])
    columns[3].metric(
        "Overall signal",
        f'{result["overall"]["media_signal_score"]:.1f}',
    )

    overview, environmental, social, governance, articles_tab = st.tabs(
        ("Overview", "Environmental", "Social", "Governance", "Articles")
    )
    with overview:
        rows = [
            {"Pillar": pillar, **metrics}
            for pillar, metrics in result["pillars"].items()
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.info(result["methodology"]["score_note"])

    for tab, pillar in (
        (environmental, "Environmental"),
        (social, "Social"),
        (governance, "Governance"),
    ):
        with tab:
            st.metric(
                "Media signal",
                result["pillars"][pillar]["media_signal_score"],
            )
            st.dataframe(
                [
                    row
                    for row in result["articles"]
                    if pillar in row["pillars"]
                ],
                use_container_width=True,
                hide_index=True,
            )

    with articles_tab:
        st.dataframe(
            result["articles"],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download CSV",
            articles_to_csv(result),
            file_name="esg_news_analysis.csv",
            mime="text/csv",
        )
else:
    st.info("Choose a source and run the analysis.")
