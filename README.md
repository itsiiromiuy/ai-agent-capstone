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

## Installation and Setup

1. Create a requirements.txt file in your project directory:
```bash
cat > requirements.txt << EOF
fastapi==0.108.0
uvicorn==0.23.2
langchain==0.1.10
langchain_core==0.1.28
langchain_community==0.0.25
langchain-google-genai
google-generativeai
redis
qdrant-client==1.7.1
httpx
websockets
pydantic>=2.0.0
python-dotenv
google-api-python-client
google-auth
google-auth-oauthlib
google-auth-httplib2
EOF
```

2. Install the dependencies using Pipenv:
```bash
pipenv install -r requirements.txt
```

3. Run the server:
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

4. For API documentation, run:
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