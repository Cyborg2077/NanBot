import json
import logging
import requests

from app.config import get_user_config
from app.dependencies import deps

logger = logging.getLogger(__name__)


def send_message(qq, msg, private=True):
    user_config = get_user_config(qq)
    if private:
        url = deps.config['oneBotApi']['send_private_msg']
        data_key = 'user_id'
    else:
        url = deps.config['oneBotApi']['send_group_msg']
        data_key = 'group_id'

    message_list = [msg.strip() for msg in msg.replace('\\n', '\n').strip().split('\n') if msg.strip()]
    for msg in message_list:
        data = {
            data_key: qq,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": msg
                    }
                }
            ]
        }
        requests.post(url, data=json.dumps(data))
        logger.info(f"向 {qq} 发送消息：{msg}")


def get_friend_msg_history(qq):
    user_config = get_user_config(qq)
    if not user_config:
        return
    url = deps.config['oneBotApi']['get_friend_msg_history']
    data = {'user_id': qq}
    response = requests.post(url, data=json.dumps(data))
    content = response.content.decode('utf-8')
    json_data = json.loads(content)
    logger.info(f'获取到和{qq}的聊天记录：{json_data}')
    return json_data
