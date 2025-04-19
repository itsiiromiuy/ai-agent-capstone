# AI Agent Capstone Project

A versatile AI agent that integrates with multiple platforms through LangChain, supporting various interfaces and learning capabilities.

## Project Architecture

### Server Side
- Interfaces with LangChain → OpenAI/Ollama

### Client Side
- Telegram bot
- WeChat bot
- Website

### Interfaces
- HTTP
- HTTPS
- WebSocket

### Server
- Interface access using FastAPI (Python)
- `/chat` endpoint
- `/add_urls` endpoint for learning from URLs
- `/add_pdfs` endpoint for learning from PDFs
- `/add_texts` endpoint for learning from text

### Emotion Detection Pipeline
- User Input → Emotion Analysis → Response Selection → Personalized Output

## Installation and Setup
1. How to install dependencies
Simply use `pipenv sync` to install dependencies.
if you don't use pipenv, you prefer to manage your `env` differently, you can use provided `requirements.txt` instead. (e.g., `pip install -r requirements.txt`)

For development purposes, to generate this file use the following command
```bash
pipenv requirements > requirements.txt
```

2. Run the server:
```bash
pipenv run python server.py
```

You should see output similar to:
```
INFO: Started server process [17047]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO: 127.0.0.1:59135 - "GET / HTTP/1.1" 200 OK
INFO: 127.0.0.1:59135 - "GET /favicon.ico HTTP/1.1" 404 Not Found
```

3. For API documentation, run:
```bash
pipenv run uvicorn bot.server:app --reload
```
Then visit http://localhost:8000/docs to view the interactive API documentation.

## Features

- Multi-platform integration (Telegram, WeChat, Web)
- Learning capabilities from different sources (URLs, PDFs, text)
- Real-time communication through WebSockets
- Extensible architecture based on LangChain

## Requirements

- Python 3.8+
- Pipenv
- API keys for selected LLM providers (OpenAI/Google)


 

# Capstone Project: Gen AI Architecture

## Server-Side Packages

### Core Frameworks
```
fastapi==0.108.0          # Web API framework
uvicorn==0.23.2           # ASGI server
langchain==0.1.10         # LLM application framework
langchain_core==0.1.28    # LangChain core components
langchain_community==0.0.25  # Community components
langchain_openai==0.0.5   # OpenAI integration
```

### Data Storage & Vector Database
```
redis                     # Caching and vector storage
qdrant_client==1.7.1      # Vector database client
```

### API Integration & Tools
```
httpx                     # Asynchronous HTTP client
websockets                # WebSocket support
pydantic>=2.0.0           # Data validation
python-dotenv             # Environment variable management
```

### Ollama Integration
```
langchain_ollama          # Ollama model integration
```

### Google API Integration
```
google-api-python-client  # Google API client
google-auth               # Google authentication
google-auth-oauthlib      # OAuth authentication
google-auth-httplib2      # HTTP auth client
```

## Client-Side Packages

### Discord Bot
```
discord.py                # Discord bot API
```

### Chatbot Interface
```
streamlit                 # Simple web interface builder
gradio                    # AI application interface builder
```

## Ollama Models with Google API Integration

Ollama runs models locally, so integrating with Google APIs requires some middleware. Here are implementation approaches:

### Approach 1: Using LangChain to Integrate Google API with Ollama
```python
from langchain_ollama import Ollama
from langchain.agents import tool
from googleapiclient.discovery import build

# Set up Google API
google_api_key = "YOUR_API_KEY"
google_cse_id = "YOUR_CSE_ID"  # Custom Search Engine ID

# Create Google search tool
@tool
def google_search(query: str) -> str:
    """Search Google for relevant information"""
    service = build("customsearch", "v1", developerKey=google_api_key)
    result = service.cse().list(q=query, cx=google_cse_id).execute()
    return str(result['items'])

# Initialize Ollama model
ollama_model = Ollama(model="llama3")

# Integrate with LangChain Agent
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that can use tools"),
    ("human", "{input}"),
])

agent = create_react_agent(ollama_model, [google_search], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[google_search])
```

