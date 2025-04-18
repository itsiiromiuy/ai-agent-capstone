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
from langchain.schema.output_parser import StrOutputParser
from .naming_master_prompt import SYSTEM_PROMPT
import json
import re

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

    def emotion_detection_chain(self, query: str):
        """
        Analyze the emotional content of user queries to enhance response quality.

        This method detects emotions, sentiment, and communication style to help
        the AI generate more appropriate and empathetic responses.

        Args:
            query (str): The user's input text

        Returns:
            dict: Emotional analysis with detected emotions, sentiment score, and response guidance
        """
        prompt = """
        As an emotional intelligence expert, analyze the following text and identify:
        
        1. Primary emotion (select one): anger, joy, sadness, fear, surprise, disgust, confusion, curiosity, neutral
        2. Emotional intensity (scale 1-5)
        3. Sentiment (positive, negative, or neutral)
        4. Communication style (formal, casual, urgent, analytical, vulnerable)
        5. Best tone for response (empathetic, enthusiastic, reassuring, factual, curious, formal, casual)
        
        Text to analyze: {query}
        
        Format your response as a structured JSON object with the following keys:
        - primary_emotion
        - intensity
        - sentiment
        - communication_style
        - response_tone
        - explanation (brief justification of your analysis)
        """

        # Create the chain
        chain = ChatPromptTemplate.from_template(
            prompt) | self.chatmodel | StrOutputParser()

        # Invoke the chain
        result = chain.invoke({"query": query})

        try:
            # Clean the result if it contains markdown or other formatting
            if "```json" in result:
                match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
                if match:
                    result = match.group(1)
            elif "```" in result:
                match = re.search(r'```\s*(.*?)\s*```', result, re.DOTALL)
                if match:
                    result = match.group(1)

            # Parse the JSON
            emotion_data = json.loads(result)
            return emotion_data

        except Exception as e:
            # Return a basic result if parsing fails
            return {
                "primary_emotion": "neutral",
                "intensity": 3,
                "sentiment": "neutral",
                "communication_style": "casual",
                "response_tone": "factual",
                "explanation": "Failed to parse emotional content",
                "error": str(e)
            }

    # Create a simple chain
    # self.chain = self.prompt | self.chatmodel | (lambda x: x.content)

    def generate_emotion_aware_response(self, query: str) -> dict:
        """
        Generate a response that takes into account the emotional context of the query.

        Args:
            query (str): The user's input text

        Returns:
            dict: Response with emotion analysis and message
        """
        # Analyze emotional content
        emotion_data = self.emotion_detection_chain(query)

        # Create an emotion-aware prompt
        emotion_context = f"""
        The user's message shows these emotional characteristics:
        - Primary emotion: {emotion_data['primary_emotion']}
        - Emotional intensity: {emotion_data['intensity']}/5
        - Sentiment: {emotion_data['sentiment']}
        - Communication style: {emotion_data['communication_style']}
        
        When responding, use a {emotion_data['response_tone']} tone.
        """

        # Create a temporary conversation with emotion-aware context
        emotion_aware_prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEMPL + "\n\n" + emotion_context),
            MessagesPlaceholder(variable_name=self.MEMORY_KEY),
            ("human", "{input}")
        ])

        emotion_aware_conversation = ConversationChain(
            llm=self.chatmodel,
            memory=self.memory,
            prompt=emotion_aware_prompt,
            verbose=True
        )

        # Generate response
        try:
            response = emotion_aware_conversation.invoke({"input": query})

            if isinstance(response, dict) and 'output' in response:
                message = response['output']
            else:
                message = str(response)

            return {
                "message": message,
                "emotion_analysis": emotion_data
            }
        except Exception as e:
            # Fallback to regular conversation
            regular_response = self.run(query)
            return {
                "message": regular_response,
                "emotion_analysis": emotion_data,
                "error": str(e)
            }

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


# API Endpoints
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


@app.websocket("/ws/emotion")
async def emotion_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for emotion-aware chat"""
    await websocket.accept()
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"Received: {data}")

            # Process with emotion-aware AI agent
            response = ai_agent.generate_emotion_aware_response(data)

            # Send response back to client
            await websocket.send_json(response)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()
