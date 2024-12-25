from main import coldEmailGen,portfoliodb,pageExt,clean_text
import streamlit as st
st.set_page_config(page_title="Cold Email Generator", page_icon="📧",layout="centered")
st.markdown(
    """
    <style>
    /* This targets the main content area of the Streamlit app */
    .stApp {
        background-color: #7695FF;
    }
   .stButton>button {
        background-color: #9DBDFF; /* Change to your desired color */
        color: white; /* Change button text color */
        transition: all 500ms;
    }

    /* Optional: Change button hover effect */
    .stButton>button:hover {
        background-color: #7d97cc; /* Hover color */
        color: white; /* Hover text color */
        transition: all 500ms;
        border: 1px solid black;
    }
    /* Hide the default Streamlit header */
    </style>
    """, 
    unsafe_allow_html=True
)
st.title("Cold Email🤖🚀")

urlinput = st.text_input("Enter URL to generate email",value="https://odolution.com/jobs/detail/python-developer-interns-lead-to-permanent-job-87")
submit = st.button("Generate")

if submit:
    fileurl = "my_portfolio.csv"
    portfoliodb(fileurl)
    res = pageExt(urlinput)
    emailout = coldEmailGen(res)

    st.code(emailout, language='markdown')
