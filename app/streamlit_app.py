import streamlit as st
from urllib.parse import urlparse
import plotly.graph_objects as go
import plotly.express as px

from utils.scoring_engine import dataset_score, live_news_score
from utils.url_extractor import extract_article


st.set_page_config(
    page_title="Hybrid News Credibility Analyzer",
    layout="wide"
)

st.title("Hybrid News Credibility Analyzer")

st.write(
    "Analyze credibility of news articles using machine learning, semantic analysis, and fact-check verification."
)


# -------------------------------------------------
# Gauge Meter
# -------------------------------------------------

def gauge_chart(score):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Credibility Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},

            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "green"}
            ],
        }
    ))

    fig.update_layout(height=350)

    return fig


# -------------------------------------------------
# Session State
# -------------------------------------------------

if "article_text" not in st.session_state:
    st.session_state.article_text = ""

if "article_url" not in st.session_state:
    st.session_state.article_url = ""

if "article_title" not in st.session_state:
    st.session_state.article_title = ""

if "authors" not in st.session_state:
    st.session_state.authors = None

if "publish_date" not in st.session_state:
    st.session_state.publish_date = None


# -------------------------------------------------
# Input Mode
# -------------------------------------------------

mode = st.radio(
    "Choose Input Type",
    ("Paste News Text", "Enter News URL (Live News)")
)

# =========================================================
# TEXT MODE
# =========================================================

if mode == "Paste News Text":

    text = st.text_area(
        "Paste News Article Text",
        height=250
    )

    if st.button("Analyze Credibility"):

        if text.strip() == "":
            st.warning("Please paste article text first.")

        else:

            result = dataset_score(text)

            st.subheader("Credibility Dashboard")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("ML Score", result["ML Score"])
                st.metric("BERT Score", result["BERT Score"])
                st.metric("Final Hybrid Score", result["Final Hybrid Score"])

                # Progress bar
                st.write("Credibility Strength")
                st.progress(int(result["Final Hybrid Score"]))

            with col2:
                fig = gauge_chart(result["Final Hybrid Score"])
                st.plotly_chart(fig, use_container_width=True)

            # -------------------------------
            # Charts Section
            # -------------------------------

            scores = {
                "ML Score": result["ML Score"],
                "BERT Score": result["BERT Score"]
            }

            st.subheader("Model Score Visualization")

            col3, col4 = st.columns(2)

            # Bar Chart
            bar_fig = px.bar(
                x=list(scores.keys()),
                y=list(scores.values()),
                labels={'x': 'Model', 'y': 'Score'},
                title="Model Prediction Scores",
                color=list(scores.values()),
                color_continuous_scale="viridis"
            )

            with col3:
                st.plotly_chart(bar_fig, use_container_width=True)

            # Pie Chart
            pie_fig = px.pie(
                values=list(scores.values()),
                names=list(scores.keys()),
                title="Model Contribution"
            )

            pie_fig.update_traces(textinfo="percent+label")

            with col4:
                st.plotly_chart(pie_fig, use_container_width=True)

            # Credibility Level

            st.metric("Credibility Level", result["Credibility Level"])

            if result["Credibility Level"] == "HIGH":
                st.success("Highly Credible Article")

            elif result["Credibility Level"] == "MEDIUM":
                st.warning("Moderately Credible Article")

            else:
                st.error("Low Credibility / Possible Fake News")

            st.subheader("Explanation")
            st.write(result["Explanation"])

# =========================================================
# URL MODE
# =========================================================

elif mode == "Enter News URL (Live News)":

    url = st.text_input("Enter News Article URL")

    if st.button("Fetch Article"):

        title, article_text, authors, publish_date = extract_article(url)

        if article_text:

            st.session_state.article_text = article_text
            st.session_state.article_url = url
            st.session_state.article_title = title
            st.session_state.authors = authors
            st.session_state.publish_date = publish_date

            st.success("Article extracted successfully.")

        else:
            st.error("Unable to extract article.")


    if st.session_state.article_text != "":

        st.subheader("Article Title")
        st.write(st.session_state.article_title)

        domain = urlparse(st.session_state.article_url).netloc
        st.write("Source:", domain)

        if st.session_state.authors:
            st.write("Author:", ", ".join(st.session_state.authors))

        if st.session_state.publish_date:
            st.write("Published on:", st.session_state.publish_date)

        st.subheader("Article Preview")

        preview = st.session_state.article_text[:800]
        st.write(preview + "...")



    if st.button("Analyze Credibility"):

        if st.session_state.article_text == "":
            st.warning("Please fetch article first.")

        else:

            result = live_news_score(
                st.session_state.article_text,
                st.session_state.article_url
            )

            st.subheader("Credibility Dashboard")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Source Score", result["Source Score"])
                st.metric("Writing Quality Score", result["Writing Quality Score"])
                st.metric("Fact Check Score", result["Fact Check Score"])
                st.metric("Final Score", result["Final Score"])

                # Progress bar
                st.write("Credibility Strength")
                st.progress(int(result["Final Score"]))

            with col2:
                fig = gauge_chart(result["Final Score"])
                st.plotly_chart(fig, use_container_width=True)


            # -------------------------------
            # Charts Section
            # -------------------------------

            scores = {
                "Source": result["Source Score"],
                "Writing Quality": result["Writing Quality Score"],
                "Fact Check": result["Fact Check Score"]
            }

            st.subheader("Credibility Score Visualization")

            col3, col4 = st.columns(2)

            bar_fig = px.bar(
                x=list(scores.keys()),
                y=list(scores.values()),
                labels={'x': 'Factor', 'y': 'Score'},
                title="Credibility Factors",
                color=list(scores.values()),
                color_continuous_scale="viridis"
            )

            with col3:
                st.plotly_chart(bar_fig, use_container_width=True)

            pie_fig = px.pie(
                values=list(scores.values()),
                names=list(scores.keys()),
                title="Score Distribution"
            )

            pie_fig.update_traces(textinfo="percent+label")

            with col4:
                st.plotly_chart(pie_fig, use_container_width=True)


            # Credibility Level

            st.metric("Credibility Level", result["Credibility Level"])

            if result["Credibility Level"] == "HIGH":
                st.success("Highly Credible News Source")

            elif result["Credibility Level"] == "MEDIUM":
                st.warning("Moderate Credibility - Needs Verification")

            else:
                st.error("Low Credibility - Possible Misinformation")

            st.subheader("Explanation")
            st.write(result["Explanation"])
