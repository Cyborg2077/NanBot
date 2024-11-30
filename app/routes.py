import json
import logging
import traceback
from collections import deque

from fastapi import APIRouter, Request

from models.msg import Msg
from .config import load_config
from .delay_queue import DelayQueue
from .function_call import function_definitions
from .llm import LLM_CLIENT, init_llm, llm_received_delay_msg, llm_multi_answer
from .messaging import send_message, send_multi_message

logger = logging.getLogger(__name__)

router = APIRouter()

config = load_config()  # 直接加载配置
llm = init_llm(config['openai']['api_key'])
delay_queue = DelayQueue()
delay_queue.start_worker()


def init_message_cache(max_queue_size):
    return {}, max_queue_size


message_queue_cache, MAX_QUEUE_SIZE = {}, 100


@router.post("/")
async def root(request: Request):
    data = await request.json()
    try:
        msg_obj = Msg.parse_obj(data)
        qq = msg_obj.user_id
        logger.info(f"QQ:{qq}，Nickname -- {msg_obj.sender.nickname}：{msg_obj.raw_message}")
        if qq not in message_queue_cache:
            message_queue_cache[qq] = deque(maxlen=MAX_QUEUE_SIZE)
        if qq == config['girl_friend']['qq']:
            if qq not in message_queue_cache:
                message_queue_cache[qq] = deque(maxlen=MAX_QUEUE_SIZE)
            msg = msg_obj.raw_message
            message_queue_cache[qq].append({"type": "user", "message": msg})

            # 调用大模型解析消息
            response = LLM_CLIENT.chat.completions.create(
                model="qwen-max",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位智能助手，帮助解析自然语言任务并添加到延迟队列，仅仅当明确出现时间并且需要判断是否有需要提醒的意愿时，才需要调用。例如：‘十分钟后提醒我去洗澡’。"
                    },
                    {
                        "role": "user",
                        "content": f"女朋友说：{msg}"
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
                    delay_queue.add_delay_task(**arguments)
                    # 生成一个立即回复
                    answer = llm_received_delay_msg(msg, list(message_queue_cache[qq]), llm,
                                        config['girl_friend']['system_prompt'],
                                        config['girl_friend']['name'])
                    message_queue_cache[qq].append({"type": "llm", "message": answer})
                    send_message(qq, answer, config['send_msg_url'])
                    return
            # 没有调用Function，生成普通回复
            answer = llm_multi_answer(msg, list(message_queue_cache[qq]), llm,
                                config['girl_friend']['system_prompt'],
                                config['girl_friend']['name'])
            message_queue_cache[qq].append({"type": "llm", "message": answer})
            send_multi_message(qq, answer, config['send_msg_url'])
            logger.info(f"Queue for {qq}: cache message:{list(message_queue_cache[qq])}")
    except Exception as e:
        logger.error(f"data parse error:{data}, error: {e}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
