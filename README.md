# ai-agent-capstone
 
1. create a requirements.txt file in your project directory:
```
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

2. install the dependencies using Pipenv:
```
pipenv install -r requirements.txt
```

3. run the server:
```
pipenv run python server.py
```
```
INFO:     Started server process [17047]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:59135 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:59135 - "GET /favicon.ico HTTP/1.1" 404 Not Found
```

4. document the api:
```
pipenv run uvicorn bot.server:app --reload
```

    