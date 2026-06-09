import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()

# Global vector store
vectorstore = None
FAISS_INDEX_PATH = "faiss_index"

def load_documents(docs_folder="documents"):
    """Load all PDFs from the documents folder"""
    global vectorstore

    embeddings = OpenAIEmbeddings(
        api_key=os.environ["OPENAI_API_KEY"]
    )

    # ⚡ Load saved index if it exists
    if os.path.exists(FAISS_INDEX_PATH):
        print("⚡ Loading saved FAISS index...")
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ RAG pipeline ready! (loaded from disk)")
        return True

    # 🔨 Build fresh index if no saved index
    pdf_files = [
        f for f in os.listdir(docs_folder)
        if f.endswith(".pdf")
    ]

    if not pdf_files:
        print("⚠️ No PDFs found in documents folder")
        return False

    print(f"📄 Loading {len(pdf_files)} PDF(s)...")
    all_docs = []

    for pdf_file in pdf_files:
        path = os.path.join(docs_folder, pdf_file)
        loader = PyPDFLoader(path)
        docs = loader.load()
        all_docs.extend(docs)
        print(f"  ✅ Loaded: {pdf_file}")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(all_docs)
    print(f"📦 Created {len(chunks)} chunks")

    # Build and save FAISS index
    print("💾 Building and saving FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print("✅ RAG pipeline ready! (saved to disk)")
    return True

def reload_documents(docs_folder="documents"):
    """Force rebuild index — call when new docs are added"""
    global vectorstore
    
    # Delete old index
    import shutil
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)
        print("🗑️ Old index deleted")
    
    # Rebuild
    return load_documents(docs_folder)

def ask_documents(question):
    """Search documents and answer question"""
    global vectorstore

    if vectorstore is None:
        return None

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_kwargs={"k": 3}
        )
    )

    result = qa_chain.invoke({"query": question})
    return result["result"]