import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
root_dir = Path(__file__).resolve().parent
sys.path.append(str(root_dir))

import uvicorn
from fastapi import FastAPI
from app.routes import router
from app.dependencies import deps
from app.config import setup_logging

setup_logging()

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    deps.initialize()


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
