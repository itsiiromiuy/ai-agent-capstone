import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate

class CommaSeperatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str) -> list[str]:
        """Parse the output of an LLM call."""
        return text.strip().split(",")
    
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

app = FastAPI() 

class MeimeiShi:
    def __init__(self):
        self.chatmodel = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            temperature=0,
            streaming=True,
        )
        self.MEMORY_KEY = "chat_history"
        self.SYSTEMPL = ""
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                "system",
                "you are a helpful assistant",
                ),
                ("user", "{input}"),
            ]
        )
        self.memory = ""
        self.agent = create_react_agent(
            llm=self.chatmodel,
            tools=[],
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )
        self.agent_executor = AgentExecutor(agent=self.agent, tools=[], verbose=True)
    def run(self, query):
        result = self.agent_executor.invoke({"input": query})
        return self.agent_executor.get_response(result)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/chat")
def chat():
    return {"message": "I am a chatbot"}

@app.post("/add_urls")
def add_urls():
    return {"message": "URLs added"}

@app.post("/add_pdfs")
def add_pdfs():
    return {"message": "PDFs added"}

@app.post("/add_texts")
def add_texts():
    return {"message": "Texts added"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run(app, host="0.0.0.0", port=8000)