import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Dict, Any
import json
import uvicorn

# Import our RAG system
from opensim_rag_complete import OpenSimRAG

# Create directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Create FastAPI app
app = FastAPI(title="OpenSim Assistant")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize the RAG system
rag = OpenSimRAG()

# Check if vector database exists, if not, initialize it
if not os.path.exists("opensim_chroma_db"):
    try:
        # Try to use cached documents
        docs_path = os.path.join("data", "opensim_docs.json")
        if os.path.exists(docs_path):
            with open(docs_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            rag.create_vector_database(documents)
        else:
            # Scrape new documents
            documents = rag.collect_documents(max_pages=20)
            rag.create_vector_database(documents)
    except Exception as e:
        print(f"Error initializing vector database: {e}")
else:
    # Load existing vector database
    rag.load_vector_database()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def process_query(query: str = Form(...)):
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Process the query
    response = rag.process_query(query)
    
    return response

@app.post("/clear")
async def clear_history():
    rag.clear_chat_history()
    return {"status": "success", "message": "Chat history cleared"}

# 404 handler
@app.exception_handler(404)
async def custom_404_handler(request, exc):
    return {"error": "Not Found", "message": "The requested resource could not be found"}, 404

# Create template files
def create_template_files():
    # Create index.html
    index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenSim Assistant</title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .chat-container {
            height: calc(100vh - 200px);
        }
        .message-container {
            max-height: calc(100vh - 280px);
        }
        pre {
            background-color: #f3f4f6;
            padding: 1rem;
            border-radius: 0.375rem;
            overflow-x: auto;
        }
        code {
            font-family: Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        }
    </style>
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal">
    <div class="container mx-auto px-4 py-8">
        <header class="bg-blue-600 text-white p-4 rounded-t-lg shadow-lg">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold">OpenSim Assistant</h1>
                    <p class="text-blue-100">Your intelligent guide to OpenSim biomechanics software</p>
                </div>
                <div>
                    <img src="/static/images/opensim_logo.png" alt="OpenSim Logo" class="h-16 bg-white p-2 rounded">
                </div>
            </div>
        </header>
        
        <main class="bg-white rounded-b-lg shadow-lg p-6">
            <div class="chat-container flex flex-col">
                <div class="message-container flex-grow overflow-y-auto mb-4 p-2">
                    <div id="messages" class="space-y-4">
                        <div class="flex items-start">
                            <div class="flex-shrink-0 bg-blue-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold">
                                A
                            </div>
                            <div class="ml-3 bg-blue-50 p-3 rounded-lg shadow">
                                <p class="text-sm text-gray-800">
                                    Hello! I'm your OpenSim Assistant. I can help you with:
                                </p>
                                <ul class="list-disc list-inside mt-2 text-sm text-gray-700 space-y-1">
                                    <li>Getting started with OpenSim</li>
                                    <li>Creating and modifying models</li>
                                    <li>Running simulations</li>
                                    <li>Analyzing results</li>
                                    <li>Troubleshooting common issues</li>
                                </ul>
                                <p class="text-sm text-gray-800 mt-2">
                                    How can I assist you today?
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="flex items-end bg-gray-50 p-4 rounded-lg">
                    <div class="flex-grow">
                        <textarea id="userInput" rows="3" class="w-full px-3 py-2 resize-none border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent" placeholder="Ask a question about OpenSim..."></textarea>
                    </div>
                    <div class="ml-4">
                        <button id="sendButton" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg focus:outline-none focus:shadow-outline transform transition hover:scale-105">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="mt-6 border-t pt-4">
                <div class="flex justify-between items-center">
                    <h2 class="text-xl font-semibold text-gray-700">Popular Questions</h2>
                    <button id="clearButton" class="text-sm text-gray-500 hover:text-red-500">Clear Chat</button>
                </div>
                <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <button class="suggestion-btn text-left p-2 border border-gray-200 rounded hover:bg-gray-50 text-sm text-gray-700">How do I add markers to my model?</button>
                    <button class="suggestion-btn text-left p-2 border border-gray-200 rounded hover:bg-gray-50 text-sm text-gray-700">What is the difference between inverse and forward dynamics?</button>
                    <button class="suggestion-btn text-left p-2 border border-gray-200 rounded hover:bg-gray-50 text-sm text-gray-700">How can I visualize muscle activations?</button>
                    <button class="suggestion-btn text-left p-2 border border-gray-200 rounded hover:bg-gray-50 text-sm text-gray-700">How do I import motion capture data?</button>
                </div>
            </div>
        </main>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const messagesContainer = document.getElementById('messages');
            const userInput = document.getElementById('userInput');
            const sendButton = document.getElementById('sendButton');
            const clearButton = document.getElementById('clearButton');
            const suggestionButtons = document.querySelectorAll('.suggestion-btn');
            
            // API endpoints
            const QUERY_ENDPOINT = '/query';
            const CLEAR_ENDPOINT = '/clear';
            
            // Add event listeners
            sendButton.addEventListener('click', handleSendMessage);
            userInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                }
            });
            
            clearButton.addEventListener('click', clearChat);
            
            suggestionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    userInput.value = button.textContent;
                    handleSendMessage();
                });
            });
            
            function handleSendMessage() {
                const message = userInput.value.trim();
                if (message === '') return;
                
                // Add user message to the chat
                addMessage('user', message);
                
                // Clear input field
                userInput.value = '';
                
                // Show loading indicator
                const loadingId = addMessage('assistant', '<div class="animate-pulse flex space-x-4"><div class="flex-1 space-y-2"><div class="h-2 bg-blue-200 rounded"></div><div class="h-2 bg-blue-200 rounded"></div><div class="h-2 bg-blue-200 rounded"></div></div></div>');
                
                // Send message to API
                const formData = new FormData();
                formData.append('query', message);
                
                fetch(QUERY_ENDPOINT, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Remove loading indicator
                    document.getElementById(loadingId).remove();
                    
                    // Add assistant response
                    addMessage('assistant', data.answer, data.sources);
                    
                    // Scroll to bottom
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                })
                .catch(error => {
                    // Remove loading indicator
                    document.getElementById(loadingId).remove();
                    
                    // Add error message
                    addMessage('assistant', 'Sorry, I encountered an error processing your request. Please try again.');
                    console.error('Error:', error);
                });
                
                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
            
            function clearChat() {
                // Clear chat on the server
                fetch(CLEAR_ENDPOINT, {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Clear messages from the UI
                        messagesContainer.innerHTML = '';
                        
                        // Add welcome message back
                        const welcomeDiv = document.createElement('div');
                        welcomeDiv.className = 'flex items-start';
                        welcomeDiv.innerHTML = `
                            <div class="flex-shrink-0 bg-blue-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold">
                                A
                            </div>
                            <div class="ml-3 bg-blue-50 p-3 rounded-lg shadow">
                                <p class="text-sm text-gray-800">
                                    Hello! I'm your OpenSim Assistant. I can help you with:
                                </p>
                                <ul class="list-disc list-inside mt-2 text-sm text-gray-700 space-y-1">
                                    <li>Getting started with OpenSim</li>
                                    <li>Creating and modifying models</li>
                                    <li>Running simulations</li>
                                    <li>Analyzing results</li>
                                    <li>Troubleshooting common issues</li>
                                </ul>
                                <p class="text-sm text-gray-800 mt-2">
                                    How can I assist you today?
                                </p>
                            </div>
                        `;
                        messagesContainer.appendChild(welcomeDiv);
                    }
                })
                .catch(error => {
                    console.error('Error clearing chat:', error);
                });
            }
            
            function addMessage(sender, content, sources = []) {
                const messageId = 'msg-' + Date.now();
                const messageDiv = document.createElement('div');
                messageDiv.id = messageId;
                messageDiv.className = 'flex items-start';
                
                const avatar = document.createElement('div');
                
                if (sender === 'user') {
                    avatar.className = 'flex-shrink-0 bg-green-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold';
                    avatar.textContent = 'U';
                    messageDiv.appendChild(avatar);
                    
                    const messageContent = document.createElement('div');
                    messageContent.className = 'ml-3 bg-green-50 p-3 rounded-lg shadow';
                    messageContent.textContent = content;
                    messageDiv.appendChild(messageContent);
                } else {
                    avatar.className = 'flex-shrink-0 bg-blue-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold';
                    avatar.textContent = 'A';
                    messageDiv.appendChild(avatar);
                    
                    const messageContent = document.createElement('div');
                    messageContent.className = 'ml-3 bg-blue-50 p-3 rounded-lg shadow';
                    
                    // Convert markdown to HTML - FIXED THE NEWLINE ISSUE HERE
                    const formattedContent = content
                        .replace(/^# (.+)$/gm, '<h1 class="text-xl font-bold mt-2 mb-1">$1</h1>')
                        .replace(/^## (.+)$/gm, '<h2 class="text-lg font-bold mt-2 mb-1">$1</h2>')
                        .replace(/^### (.+)$/gm, '<h3 class="text-md font-bold mt-2 mb-1">$1</h3>')
                        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\*(.+?)\*/g, '<em>$1</em>')
                        .replace(/`(.+?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
                        .replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>')
                        .replace(/\\n/g, '<br>');
                    
                    messageContent.innerHTML = formattedContent;
                    
                    // Add sources if available
                    if (sources && sources.length > 0) {
                        const sourcesDiv = document.createElement('div');
                        sourcesDiv.className = 'mt-2 pt-2 border-t border-gray-200 text-xs text-gray-600';
                        sourcesDiv.innerHTML = '<strong>Sources:</strong>';
                        
                        const sourcesList = document.createElement('ul');
                        sourcesList.className = 'list-disc list-inside mt-1';
                        
                        sources.forEach(source => {
                            const sourceItem = document.createElement('li');
                            sourceItem.innerHTML = `<a href="${source.source}" target="_blank" class="text-blue-500 hover:underline">${source.title}</a> (${source.type})`;
                            sourcesList.appendChild(sourceItem);
                        });
                        
                        sourcesDiv.appendChild(sourcesList);
                        messageContent.appendChild(sourcesDiv);
                    }
                    
                    messageDiv.appendChild(messageContent);
                }
                
                messagesContainer.appendChild(messageDiv);
                
                return messageId;
            }
        });
    </script>
</body>
</html>
    """
    
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print("Template files created successfully.")

# Create template files if they don't exist
if not os.path.exists("templates/index.html"):
    create_template_files()
else:
    # If the file exists but might have the error, recreate it
    create_template_files()
    print("Updated template files to fix JavaScript issues.")

# Run the app
if __name__ == "__main__":
    print("Starting OpenSim Assistant web app...")
    print("Open your browser and go to http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)