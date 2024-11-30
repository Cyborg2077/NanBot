import uvicorn
from fastapi import FastAPI
from app.routes import router
from app.config import load_config
from app.llm import init_llm

from app.config import setup_logging

setup_logging()  # 设置日志

config = load_config()
llm = init_llm(api_key=config['openai']['api_key'])

app = FastAPI()
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