### Approach 2: Recommended Ollama Models

The following Ollama models work well with Google API integration:

1. **llama3** - Meta's latest model with strong general comprehension
2. **mistral** - Good for various tasks, especially understanding and generation
3. **phi3** - Microsoft's lightweight model for resource-constrained environments
4. **gemma** - Google's open-source model with good compatibility with Google APIs

## Implementation Suggestions

1. First, build the basic FastAPI server framework
2. Integrate Ollama models
3. Add Google API functionality (search, translation, etc.)
4. Implement vector storage and retrieval
5. Add agent capabilities
6. Finally, develop the client-side interfaces


Server-Side Architecture
```
Client Requests (HTTP/WebSocket) → FastAPI → LangChain → Ollama
                                     ↑
                                     ↓
                              Vector Database/Redis
```


# Capstone Project: Gen AI Architecture

## Server-Side Packages

### Core Frameworks
```
fastapi==0.108.0          # Web API framework
uvicorn==0.23.2           # ASGI server
langchain==0.1.10         # LLM application framework
langchain_core==0.1.28    # LangChain core components
langchain_community==0.0.25  # Community components
langchain_openai==0.0.5   # OpenAI integration
```

### Data Storage & Vector Database
```
redis                     # Caching and vector storage
qdrant_client==1.7.1      # Vector database client
```

### API Integration & Tools
```
httpx                     # Asynchronous HTTP client
websockets                # WebSocket support
pydantic>=2.0.0           # Data validation
python-dotenv             # Environment variable management
```

### Ollama Integration
```
langchain_ollama          # Ollama model integration
```

### Google API Integration
```
google-api-python-client  # Google API client
google-auth               # Google authentication
google-auth-oauthlib      # OAuth authentication
google-auth-httplib2      # HTTP auth client
```

## Client-Side Packages

### Discord Bot
```
discord.py                # Discord bot API
```

### Chatbot Interface
```
streamlit                 # Simple web interface builder
gradio                    # AI application interface builder
```

## Ollama Models with Google API Integration

Ollama runs models locally, so integrating with Google APIs requires some middleware. Here are implementation approaches:

### Approach 1: Using LangChain to Integrate Google API with Ollama
```python
from langchain_ollama import Ollama
from langchain.agents import tool
from googleapiclient.discovery import build

# Set up Google API
google_api_key = "YOUR_API_KEY"
google_cse_id = "YOUR_CSE_ID"  # Custom Search Engine ID

# Create Google search tool
@tool
def google_search(query: str) -> str:
    """Search Google for relevant information"""
    service = build("customsearch", "v1", developerKey=google_api_key)
    result = service.cse().list(q=query, cx=google_cse_id).execute()
    return str(result['items'])

# Initialize Ollama model
ollama_model = Ollama(model="llama3")

# Integrate with LangChain Agent
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that can use tools"),
    ("human", "{input}"),
])

agent = create_react_agent(ollama_model, [google_search], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[google_search])
```

### Approach 2: Recommended Ollama Models

The following Ollama models work well with Google API integration:

1. **llama3** - Meta's latest model with strong general comprehension
2. **mistral** - Good for various tasks, especially understanding and generation
3. **phi3** - Microsoft's lightweight model for resource-constrained environments
4. **gemma** - Google's open-source model with good compatibility with Google APIs

## Implementation Suggestions

1. First, build the basic FastAPI server framework
2. Integrate Ollama models
3. Add Google API functionality (search, translation, etc.)
4. Implement vector storage and retrieval
5. Add agent capabilities
6. Finally, develop the client-side interfaces


Server-Side Architecture
```
Client Requests (HTTP/WebSocket) → FastAPI → LangChain → Ollama
                                     ↑
                                     ↓
                              Vector Database/Redis
```


 