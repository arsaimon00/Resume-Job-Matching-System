import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import extract_text, preprocess_text
from model import compare_models, rank_resumes, get_top_resumes


# Page config
st.set_page_config(page_title="Resume Matcher", layout="wide")

# UI START
st.markdown("""
<style>

/* Background Gradient */
.stApp {
    background: linear-gradient(135deg, #eef2ff, #f0fdf4, #fef3c7);
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #1e3a8a;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    color: #475569;
    margin-bottom: 25px;
}

/* Section Titles */
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #0f172a;
    margin-top: 30px;
}

/* Cards */
.card {
    padding: 20px;
    border-radius: 16px;
    background: white;
    box-shadow: 0px 8px 18px rgba(0,0,0,0.08);
    text-align: center;
    transition: all 0.3s ease;
    border: 1px solid #e2e8f0;
}

.card:hover {
    transform: translateY(-6px);
    box-shadow: 0px 12px 24px rgba(0,0,0,0.12);
}

/* Button */
.stButton>button {
    background: linear-gradient(135deg, #6366f1, #22c55e);
    color: white;
    border-radius: 12px;
    height: 48px;
    font-size: 16px;
    font-weight: 600;
    border: solid;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #4f46e5, #16a34a);
}

/* Inputs */
div[data-testid="stTextArea"] textarea {
    background: white;
    color: black;
    border-radius: 12px;
    height: 180px;
    font-size: 16px;
    font-weight: 600;
    border: 1.5px solid;
}

/* File uploader */
/* Initial upload box */
[data-testid="stFileUploaderDropzone"] {
    border: 1.5px solid black !important;
    border-radius: 12px !important;
    background: white !important;
    padding: 12px !important;
}

/* Uploaded file list box */
[data-testid="stFileUploaderFile"] {
    border: 1.5px solid black !important;
    border-radius: 12px !important;
    background: white !important;
    margin-top: 5px !important;
    padding: 12px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px;
}

/* Divider */
hr {
    margin: 1px 0;
}

</style>
""", unsafe_allow_html=True)


# HEADER
st.markdown('<div class="main-title">Intelligent Resume Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find the best candidates using AI-powered similarity scoring.</div>', unsafe_allow_html=True)


st.divider()

# INPUT SECTION
st.markdown('<div class="section-title">Input Section</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])


with col1:
   
    job_desc = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste job description..."
    )

with col2:
    uploaded_files = st.file_uploader(
        "Upload Resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

# BUTTON
col1, col2, col3 = st.columns([1,2,1])
with col2:
    match_btn = st.button("Match Resumes", use_container_width=True)


# when click
if match_btn:
    if job_desc and uploaded_files:
        with st.spinner("Analyzing resumes..."):
            resumes = []
            resume_names = []

            for file in uploaded_files:
                text = extract_text(file)
                cleaned = preprocess_text(text)
                resumes.append(cleaned)
                resume_names.append(file.name.split('.')[0])

            job_cleaned = preprocess_text(job_desc)

            results = compare_models(job_cleaned, resumes, resume_names)
            ranked = rank_resumes(results)
            top_resumes = get_top_resumes(ranked)

        st.success("Analysis completed successfully!")

        st.divider()

        # ALL SCORES TABLE
       
        st.markdown('<div class="section-title">All Resume Scores</div>', unsafe_allow_html=True)

        df = pd.DataFrame(ranked)
        df.columns = ["Resume", "TF-IDF", "Word2Vec", "BERT", "Final Score"]

        st.dataframe(df, use_container_width=True)

        st.divider()
       
        # TOP 5 CANDIDATES
   
        st.markdown('<div class="section-title">Top Candidates</div>', unsafe_allow_html=True)

        top_df = pd.DataFrame(top_resumes)
        cols = st.columns(5)

        colors = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#06b6d4"]

        for i, row in top_df.iterrows():
            with cols[i]:
                st.markdown(f"""
                <div class="card">
                    <div style="font-size:28px; font-weight:700; color:{colors[i]};">{i+1}</div>
                    <div style="font-size:15px; color:#334155; margin-top:8px;">
                        {row['resume_id']}
                    </div>
                    <div style="font-size:24px; font-weight:700; color:{colors[i]}; margin-top:10px;">
                        {round(row['final'],2)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # MODEL-WISE CHART
        st.subheader("Model-wise Score Comparison")


        model_df = pd.DataFrame(ranked)
        model_df = model_df.melt(
            id_vars="resume_id",
            value_vars=["tfidf", "word2vec", "bert"],
            var_name="Model",
            value_name="Score"
        )


        plt.figure(figsize=(10,5))
        sns.barplot(x="resume_id", y="Score", hue="Model", data=model_df)
        plt.title("Model-wise Resume Scores")
        plt.ylabel("Similarity (%)")
        plt.xlabel("Resumes")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

        st.divider()
   
        # TOP 5 CHART
   
        st.subheader("Top 5 Resume Similarity Scores")

        top_df_plot = pd.DataFrame(top_resumes)
        plt.figure(figsize=(8,4))
        sns.barplot(x="resume_id", y="final", data=top_df_plot, palette="viridis")
        plt.title("Top 5 Resumes by Final Score")
        plt.ylabel("Final Similarity (%)")
        plt.xlabel("Resume")
        plt.ylim(0, 100)
        plt.tight_layout()
        st.pyplot(plt)

    else:
        st.error("Please enter job description and upload resumes.")
