# OpenSim RAG Assistant 🧠🦵

<div align="center">

![OpenSim RAG Logo](https://simtk.org/logos/logo.png)

**A Retrieval Augmented Generation (RAG) system for OpenSim biomechanics software**

[![GitHub license](https://img.shields.io/github/license/yourusername/opensim-rag)](https://github.com/yourusername/opensim-rag/blob/main/LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

</div>

## 🌟 Overview

OpenSim RAG Assistant helps biomechanics researchers, students, and practitioners quickly find information about [OpenSim](https://simtk.org/projects/opensim), a powerful but complex biomechanical modeling software. This tool uses modern Retrieval Augmented Generation (RAG) technology to:

- Answer natural language questions about OpenSim
- Find relevant documentation sections
- Provide step-by-step instructions for common tasks
- Help users get acquainted with OpenSim terminology and workflows

**No API keys required!** This system uses Hugging Face's free models for semantic search.

## 📋 Features

- **Intelligent Document Retrieval**: Find relevant OpenSim documentation based on natural language queries
- **Automatic Scraping**: Collect documentation from the official OpenSim website
- **Semantic Search**: Understand the meaning of your questions, not just keywords
- **User-Friendly Interface**: Simple chat UI for asking questions
- **Citation Sources**: See where the information comes from
- **Local Processing**: All data and processing happens on your machine

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Git ([Download](https://git-scm.com/downloads))
- pip or conda

### Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/opensim-rag.git
cd opensim-rag

# Create and activate a conda environment
conda create -n opensim-rag python=3.10
conda activate opensim-rag

# Install dependencies
pip install -r requirements.txt
```

### Step-by-Step Setup and Testing

Follow these steps in order to ensure everything is working properly:

#### 1️⃣ Test the basic RAG system with sample data

This step verifies that Hugging Face embeddings are working correctly:

```bash
python hf_rag.py
```

You should see output showing sample document retrieval for test queries.

#### 2️⃣ Collect OpenSim documentation

This step scrapes documentation from the OpenSim website:

```bash
python opensim_scraper.py
```

This will create a file `data/opensim_docs.json` with the collected documentation.

#### 3️⃣ Set up the complete RAG system

This builds the vector database and provides an interactive command-line interface:

```bash
python opensim_rag_complete.py
```

Try asking questions about OpenSim to test the system.

#### 4️⃣ Launch the web application

Finally, start the web interface:

```bash
python app.py
```

Open your browser and go to [http://localhost:8000](http://localhost:8000)

## 💬 Using the Assistant

Once set up, you can ask questions about OpenSim through either:

### Command Line Interface

```bash
python opensim_rag_complete.py
```

### Web Interface

```bash
python app.py
```

Then browse to [http://localhost:8000](http://localhost:8000)

### Example Questions

- "How do I install OpenSim?"
- "What are markers in OpenSim and how do I add them?"
- "How do I run inverse kinematics?"
- "What's the difference between forward and inverse dynamics?"
- "How can I visualize muscle activations?"

## 🧩 Project Structure

```
opensim-rag/
├── app.py                        # Web application
├── create_favicon.py             # Utility script for creating favicon
├── create_placeholder_logo.py    # Utility script for creating placeholder logo
├── download_logo.py              # Utility script for downloading OpenSim logo
├── hf_rag.py                     # Basic RAG with Hugging Face embeddings
├── opensim_rag_complete.py       # Complete RAG system with interactive CLI
├── opensim_scraper.py            # Web scraper for OpenSim documentation
├── requirements.txt              # Python dependencies
├── data/                         # Directory for storing document data
│   └── opensim_docs.json         # Scraped documentation (generated)
├── static/                       # Static files for web app
│   ├── favicon.ico               # Favicon (generated)
│   └── images/                   # Images for web app
│       └── opensim_logo.png      # OpenSim logo (generated)
├── templates/                    # HTML templates for web app
│   └── index.html                # Main template (generated)
└── opensim_chroma_db/            # Vector database (generated)
```

## 🛠️ Customization

### Scraping Additional Documentation

Modify the base URLs in `opensim_scraper.py` to include additional sources:

```python
self.base_urls = [
    "https://simtk.org/projects/opensim",
    "https://simtk-confluence.stanford.edu/display/OpenSim/User%27s+Guide",
    "https://simtk-confluence.stanford.edu/display/OpenSim/Tutorials",
    # Add your URLs here
]
```

### Changing the Embedding Model

You can use a different Hugging Face embedding model by changing:

```python
EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"  # Change to another model
```

Popular alternatives include:
- `"sentence-transformers/all-mpnet-base-v2"` (more accurate but slower)
- `"sentence-transformers/all-distilroberta-v1"` (balanced performance)

## 📚 How It Works

1. **Document Collection**: The system scrapes OpenSim documentation from various sources
2. **Text Processing**: Documents are split into chunks of appropriate size
3. **Embedding Generation**: Hugging Face models convert text into vector embeddings
4. **Vector Database**: Embeddings are stored in a Chroma vector database
5. **Query Processing**: User questions are converted to embeddings and used to search for similar content
6. **Response Generation**: The most relevant document chunks are retrieved and presented to the user

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- Add a language model for better answer synthesis
- Improve the web interface
- Add support for more documentation sources
- Create better scraping for complex documentation
- Add more interactive features

Please feel free to submit a PR or open an issue.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Acknowledgments

- The OpenSim team for their excellent biomechanics software
- Hugging Face for providing free embedding models
- LangChain for the RAG framework
- The biomechanics community for their continued research and innovation

---

<div align="center">
    <p>Made with ❤️ for the biomechanics community</p>
</div>
