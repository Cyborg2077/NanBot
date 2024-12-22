import asyncio
import json
import logging
import traceback
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, WebSocket, Request
from starlette.websockets import WebSocketDisconnect

from app.models.privatemsg import PrivateMsg, GroupMsg
from app.utils.delay_queue import delay_queue
from app.dependencies import deps
from app.function_call import function_definitions
from app.llm import llm_answer, llm_received_delay_msg
from app.messaging import send_message, get_friend_msg_history
from app.config import get_user_config

logger = logging.getLogger(__name__)

router = APIRouter()

# 存储每个用户（QQ）最后接收到消息的时间戳
last_message_time = defaultdict(lambda: datetime.min)

# 存储延迟回复的任务
response_tasks = {}


async def send_reply_after_delay(qq: str, msg: str):
    # await asyncio.sleep(5)  # 等待5秒
    # if datetime.now() - last_message_time[qq] >= timedelta(seconds=5):
    #     # 如果5秒内没有新消息
    #     # 生成并发送回复
    answer = llm_answer(qq)
    send_message(qq, answer)
    logger.info(f"对QQ {qq} 发送延迟回复: {answer}")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Bot connected!")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f'接收到ws消息：{data}')
            try:
                # 解析接收到的消息
                data = json.loads(data)
                if data['post_type'] == 'meta_event':
                    continue
                if data['message_type'] == 'group':
                    msg_obj = GroupMsg.parse_obj(data)
                    qq = msg_obj.group_id
                    deps.msg_cache.add(qq, msg_obj.raw_message)
                    if deps.msg_cache.is_last_two_message_equal(qq):
                        # send_message(qq, msg_obj.raw_message, False)
                        logger.info(f"在群:{qq}，发送了复读消息：{msg_obj.raw_message}")
                        return
                    continue

                msg_obj = PrivateMsg.parse_obj(data)
                qq = msg_obj.user_id
                logger.info(f"QQ:{qq}，Nickname -- {msg_obj.sender.nickname}：{msg_obj.raw_message}")

                user_config = get_user_config(qq)
                if not user_config:
                    continue  # 继续等待下一个消息
                else:
                    msg = msg_obj.raw_message
                    name = user_config['name']

                    # 加载历史消息
                    if qq not in deps.msg_cache.cache_data:
                        history_msg = get_friend_msg_history(qq)
                        if history_msg['status'] != 'failed':
                            for his_msg in history_msg['data']['messages']:
                                his_qq = his_msg['user_id']
                                tmp_user_cfg = get_user_config(his_qq)
                                tmp_name = tmp_user_cfg['name']
                                deps.msg_cache.add(qq, {"user": tmp_name, "message": his_msg['raw_message']})
                    else:
                        # 添加当前消息到缓存
                        deps.msg_cache.add(qq, {"user": name, "message": msg})

                    # 调用大模型解析消息
                    response = deps.llm_client.chat.completions.create(
                        model="qwen-max",
                        messages=[
                            {
                                "role": "system",
                                "content": "你是一位智能助手，帮助解析自然语言任务并添加到延迟队列，仅仅当明确出现时间并且需要判断是否有需要提醒的意愿时，才需要调用。例如：'十分钟后提醒我去洗澡'。"
                            },
                            {
                                "role": "user",
                                "content": f"接收到消息：{msg}"
                            }
                        ],
                        functions=function_definitions,
                        function_call="auto"  # 让模型决定是否调用功能
                    )

                    # 如果模型调用了 Function
                    if response.choices[0].message.function_call:
                        func_name = response.choices[0].message.function_call.name
                        arguments = json.loads(response.choices[0].message.function_call.arguments)

                        if func_name == "add_delay_task":
                            # 执行了 add_delay_task 方法
                            delay_queue.add_delay_task(qq, **arguments)
                            # 生成一个立即回复
                            answer = llm_received_delay_msg(qq)
                            send_message(qq, answer)
                            await websocket.send_text(json.dumps({"response": answer}))
                            continue  # 继续等待下一个消息

                    # 没有调用Function，生成普通回复
                    last_message_time[qq] = datetime.now()

                    # 如果该用户已有延迟任务，取消它（因为新消息到来了）
                    if qq in response_tasks:
                        response_tasks[qq].cancel()

                    # 启动一个新的延迟回复任务
                    response_tasks[qq] = asyncio.create_task(send_reply_after_delay(qq, msg))

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                logger.error(f"Stack trace: {traceback.format_exc()}")
                continue  # 继续等待下一个消息

    except WebSocketDisconnect:
        logger.info("Client disconnected.")
