import requests
import json
import logging

logger = logging.getLogger(__name__)


def send_message(qq, message, url):
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
    requests.post(url, data=json.dumps(data))
    logger.info(f"向 {qq} 发送消息：{message}")
