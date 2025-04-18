#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langserve import add_routes
import os
from dotenv import load_dotenv

# Load environment variables for API key
load_dotenv()

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key),
    path="/gemini-pro",
)

add_routes(
    app,
    ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key),
    path="/gemini-flash",
)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", google_api_key=api_key)
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
add_routes(
    app,
    prompt | model,
    path="/joke",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
