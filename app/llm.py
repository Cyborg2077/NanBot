from openai import OpenAI
import logging

logger = logging.getLogger(__name__)
LLM_CLIENT = None


def init_llm(api_key):
    global LLM_CLIENT
    if LLM_CLIENT is None:
        LLM_CLIENT = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    return LLM_CLIENT


def llm_answer(question, content, client, prompt, name):
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
    logger.info(f'LLM Response: {response_content}')
    return response_content


def llm_received_delay_msg(question, content, client, prompt, name):
    context = "\n".join([f"{msg['type']}:{msg['message']}" for msg in content])

    # 修改为更加自然、友好的提示词
    new_prompt = f"""
    我已经将这条消息加入到了延迟队列中，所以你此时需要温馨的提示她，我已经收到你的xxx消息啦，并且会再xxx时间后提醒你的哦。
    """

    completion = client.chat.completions.create(
        model="qwen-max",
        messages=[
            {
                'role': 'system',
                'content': new_prompt
            },
            {
                'role': 'user',
                'content': f"{name}对你说：{question}。\n当前上下文：\n{context}"
            }
        ]
    )
    response_content = completion.choices[0].message.content
    logger.info(f'LLM Response: {response_content}')
    return response_content


def llm_answer_delay_msg(question, content, client, prompt):
    # 将上下文整理为字符串
    context = "\n".join([f"{msg['type']}:{msg['message']}" for msg in content])

    # 构造提示词，明确表示消息是延迟队列中的任务，且需要提醒
    delay_msg_prompt = (
        f"这是一条来自延迟队列的消息。你回答的时候要说类似，已经到了xxx时间啦...，现在应该去xxx啦。这种的话，但是不要太生硬。"
        f"请生成一个友好且礼貌的提醒回复，提示对方有一个需要关注的任务：\n"
        f"任务详情：{question}\n"
        f"当前上下文：\n{context}"
    )

    completion = client.chat.completions.create(
        model="qwen-turbo",  # 使用你指定的模型
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
