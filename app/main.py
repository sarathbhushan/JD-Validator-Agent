import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import pandas as pd
import io

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="JD Validator", page_icon="📧")
    st.title("📧 JD Validator")
    
    # Add sidebar for database operations
    with st.sidebar:
        st.header("Database Operations")
        
        # File uploader with instructions
        st.info("Upload a CSV file with 'Techstack' and 'Links' columns")
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="Upload your portfolio CSV file"
        )
        
        if uploaded_file is not None:
            try:
                # Show upload status
                with st.spinner('Processing CSV file...'):
                    # Read the uploaded file with explicit encoding
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                    
                    # Validate columns
                    required_columns = ['Techstack', 'Links']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    else:
                        # Preview the data
                        st.write("Preview of uploaded data:")
                        st.dataframe(df.head(3), use_container_width=True)
                        
                        # Load to database
                        portfolio.data = df
                        portfolio.load_portfolio(force_reload=True)
                        st.success("✅ CSV file loaded successfully!")
                        
                        # Show row count
                        st.text(f"Loaded {len(df)} rows to database")
            except UnicodeDecodeError:
                st.error("Error: Please ensure your CSV file is encoded in UTF-8")
            except pd.errors.EmptyDataError:
                st.error("Error: The uploaded file is empty")
            except Exception as e:
                st.error(f"Error processing CSV: {str(e)}")
        
        st.divider()
        
        # Database operation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Database"):
                try:
                    with st.spinner('Clearing database...'):
                        portfolio.clear_collection()
                        st.success("Vector database cleared successfully!")
                except Exception as e:
                    st.error(f"Error clearing database: {str(e)}")
        
        with col2:
            if st.button("Reload Database"):
                if not hasattr(portfolio, 'data'):
                    st.error("Please upload a CSV file first!")
                else:
                    try:
                        with st.spinner('Reloading database...'):
                            portfolio.load_portfolio(force_reload=True)
                            st.success("Vector database reloaded successfully!")
                    except Exception as e:
                        st.error(f"Error reloading database: {str(e)}")
        
        # Show database stats
        st.divider()
        st.subheader("Database Stats")
        try:
            doc_count = portfolio.collection.count()
            st.text(f"Total documents: {doc_count}")
        except Exception as e:
            st.error(f"Error getting stats: {e}")
    
    # Main content
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="JD Validator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)


