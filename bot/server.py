from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
import pymupdf

import os
from typing import Any, Dict
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile
from langchain.agents import initialize_agent, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from langchain_google_vertexai import VertexAIEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from .naming_master_prompt import SYSTEM_PROMPT
from langgraph.checkpoint.redis import RedisSaver
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vertexai import init
from langchain_community.document_loaders import PyMuPDFLoader
import pymupdf4llm
from langchain.text_splitter import MarkdownTextSplitter

# Initialize with your correct project
init(project="ai-agent-capstone", location="us-central1")

logger = logging.getLogger(__name__)
LOCAL_QDRANT_PATH = "/Users/itsyuimorii/Documents/local_qdrant"

load_dotenv()
app = FastAPI(title="Meimei Shi AI Chat API")

# Load environment variables
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")


@tool
def search(query: str) -> str:
    """Use Google Search to find information related to the query."""
    search_tool = SerpAPIWrapper()
    return search_tool.run(query)


@tool
def get_info_from_local_db(query: str) -> str:
    """Use Qdrant to find information related to the query."""
    try:
        qdrant = Qdrant(
            QdrantClient(path=LOCAL_QDRANT_PATH),
            "local_documents",
            VertexAIEmbeddings(model="text-embedding-004")
        )
        results = qdrant.similarity_search(query, k=3)
        return "\n\n".join(doc.page_content for doc in results) if results else "No relevant information found."
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return f"Error accessing local database: {str(e)}"


def load_system_prompt(file_path="naming_master_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


class EmotionAnalysis(BaseModel):
    """Pydantic model for emotion analysis results"""
    primary_emotion: str
    intensity: int
    sentiment: str
    communication_style: str
    response_tone: str
    explanation: str


class MeimeiShi:
    """AI chat agent using Google Generative AI"""

    def __init__(self):
        """Initialize the AI chat agent with Google Generative AI"""
        # Use the imported prompt instead of defining it inline
        self.SYSTEMPL = SYSTEM_PROMPT

        # Initialize the chat model with the system prompt
        self.chatmodel = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0,
            google_api_key=api_key,
        )

        # Initialize the search tool
        self.tools = [search, get_info_from_local_db]
        self.chatmodel.bind_tools(self.tools)

        REDIS_URI = "redis://localhost:6379"

        with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
            checkpointer.setup()
            self.conversation = create_react_agent(
                model=self.chatmodel,
                tools=self.tools,
                prompt=self.SYSTEMPL,
                checkpointer=checkpointer
            )

    def emotion_detection_chain(self, query: str) -> Dict[str, Any]:
        """Analyze emotional content of text"""
        try:
            analysis = self.chatmodel.with_structured_output(EmotionAnalysis).invoke(
                f"Analyze this text: {query}"
            )
            return analysis.dict()
        except Exception as e:
            logger.error(f"Emotion analysis failed: {str(e)}")
            return self._default_emotion_analysis()

    def _default_emotion_analysis(self) -> Dict[str, Any]:
        """Fallback emotion analysis"""
        return {
            "primary_emotion": "neutral",
            "intensity": 3,
            "sentiment": "neutral",
            "communication_style": "casual",
            "response_tone": "factual",
            "explanation": "Default analysis used"
        }

    def generate_emotion_aware_response(self, query: str) -> Dict[str, Any]:
        """Generate response considering emotional context"""
        try:
            emotion_data = self.emotion_detection_chain(query)
            message = self.run(query)
            return {
                "message": message,
                "emotion_analysis": emotion_data
            }
        except Exception as e:
            logger.error(f"Emotion-aware response failed: {str(e)}")
            return {
                "message": "I encountered an error processing your request.",
                "emotion_analysis": self._default_emotion_analysis(),
                "error": str(e)
            }

    def run(self, query: str) -> str:
        """Process user query and return response"""
        try:
            formatted_input = {
                "messages": [{"role": "user", "content": query}]
            }
            config = {
                "configurable": {
                    "thread_id": "1",
                    "search_tool": any(
                        kw in query.lower()
                        for kw in ["current", "trending", "latest", "recent", "today"]
                    )
                }
            }
            response = self.conversation.invoke(formatted_input, config)
            return response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request."


ai_agent = MeimeiShi()


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "MeimeiShi AI Chat API",
        "version": "1.0",
        "endpoints": ["/chat", "/emotion_chat", "/analyze_emotion", "/ws", "/add_urls", "/add_pdfs", "/add_texts"]
    }


@app.post("/chat")
def chat(query: str) -> Dict[str, Any]:
    """Chat endpoint for text-based interaction"""
    response = ai_agent.run(query)
    return {"message": response}


@app.post("/emotion_chat")
def emotion_chat(query: str) -> Dict[str, Any]:
    """Chat endpoint with emotional intelligence"""
    response = ai_agent.generate_emotion_aware_response(query)
    return response


@app.post("/analyze_emotion")
def analyze_emotion(query: str) -> Dict[str, Any]:
    """Analyze the emotional content of text"""
    emotion_data = ai_agent.emotion_detection_chain(query)
    return emotion_data


@app.post("/add_urls")
def add_urls(url: str):
    """Learning knowledge from URLs and storing it in vector databases"""
    loader = WebBaseLoader(url)
    documents = loader.load()

    document_chunks = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=50).split_documents(documents)

    qdrantDB = Qdrant.from_documents(
        document_chunks,
        VertexAIEmbeddings(model_name="text-embedding-004"),
        path=LOCAL_QDRANT_PATH,
        collection_name="local_documents"
    )
    return {"message": "Successfully learned text blocks from url"}


@app.post("/add_pdfs")
def add_pdfs(file: UploadFile):
    """Endpoint to add PDFs (placeholder)"""
    document = pymupdf.open(stream=file.file.read())
    md_text = pymupdf4llm.to_markdown(document)

    splitter = MarkdownTextSplitter(
        chunk_size=40,
        chunk_overlap=0,
    )

    document_chunks = splitter.create_documents([md_text])

    if not document_chunks:
        return {"message": "No text was found in the uploaded PDF"}

    qdrantDB = Qdrant.from_documents(
        document_chunks,
        VertexAIEmbeddings(model_name="text-embedding-004"),
        path=LOCAL_QDRANT_PATH,
        collection_name="local_documents"
    )

    return {"message": "PDFs added successfully"}


@app.post("/add_texts")
def add_texts():
    """Endpoint to add texts (placeholder)"""
    return {"message": "Texts added successfully"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            response = ai_agent.run(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@app.websocket("/ws/emotion")
async def emotion_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for emotion-aware chat"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received emotion message: {data}")
            response = ai_agent.generate_emotion_aware_response(data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()
