import os
import streamlit as st
import zipfile
from io import BytesIO
from dotenv import load_dotenv
from web_article_scanner import ArticleCollector  # Import from your script

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH")

# Initialize the article collector
collector = ArticleCollector(OPENAI_API_KEY,WKHTMLTOPDF_PATH)
# Streamlit UI
st.title("🕵️‍♂️ Web Article Scanner")
st.markdown("Search and download domain-related articles as PDFs.")

# Input Form
with st.form("Input Form"):
    domain_description = st.text_area("Domain Description", "common diseases in sheep etc..")
    num_documents = st.number_input("Number of Documents Required", min_value=1, max_value=50, value=10)
    
    # Advanced Options (Hidden)
    with st.expander("Advanced Options"):
        min_words = st.number_input("Minimum Words in an Article", min_value=300, max_value=10000, value=3000)
        articles_per_query = st.number_input("Articles per Query", min_value=1, max_value=10, value=5)
    
    submit_button = st.form_submit_button("Start Collecting")

# When the form is submitted
if submit_button:
    st.info("Starting the article collection process...")
    output_dir = "collected_articles"
    os.makedirs(output_dir, exist_ok=True)
    
    progress_bar = st.progress(0)
    progress_text = st.empty()
    collected_count = 0
    results = []

    try:
        with st.spinner("Collecting articles..."):
            for article in collector.collect_articles(domain_description, output_dir, num_documents):
                results.append(article)
                collected_count += 1
                progress_bar.progress(collected_count / num_documents)
                progress_text.text(f"Collected {collected_count}/{num_documents} articles...")
        
        st.success(f"Collected {len(results)} articles!")

        # Zip all PDFs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for res in results:
                zip_file.write(res["pdf_path"], os.path.basename(res["pdf_path"]))
        zip_buffer.seek(0)

        # Provide download button for the zip file
        st.download_button(
            "Download All PDFs as ZIP",
            data=zip_buffer,
            file_name="collected_articles.zip",
            mime="application/zip",
        )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
