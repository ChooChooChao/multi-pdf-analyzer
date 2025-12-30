import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs: # loop through pdfs
        pdf_reader = PdfReader(pdf) # creates pages from the pdf
        for page in pdf_reader.pages: # loop through pages
            text += page.extract_text() # extract and append the text
    return text

def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(raw_text) # returns list of chunks
    return chunks

def get_vector_store(text_chunks):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def main():
    load_dotenv() # allows langchain access to api keys in .env file

    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:") # tab/page title

    st.header("Chat with multiple PDFs :books:") # Main header on webpage
    st.text_input("Ask a Question about your documents: ") # text input area for users (text above input area)

    # sidebar where users input docs
    with st.sidebar: # Note: Keyword "with" used to put things inside sidebar
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your PDFs here and click on process", accept_multiple_files=True) # element that allows the actual upload of files
        if st.button("Process"): # make conditional to trigger only when pressed
            with st.spinner("Processing"): # visual spinning wheel to inform user it is running
                # get the pdf text
                raw_text = get_pdf_text(pdf_docs)
                # st.write(raw_text)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)
                # st.write(text_chunks)

                # create vector store
                vector_store = get_vector_store(text_chunks)

if __name__ == "__main__":
    main()