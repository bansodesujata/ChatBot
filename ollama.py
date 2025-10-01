import os
import streamlit as st
import hashlib
import pdfminer
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

# Configuration
VECTOR_STORE_PATH = "faiss_index"
PDF_FOLDER = "documents"
HASH_FILE = os.path.join(VECTOR_STORE_PATH, "pdf_hash.txt")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

st.title("📄 Bajaj Finance Assistant")

# Get PDF files
pdf_files = [os.path.join(PDF_FOLDER, f) for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf")]
if not pdf_files:
    st.error(f"No PDF files found in '{PDF_FOLDER}' folder. Please add your PDFs.")
    st.stop()

# Function to calculate file hash
def generate_pdf_hash(filepaths):
    md5 = hashlib.md5()
    for path in sorted(filepaths):
        with open(path, 'rb') as f:
            while chunk := f.read(4096):
                md5.update(chunk)
    return md5.hexdigest()

# Load embedding model
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# Check for vector store and hash
vector_exists = os.path.exists(VECTOR_STORE_PATH)
current_hash = generate_pdf_hash(pdf_files)
saved_hash = ""
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, 'r') as f:
        saved_hash = f.read()

# Create or load vector store
if vector_exists and saved_hash == current_hash:
    st.success("✅ Loaded cached vector store.")
    db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    st.warning("🔄 Processing PDFs and building vector store...")
    all_pages = []
    for pdf in pdf_files:
        st.write(f"📄 Processing: {os.path.basename(pdf)}")
        loader = UnstructuredPDFLoader(pdf)
        pages = loader.load()
        all_pages.extend(pages)

    st.info("🔎 Sample extracted text:")
    for i, page in enumerate(all_pages[:2]):
        st.write(f"📃 Chunk {i + 1}:")
        st.write(page.page_content[:500])

    db = FAISS.from_documents(all_pages, embeddings)
    db.save_local(VECTOR_STORE_PATH)

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    with open(HASH_FILE, 'w') as f:
        f.write(current_hash)

    st.success("✅ Vector store created and saved!")

# Chatbot setup
retriever = db.as_retriever()
#llm = Ollama(model="llama2")
llm = Ollama(model="gemma:2b")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

query = st.text_input("Ask a question:")

if query:
    with st.spinner("🤖 Generating answer..."):
        answer = qa_chain.run(query)
    st.write("🧠", answer)
