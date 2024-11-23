from collections import deque

import uvicorn
import logging
import requests
import json

import yaml
from fastapi import FastAPI, Request
from openai import OpenAI

from models import Msg

from logging_config import setup_logging

setup_logging()  # 设置日志
logger = logging.getLogger(__name__)


def load_config():
    with open(r"config.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def init_llm(api_key):
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    return client


app = FastAPI()

config = load_config()
llm = init_llm(api_key=config['openai']['api_key'])

message_queue_cache = {}
MAX_QUEUE_SIZE = config['girl_friend']['max_queue_size']


@app.post("/")
async def root(request: Request):
    data = await request.json()
    try:
        msg_obj = Msg.parse_obj(data)
        qq = msg_obj.user_id
        logger.info(f"QQ:{qq}，Nickname -- {msg_obj.sender.nickname}：{msg_obj.raw_message}")
        if qq == config['girl_friend']['qq']:
            msg = msg_obj.raw_message
            if qq not in message_queue_cache:
                message_queue_cache[qq] = deque(maxlen=MAX_QUEUE_SIZE)
            message_queue_cache[qq].append({"type": "user", "message": msg})
            answer = llm_answer(msg, list(message_queue_cache[qq]), llm, config['girl_friend']['system_prompt'],
                                config['girl_friend']['name'])
            message_queue_cache[qq].append({"type": "llm", "message": answer})
            send_message(qq, answer)
            logger.info(f"Queue for {qq}: cache message:{list(message_queue_cache[qq])}")
    except Exception:
        logger.error(f"data parse error:{data}")


def llm_answer(question, content, client, prompt, name):
    # 将上下文整理为字符串
    context = "\n".join([f"{msg['type']}:{msg['message']}" for msg in content])

    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                'role': 'system',
                'content': prompt
            },
            {
                'role': 'user',
                'content': f"{name}对你说：{question}。\n当前上下文：\n{context}"
            }
        ]
    )
    response_content = completion.choices[0].message.content
    logging.info(f'LLM Response: {response_content}')
    return response_content


def send_message(qq, message):
    url = config['send_msg_url']
    data = {
        "user_id": qq,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": message
                }
            }
        ]
    }
    response = requests.post(url, data=json.dumps(data))
    logger.info(f"send message to {qq} result:{response.text}")


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
