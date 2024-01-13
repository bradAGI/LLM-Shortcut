import os
import sys
import uuid

import llm
from fastapi import FastAPI
from pydantic_settings import BaseSettings
from pyngrok import ngrok


class Settings(BaseSettings):
    USE_NGROK: bool = True
    BASE_URL: str = "http://localhost:8000"
    NGROK_AUTHTOKEN: str
    LLM_ANYSCALE_ENDPOINTS_KEY: str
    MODEL: str
    MAX_TOKENS: int = 100


settings = Settings(_env_file='.env')
app = FastAPI()
key = uuid.uuid4().hex

print("\nThe following models are available:")
print('\n'.join(l.split(':', 1)[1].strip() for l in os.popen('llm models').read().splitlines() if ':' in l))


@app.on_event("startup")
async def startup_event():
    if settings.USE_NGROK:
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8000"
        ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
        public_url = ngrok.connect(port).public_url
        print("NGROK URL: ", public_url, flush=True)
        print("API KEY: ", key, flush=True)
        settings.BASE_URL = public_url


@app.get("/{key}/{prompt}")
async def get_answer(key: str, prompt: str):
    if key != str(key):
        return "Invalid key"
    prompt = prompt.replace("_", " ")
    system = "You are a helpful chatbot."
    return await get_response(prompt, system)


async def get_response(prompt, system):
    model = llm.get_model(settings.MODEL)
    model.key = settings.LLM_ANYSCALE_ENDPOINTS_KEY
    return model.prompt(system, prompt, max_tokens=settings.MAX_TOKENS).text().strip()
