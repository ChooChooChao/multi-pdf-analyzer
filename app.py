import streamlit as st
from dotenv import load_dotenv



def main():
    load_dotenv() # allows langchain access to api keys in .env file

    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:") # tab/page title

    st.header("Chat with multiple PDFs :books:") # Main header on webpage
    st.text_input("Ask a Question about your documents: ") # text input area for users (text above input area)

    # sidebar where users input docs
    with st.sidebar: # Note: Keyword "with" used to put things inside sidebar
        st.subheader("Your documents")
        st.file_uploader("Upload your PDFs here and click on process") # element that allows the actual upload of files
        st.button("Process")

if __name__ == "__main__":
    main()