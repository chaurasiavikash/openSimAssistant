import os
import sys
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

print("Testing Hugging Face setup...")

# Test imports
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_huggingface import HuggingFaceEmbeddings
    print("LangChain imports successful")
except ImportError as e:
    print(f"Error importing LangChain components: {e}")
    sys.exit(1)

# Test Hugging Face embeddings
try:
    # This uses a small, free model for embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    result = embeddings.embed_query("Test query")
    print(f"Hugging Face embeddings working: Generated embedding of length {len(result)}")
except Exception as e:
    print(f"Error with Hugging Face embeddings: {e}")
    sys.exit(1)

print("All tests passed! Your environment is set up correctly with Hugging Face.")