import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import LangChain components
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import our scraper
from opensim_scraper import OpenSimScraper

# Load environment variables
load_dotenv()

# Constants
EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"  # A small, free embedding model
CHROMA_DB_DIR = "opensim_chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
DATA_DIR = "data"
DOCS_FILE = "opensim_docs.json"

class OpenSimRAG:
    """Complete RAG system for OpenSim documentation using Hugging Face"""
    
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL_NAME
        )
        self.vectorstore = None
        self.chat_history = []
        
    def collect_documents(self, max_pages=50, use_cached=True):
        """
        Collect documents from OpenSim website
        
        Args:
            max_pages: Maximum number of pages to scrape
            use_cached: Whether to use cached documents if available
        
        Returns:
            List of documents
        """
        docs_path = os.path.join(DATA_DIR, DOCS_FILE)
        
        # Check if we can use cached documents
        if use_cached and os.path.exists(docs_path):
            print(f"Loading cached documents from {docs_path}")
            with open(docs_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            print(f"Loaded {len(documents)} documents")
            return documents
        
        # Scrape documents
        print("Scraping documents from OpenSim website...")
        scraper = OpenSimScraper(output_dir=DATA_DIR)
        documents = scraper.scrape(max_pages=max_pages)
        return documents
    
    def create_vector_database(self, documents: List[Dict[str, Any]], force_recreate=False):
        """
        Create and persist vector database from documents
        
        Args:
            documents: List of documents with content and metadata
            force_recreate: Whether to recreate the database even if it exists
        """
        # Check if database already exists
        if os.path.exists(CHROMA_DB_DIR) and not force_recreate:
            print(f"Vector database already exists at {CHROMA_DB_DIR}")
            self.load_vector_database()
            return
        
        print("Creating new vector database...")
        
        # Convert to LangChain Document format
        langchain_docs = []
        for doc in documents:
            langchain_docs.append(
                Document(
                    page_content=doc["content"],
                    metadata=doc["metadata"]
                )
            )
        
        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n### ", "\n#### ", "\n", " ", ""]
        )
        
        # Split documents
        splits = text_splitter.split_documents(langchain_docs)
        print(f"Split {len(langchain_docs)} documents into {len(splits)} chunks")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        
        # Persist to disk
        self.vectorstore.persist()
        print(f"Vector database created with {len(splits)} chunks and persisted to {CHROMA_DB_DIR}")
    
    def load_vector_database(self):
        """
        Load existing vector database
        """
        if os.path.exists(CHROMA_DB_DIR):
            self.vectorstore = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=self.embeddings
            )
            print(f"Loaded vector database from {CHROMA_DB_DIR}")
        else:
            print(f"No existing vector database found at {CHROMA_DB_DIR}")
    
    def process_query(self, query: str, k: int = 4) -> Dict[str, Any]:
        """
        Process a user query and return relevant documents
        
        Args:
            query: The user's question about OpenSim
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with relevant documents
        """
        # Make sure vector store is loaded
        if self.vectorstore is None:
            self.load_vector_database()
            
        if self.vectorstore is None:
            return {"answer": "No knowledge base available. Please add documents first.", "sources": []}
        
        # Add query to chat history
        self.chat_history.append({"role": "user", "content": query})
        
        # Get relevant documents
        docs = self.vectorstore.similarity_search(query, k=k)
        
        # For now, without an LLM, we'll just return the most relevant document
        if docs:
            answer = f"Here's what I found about '{query}':\n\n"
            answer += docs[0].page_content
        else:
            answer = "I couldn't find any relevant information about that topic."
        
        # Add to chat history
        self.chat_history.append({"role": "assistant", "content": answer})
        
        # Format the response
        response = {
            "answer": answer,
            "sources": [
                {
                    "title": doc.metadata.get("title", "Unknown"),
                    "source": doc.metadata.get("source", "Unknown"),
                    "section": doc.metadata.get("section", "Unknown"),
                    "type": doc.metadata.get("type", "Unknown")
                }
                for doc in docs
            ]
        }
        
        return response
    
    def clear_chat_history(self):
        """Clear the chat history"""
        self.chat_history = []
        print("Chat history cleared")


def main():
    print("Initializing OpenSim RAG system")
    
    # Create the RAG system
    rag = OpenSimRAG()
    
    # Create output directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Collect documents (use_cached=True to use existing documents if available)
    # Set use_cached=False to force re-scraping
    documents = rag.collect_documents(max_pages=20, use_cached=True)
    
    # Create vector database
    # Set force_recreate=True to recreate the database even if it exists
    rag.create_vector_database(documents, force_recreate=False)
    
    # Interactive query loop
    print("\nOpenSim RAG system is ready for queries!")
    print("Type 'exit' to quit, 'clear' to clear chat history")
    
    while True:
        query = input("\nEnter your query: ")
        
        if query.lower() == 'exit':
            break
        
        if query.lower() == 'clear':
            rag.clear_chat_history()
            continue
        
        response = rag.process_query(query)
        
        print("\nAnswer:")
        print(response["answer"][:500] + "..." if len(response["answer"]) > 500 else response["answer"])
        
        print("\nSources:")
        for i, source in enumerate(response["sources"], 1):
            print(f"{i}. {source['title']} ({source['type']})")
            print(f"   Source: {source['source']}")
    
    print("\nThanks for using the OpenSim RAG system!")


if __name__ == "__main__":
    main()