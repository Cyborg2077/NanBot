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


@app.post("/")
async def root(request: Request):
    data = await request.json()
    try:
        msg_obj = Msg.parse_obj(data)
        qq = msg_obj.user_id
        logger.info(f"QQ:{qq}，Nickname -- {msg_obj.sender.nickname}：{msg_obj.raw_message}")
        if qq == config['girl_friend']['qq']:
            logger.info("Received a message from girl friend")
            answer = llm_answer(msg_obj.raw_message, llm, config['girl_friend']['system_prompt'])
            send_message(qq, answer)

    except Exception:
        logger.error(f"data parse error:{data}")


def llm_answer(question, client, prompt):
    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                'role': 'system',
                'content': prompt
            },
            {'role': 'user', 'content': '楠楠对你说：' + question}
        ]
    )
    content = completion.choices[0].message.content
    logging.info(f'LLM Response:：{content}')
    return content


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
