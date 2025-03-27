import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import numpy as np

# Import LangChain components
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_text_splitters  import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Constants
EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"  # A small, free embedding model
CHROMA_DB_DIR = "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class OpenSimRAG:
    """RAG system for OpenSim documentation using Hugging Face"""
    
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL_NAME
        )
        self.vectorstore = None
        self.chat_history = []
        
    def create_vector_database(self, documents: List[Dict[str, Any]]):
        """
        Create and persist vector database from documents
        
        Args:
            documents: List of documents with content and metadata
        """
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
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query and return relevant documents
        
        Args:
            query: The user's question about OpenSim
            
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
        docs = self.vectorstore.similarity_search(query, k=4)
        
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

def create_sample_documents():
    """
    Create a set of sample OpenSim documents for testing
    """
    document_contents = [
        {
            "content": """# Getting Started with OpenSim

OpenSim is an open source software system that allows users to develop models of musculoskeletal structures and create dynamic simulations of movement.

## Installation

1. Go to the OpenSim download page: https://simtk.org/projects/opensim
2. Download the appropriate version for your operating system
3. Run the installer and follow the prompts
4. Launch OpenSim from your applications menu

## First Steps

When you first open OpenSim, you'll see the Navigator view on the left side showing available models, and the main visualization window on the right.

Try loading an example model:
1. Go to File > Open Model
2. Browse to the examples folder in your OpenSim installation
3. Select one of the example models (e.g., 'Arm26')
4. Click 'Open'""",
            "metadata": {
                "title": "Getting Started with OpenSim",
                "source": "https://simtk.org/projects/opensim/docs/getting_started.html",
                "section": "Introduction",
                "type": "tutorial"
            }
        },
        {
            "content": """## Adding Markers to a Model

Markers in OpenSim represent experimental markers that would be placed on a subject during a motion capture session. They're used for model scaling and inverse kinematics.

### Adding a Marker Through the GUI

1. Open your model in OpenSim
2. Right-click on 'Markers' in the Navigator
3. Select 'Add Marker'
4. In the dialog that appears:
   - Enter a name for your marker
   - Select the body to attach the marker to
   - Set the location (X, Y, Z coordinates) of the marker relative to the body
5. Click 'OK'

### Adding Markers Programmatically

You can also add markers using the OpenSim API:

```python
# Add a marker using the OpenSim API
import opensim as osim

# Load your model
model = osim.Model('your_model.osim')

# Create a new marker
marker = osim.Marker()
marker.setName('new_marker')
marker.setParentFrame(model.getBodySet().get('tibia_r'))
marker.set_location(osim.Vec3(0.0, 0.2, 0.1))

# Add the marker to the model
model.addMarker(marker)

# Save the model
model.initSystem()
model.printToXML('model_with_marker.osim')
```

### Common Issues with Markers

- Ensure marker names are unique within the model
- Check that the parent body exists in the model
- Verify the marker location is anatomically reasonable""",
            "metadata": {
                "title": "Working with Markers",
                "source": "https://simtk.org/projects/opensim/docs/markers.html",
                "section": "Markers",
                "type": "how-to"
            }
        },
        {
            "content": """# Running Inverse Kinematics in OpenSim

Inverse Kinematics (IK) is the process of determining the joint angles that position the model in a pose that best matches experimental marker positions.

## Prerequisites

Before running IK, you need:
- A scaled OpenSim model (.osim file)
- Experimental marker data (.trc file)
- A marker set that corresponds between your model and experimental data

## Running IK via the GUI

1. Open your model in OpenSim
2. Go to Tools > Inverse Kinematics
3. In the dialog that appears:
   - Click "Load" to load a settings file, or set up manually:
   - Set your model file
   - Set your marker data file
   - Set the time range for analysis
   - Set output directory and file name
   - Set weighting for markers (optional)
4. Click "Run" to execute the IK tool

## Running IK via Python API

```python
import opensim as osim

# Create the IK tool
ik_tool = osim.InverseKinematicsTool()

# Load the model
model = osim.Model("scaled_model.osim")
model.initSystem()
ik_tool.setModel(model)

# Set marker file
ik_tool.setMarkerDataFileName("marker_data.trc")

# Set the time range
ik_tool.setStartTime(0.0)
ik_tool.setEndTime(1.0)

# Set output files
ik_tool.setOutputMotionFileName("ik_results.mot")

# Run the IK tool
ik_tool.run()
```

## Troubleshooting

### Common IK Problems

- **High marker errors**: Check marker placement on the model, or adjust marker weights
- **Unrealistic joint angles**: Add joint limits or coordinate constraints
- **IK fails to converge**: Try increasing the error tolerance or maximum iterations""",
            "metadata": {
                "title": "Inverse Kinematics Guide",
                "source": "https://simtk.org/projects/opensim/docs/inverse_kinematics.html",
                "section": "Analysis",
                "type": "tutorial"
            }
        }
    ]
    return document_contents

def main():
    print("Initializing OpenSim RAG system with Hugging Face embeddings")
    
    # Create the RAG system
    rag = OpenSimRAG()
    
    # Check if vector database exists
    if os.path.exists(CHROMA_DB_DIR):
        print("Loading existing vector database...")
        rag.load_vector_database()
    else:
        print("Creating new vector database...")
        documents = create_sample_documents()
        rag.create_vector_database(documents)
    
    # Test some queries
    test_queries = [
        "How do I install OpenSim?",
        "How can I add markers to my model?",
        "What is inverse kinematics and how do I run it?"
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        
        response = rag.process_query(query)
        
        print("\nAnswer:")
        print(response["answer"][:300] + "..." if len(response["answer"]) > 300 else response["answer"])
        
        print("\nSources:")
        for source in response["sources"]:
            print(f"- {source['title']} ({source['type']})")
    
    print("\nRAG system test completed successfully.")
 
main()