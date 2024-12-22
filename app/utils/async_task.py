from asyncio import create_task, sleep
from venv import logger

from app.config import CONFIG
from app.messaging import send_message
from app.utils.msgcache import msg_cache
from app.llm import llm_answer, LLM_CLIENT

writing_status = {}

import asyncio
import websockets
import json


async def websocket_client():
    uri = "ws://localhost:8080/ws"  # 修改为你的 WebSocket 服务地址
    async with websockets.connect(uri) as websocket:
        # 发送一个测试消息
        message = {
            "user_id": 123456,
            "raw_message": "提醒我十分钟后去洗澡"
        }
        await websocket.send(json.dumps(message))

        # 接收响应
        response = await websocket.recv()
        print(f"Received: {response}")


asyncio.get_event_loop().run_until_complete(websocket_client())
