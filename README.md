# Multi-Agent Knowledge Assistant: A LangGraph-based RAG System

## Google Gen AI Intensive Course Capstone Project 2025Q1

![Project Banner](https://i.imgur.com/placeholder.png)

## Overview

This project demonstrates an intelligent multi-agent system that combines vector search, retrieval-augmented generation (RAG), and agent-based architecture to create a powerful knowledge assistant. The system employs a supervisor agent to orchestrate specialized agents, each with specific roles, to efficiently process user queries and manage knowledge.

### Key Features

- **Supervisor-based Multi-Agent Coordination**: Intelligent task routing between specialized agents
- **Local Vector Database**: Semantic storage and retrieval of information using ChromaDB
- **Web Search Augmentation**: Finding information beyond the local knowledge base
- **Knowledge Management**: Adding content from websites, PDFs, and raw text
- **Real-time Interaction**: Both command-line and API interfaces with WebSocket support

## Gen AI Capabilities Demonstrated

This project showcases **six** Gen AI capabilities (exceeding the minimum requirement of three):

1. **Agents**: Implementation of a supervisor agent coordinating specialized worker agents
2. **Function Calling**: LLM-powered tools for specific tasks like web search and knowledge base management
3. **Retrieval Augmented Generation (RAG)**: Enhancing responses with information from a vector database
4. **Vector Search/Vector Store**: Local ChromaDB implementation for semantic document retrieval
5. **Structured Output/JSON mode**: Controlled generation for agent communication protocol
6. **Embeddings**: Semantic understanding of documents using HuggingFace embeddings

## System Architecture

![System Architecture](https://i.imgur.com/placeholder2.png)

The system follows a LangGraph-based flow:

1. **Supervisor Agent**: Determines which specialized agent should handle a user query
2. **Research Agent**: Retrieves information from the vector database or web
3. **Knowledge Agent**: Manages the knowledge base by adding new information from various sources
4. **Communication Agent**: Presents results to the user in a coherent manner

## Use Case

This system addresses the challenge of information overload by creating a personal knowledge assistant that can:

- Answer questions using previously stored knowledge
- Search the web when information isn't available locally
- Learn from new information sources like websites, documents, and user inputs
- Maintain context and coherence throughout conversations

This makes it ideal for researchers, students, content creators, or anyone who needs to organize and retrieve information efficiently.

## Implementation Details

### Technology Stack

- **LangGraph**: Agent workflow and state management
- **LangChain**: Agent creation and tool calling
- **Google Vertex AI (Gemini)**: Base LLM for all agents
- **ChromaDB**: Vector storage for semantic search
- **HuggingFace**: Sentence transformers for embeddings
- **FastAPI**: API and WebSocket server

### Key Components

- **capstone_langgraph.py**: Core multi-agent system implementation
- **example_usage.py**: Command-line interface for interacting with the system
- **api_server.py**: FastAPI server for programmatic access and WebSocket support

## Getting Started

### Prerequisites

- Python 3.9+
- Google Vertex AI API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multi-agent-knowledge-assistant.git
   cd multi-agent-knowledge-assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements_langgraph.txt
   ```

3. Set up your environment variables:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

### Running the Application

#### Command Line Interface

```bash
python example_usage.py
```

#### API Server

```bash
python api_server.py
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## Example Usage

### Adding Knowledge

```
Enter your query: Add this website to your knowledge base: https://www.kaggle.com/competitions/gen-ai-intensive-course-capstone-2025q1
```

### Querying Knowledge

```
Enter your query: What information do you have about the Kaggle Gen AI Intensive Course?
```

### Combining Knowledge and Web Search

```
Enter your query: What's the latest research on multi-agent systems? Compare with what you know.
```

## Limitations and Future Improvements

- **Streaming Responses**: Add token-by-token streaming for more responsive user experience
- **Improved Memory Management**: Implement more sophisticated memory systems for longer conversations
- **Enhanced Web Search**: Integrate with more comprehensive search APIs
- **Multi-modal Support**: Extend to understand images and other data types
- **Collaborative Learning**: Allow the system to learn from multiple users' interactions

## Conclusion

This project demonstrates how modern LLM capabilities can be combined with agent-based architectures to create powerful knowledge management systems. By leveraging specialized agents, vector search, and RAG, we've created a system that can efficiently manage, retrieve, and communicate information to users.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gen AI Intensive Course for the inspiration and knowledge
- The LangChain and LangGraph teams for their excellent frameworks
- Kaggle for hosting the capstone competition

# redis server
- clean redis server: `docker stop redis-stack`
- clean redis content: `redis-cli flushall`
- start redis server: `docker start redis-stack`
- If you don't have it running yet, you might need to create it first, as mentioned in your README:
`docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest`
- You can check if Redis is running by using: `docker ps | grep redis`
- Or try connecting to it directly: `docker exec -it redis-stack redis-cli ping`