import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationalRetrievalChain
# from langchain_anthropic import ChatAnthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

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

def _get_memory():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = InMemoryChatMessageHistory()
    return st.session_state.chat_history

def get_conversation_chain(vectorstore):
    llm = ChatAnthropic(model="claude-3-5-sonnet-latest")
    retriever = vectorstore.as_retriever()

    # Minimal retrieval + LLM runnable
    chain = retriever | llm  # Means to take the output of the left runnable and feed it as input to the right runnable.
    # EQUIVALENT 
    # def chain(input):
    #   intermediate = retriever.invoke(input)
    #   return llm.invoke(intermediate)

    # This is the *direct* replacement for ConversationBufferMemory
    conversation_chain = RunnableWithMessageHistory(
        chain,
        lambda session_id: _get_memory(),
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return conversation_chain

def main():
    load_dotenv() # allows langchain access to api keys in .env file

    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:") # tab/page title

    st.header("Chat with multiple PDFs :books:") # Main header on webpage
    st.text_input("Ask a Question about your documents: ") # text input area for users (text above input area)

    # check for the initial of the session state and initializes it if not found
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

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
                vectorstore = get_vector_store(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore) # session_state ==> makes it persistent so streamlit doesn't reload the code everytime

if __name__ == "__main__":
    main()