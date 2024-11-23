# Function Call 定义
function_definitions = [
    {
        "name": "add_delay_task",
        "description": "将任务添加到延迟队列。",
        "parameters": {
            "type": "object",
            "properties": {
                "delay_msg": {
                    "type": "string",
                    "description": "延迟任务的消息内容"
                },
                "delay_time": {
                    "type": "integer",
                    "description": "延迟时间，单位是秒"
                }
            },
            "required": ["delay_msg", "delay_time"]
        }
    }
]
