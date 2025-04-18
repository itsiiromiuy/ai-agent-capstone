import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Initialize FastAPI app
app = FastAPI(title="Meimei Shi AI Chat API")

class CommaSeperatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""
    
    def parse(self, text: str) -> list[str]:
        """Parse the output of an LLM call."""
        return text.strip().split(",")


class MeimeiShi:
    """AI chat agent using Google Generative AI"""
    
    def __init__(self):
        """Initialize the AI chat agent with Google Generative AI"""
        self.chatmodel = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            temperature=0,
            streaming=True,
            google_api_key=api_key
        )
        
        # Create a simple chain instead of using ReAct agent
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant named Meimei Shi. You provide concise, accurate, and helpful responses."),
            ("user", "{input}")
        ])
        
        # Create a simple chain
        self.chain = self.prompt | self.chatmodel | (lambda x: x.content)
    
    def run(self, query: str) -> str:
        """Process user query and return response"""
        try:
            return self.chain.invoke({"input": query})
        except Exception as e:
            return f"Error processing your request: {str(e)}"


# Create a singleton instance of the agent
ai_agent = MeimeiShi()

@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "Meimei Shi AI Chat API", 
        "version": "1.0",
        "endpoints": ["/chat", "/ws", "/add_urls", "/add_pdfs", "/add_texts"]
    }

@app.post("/chat")
def chat(query: str) -> Dict[str, Any]:
    """Chat endpoint for text-based interaction"""
    response = ai_agent.run(query)
    return {"message": response}

@app.post("/add_urls")
def add_urls():
    """Endpoint to add URLs (placeholder)"""
    return {"message": "URLs added successfully"}

@app.post("/add_pdfs")
def add_pdfs():
    """Endpoint to add PDFs (placeholder)"""
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
            # Receive message from client
            data = await websocket.receive_text()
            print(f"Received: {data}")
            
            # Process with AI agent
            response = ai_agent.run(data)
            
            # Send response back to client
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)