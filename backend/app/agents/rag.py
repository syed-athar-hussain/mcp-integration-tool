from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

embeddings = OpenAIEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

async def build_repo_rag_context(files_json: str) -> str:
    """Basic RAG: chunk and embed repo files returned by MCP"""
    files = json.loads(files_json).get("files", [])
    documents = []
    for f in files:
        documents.append(f["content"])
    splits = text_splitter.split_text("\n\n".join(documents))
    vectorstore = FAISS.from_texts(splits, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke("relevant code context")
    return "\n\n".join([doc.page_content for doc in docs])