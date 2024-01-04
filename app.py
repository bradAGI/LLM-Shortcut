import os
import sys

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


@app.on_event("startup")
async def startup_event():
    if settings.USE_NGROK:
        # Extract the port number. Use 8000 as default if not specified.
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8000"
        # Set ngrok authtoken from settings
        ngrok.set_auth_token(settings.NGROK_AUTHTOKEN)
        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        print(f"NGROK URL: \"{public_url}\" ", flush=True)
        # Update the base URL to use the public ngrok URL
        settings.BASE_URL = public_url


@app.get("/llm/{prompt}")
async def get_answer(prompt: str):
    prompt = prompt.replace("_", " ")
    system = "You are a helpful chatbot."
    return await get_response(prompt, system)


async def get_response(prompt, system):
    print(os.system("llm models"))
    model = llm.get_model(settings.MODEL)
    model.key = settings.LLM_ANYSCALE_ENDPOINTS_KEY
    return model.prompt(system, prompt, max_tokens=settings.MAX_TOKENS).text().strip()
