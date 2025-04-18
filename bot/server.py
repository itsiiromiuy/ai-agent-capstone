import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from bot.naming_master_prompt import SYSTEM_PROMPT

load_dotenv()
app = FastAPI(title="Meimei Shi AI Chat API")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


def load_system_prompt(file_path="naming_master_prompt.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


class CommaSeperatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str) -> list[str]:
        """Parse the output of an LLM call."""
        return text.strip().split(",")


class MeimeiShi:
    """AI chat agent using Google Generative AI"""

    def __init__(self):
        """Initialize the AI chat agent with Google Generative AI"""
        # Use the imported prompt instead of defining it inline
        self.SYSTEMPL = SYSTEM_PROMPT

        # Initialize the chat model with the system prompt
        self.chatmodel = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0.7,
            streaming=True,
            google_api_key=api_key,
            system=self.SYSTEMPL
        )

        # Create a simple prompt for direct interactions
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEMPL),
            ("human", "{input}")
        ])
        # Set up memory if needed
        self.MEMORY_KEY = "chat_history"
        self.memory = ConversationBufferMemory(
            memory_key=self.MEMORY_KEY, return_messages=True)

        # Create the conversation chain with memory
        self.conversation = ConversationChain(
            llm=self.chatmodel,
            memory=self.memory,
            prompt=ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(self.SYSTEMPL),
                MessagesPlaceholder(variable_name=self.MEMORY_KEY),
                HumanMessagePromptTemplate.from_template("{input}")
            ]),
            verbose=True
        )

        # Create a simple chain
        self.chain = self.prompt | self.chatmodel | (lambda x: x.content)

    def run(self, query: str) -> str:
        """Process user query and return response"""
        try:
            # Use the conversation chain to maintain history
            response = self.conversation.invoke({"input": query})

            # Extract the string content from the response
            # The response from ConversationChain is a dictionary with an 'output' key
            if isinstance(response, dict) and 'output' in response:
                return response['output']
            elif hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                # If we can't extract content in a known way, convert to string
                return str(response)
        except Exception as e:
            return f"Error processing your request: {str(e)}"


# Create a singleton instance of the agent
ai_agent = MeimeiShi()


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "MeimeiShi AI Chat API",
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
