import logging
from app.dependencies import deps
from app.config import get_user_config

logger = logging.getLogger(__name__)


def llm_answer(qq: str) -> str:
    context = "\n".join([f"{msg['user']}:{msg['message']}" for msg in deps.msg_cache.get(qq)])
    user_config = get_user_config(qq)
    prompt = user_config['prompt']
    name = user_config['name']

    formatted_prompt = f"""{prompt}
    请注意，你的回答应该由多条简短的独立的消息组成，每条消息之间使用换行符（\\n）分隔。确保每条消息都是一条完整的句子或段落。当你接收到多条消息时，若多条消息表达的意思相近，不必逐一回复"""

    completion = deps.llm_client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                'role': 'system',
                'content': formatted_prompt
            },
            {
                'role': 'user',
                'content': f"{name}向你发送了消息，\n当前上下文：\n{context}"
            }
        ]
    )
    logger.info(
        f'prompt:{formatted_prompt}, content:{name}向你发送了消息，\n当前上下文：\n{context},llm answer:{completion.choices[0].message.content}')
    return completion.choices[0].message.content


def llm_received_delay_msg(qq):
    user_config = get_user_config(qq)
    prompt = user_config['prompt']
    name = user_config['name']
    context = "\n".join([f"{msg['user']}:{msg['message']}" for msg in deps.msg_cache.get(qq)])

    # 修改为更加自然、友好的提示词
    new_prompt = f"""
    我已经将这条消息加入到了延迟队列中，所以你此时需要温馨的提示她，我已经收到你的xxx消息啦，并且会再xxx时间后提醒你的哦。
    """

    completion = deps.llm_client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                'role': 'system',
                'content': prompt + new_prompt
            },
            {
                'role': 'user',
                'content': f"{name}向你发送了消息。\n当前上下文：\n{context}"
            }
        ]
    )
    response_content = completion.choices[0].message.content
    logger.info(f'LLM Response: {response_content}')
    return response_content


def llm_answer_delay_msg(qq, question):
    user_config = get_user_config(qq)
    # 将上下文整理为字符串
    prompt = user_config['prompt']
    name = user_config['name']
    context = "\n".join([f"{msg['user']}:{msg['message']}" for msg in deps.msg_cache.get(qq)])
    # 构造提示词，明确表示消息是延迟���列中的任务，且需要提醒
    delay_msg_prompt = (
        f"这是一条来自延迟队列的消息。你回答的时候要说类似，已经到了xxx时间啦...，现在应该去xxx啦。这种的话，但是不要太生硬。\n"
        f"请生成一个友好且礼貌的提醒回复，提示对方有一个需要关注的任务：\n"
        f"目标对象：{name}"
        f"任务详情：{question}\n"
        f"当前上下文：{context}"
    )

    completion = deps.llm_client.chat.completions.create(
        model="qwen-max",  # 使用你指定的模型
        messages=[
            {
                'role': 'system',
                'content': prompt
            },
            {
                'role': 'user',
                'content': delay_msg_prompt
            }
        ]
    )

    response_content = completion.choices[0].message.content
    logger.info(f'LLM Delay Message Response: {response_content}')
    return response_content
