from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


def create_chunks(text):
    """
    Splits large project text into smaller chunks.
    This is useful for RAG because LLMs cannot process very large files at once.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)
    return chunks


def create_vector_store(text, api_key):
    """
    Creates FAISS vector database from project text.
    """

    if not text or not text.strip():
        return None

    chunks = create_chunks(text)

    if not chunks:
        return None

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    return vector_store


def retrieve_relevant_context(vector_store, query, k=5):
    """
    Retrieves top-k relevant chunks from FAISS vector store.
    """

    if vector_store is None:
        return ""

    docs = vector_store.similarity_search(query, k=k)

    context = ""

    for i, doc in enumerate(docs, start=1):
        context += f"\n\n--- Relevant Chunk {i} ---\n"
        context += doc.page_content

    return context